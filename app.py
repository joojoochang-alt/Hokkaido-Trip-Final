import streamlit as st
import requests
import datetime
import google.generativeai as genai
import json
import os

# --- 1. 設定頁面與 CSS (Muji Minimalist Style) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# Muji 風格配色與樣式定義
COLORS = {
    'bg_main': '#F8F7F3',       # 極淺米色背景
    'surface': '#FFFFFF',       # 純白卡片
    'text_primary': '#5B5551',  # 深棕灰主文字
    'text_secondary': '#A09B96',# 淺灰輔助文字
    'accent_warm': '#C7B299',   # 燕麥色
    'accent_deep': '#8C8376',   # 深卡其 (補回此缺少的顏色)
    'accent_light': '#EBE9E5',  # 淺米白 (按鈕反白用)
    'line_light': '#EAE8E4',    # 極細淺灰線
    'alert_red': '#B94047',     # 警示紅
}

# 注入 CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;500;700&family=Shippori+Mincho:wght@400;500;600&display=swap');

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg_main']};
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif;
        color: {COLORS['text_primary']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif !important;
        font-weight: 500 !important;
        color: {COLORS['text_primary']} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* 簡約日式卡片 */
    .minimal-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line_light']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }}
    
    /* 按鈕樣式調整 */
    .stButton button {{
        background-color: transparent;
        border: 1px solid {COLORS['line_light']} !important;
        color: {COLORS['text_secondary']};
        border-radius: 20px;
        padding: 6px 16px;
        font-weight: 400;
        box-shadow: none;
        transition: all 0.2s ease;
        font-family: 'Shippori Mincho', serif;
    }}
    /* Hover 狀態 */
    .stButton button:hover {{
        background-color: {COLORS['accent_light']} !important;
        color: {COLORS['text_primary']} !important;
        border-color: {COLORS['line_light']} !important;
    }}
    /* 選中/Primary 狀態 */
    .stButton button[kind="primary"] {{
        background-color: {COLORS['accent_light']} !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['accent_warm']} !important;
        font-weight: 600;
    }}

    /* 天氣與匯率區塊 */
    .info-grid-minimal {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .info-box-minimal {{
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid {COLORS['line_light']};
    }}
    .info-label-minimal {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }}
    .info-value-minimal {{
        font-family: 'Shippori Mincho', serif;
        font-size: 1.6rem;
        font-weight: 500;
        color: {COLORS['text_primary']};
        line-height: 1.1;
    }}

    /* Expander 優化 */
    div[data-testid="stExpander"] {{
        background-color: transparent;
        border: none;
        box-shadow: none;
    }}
    div[data-testid="stExpander"] summary {{
        color: {COLORS['text_primary']};
    }}
    
    /* Ticket Style */
    .wallet-pass {{
        background-color: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {COLORS['line_light']};
        font-family: 'Shippori Mincho', serif;
        margin-bottom: 20px;
    }}
    .pass-header {{
        padding: 24px;
        background: #F8F7F3;
    }}
    .pass-notch-container {{
        height: 20px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #FFFFFF;
    }}
    .pass-notch-left, .pass-notch-right {{
        width: 20px;
        height: 20px;
        background-color: {COLORS['bg_main']};
        border-radius: 50%;
        position: absolute;
        top: 0;
        z-index: 10;
        border: 1px solid {COLORS['line_light']};
    }}
    .pass-notch-left {{ left: -10px; border-right: none; }}
    .pass-notch-right {{ right: -10px; border-left: none; }}
    .pass-dashed-line {{
        width: 90%;
        border-top: 1px dashed {COLORS['line_light']};
    }}

    /* 時間軸樣式 */
    .timeline-point {{
        width: 8px;
        height: 8px;
        background-color: {COLORS['accent_warm']};
        border-radius: 50%;
        margin-right: 12px;
    }}
    .timeline-line {{
        position: absolute;
        left: 3px;
        top: 24px;
        bottom: -20px;
        width: 1px;
        background-color: {COLORS['line_light']};
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 ---
if 'view' not in st.session_state: st.session_state.view = 'overview'
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing' not in st.session_state: st.session_state.packing = {}
if 'chat_history' not in st.session_state: st
