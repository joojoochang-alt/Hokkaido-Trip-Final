import streamlit as st
import requests
import datetime
import json
import os
from PIL import Image

# --- 1. 設定頁面與 CSS (App-Like UI) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# 配色定義 (截圖取色)
COLORS = {
    'bg_main': '#F9F8F6',       # 背景
    'surface': '#FFFFFF',       # 卡片/未選中日期
    'text_primary': '#4A3B32',  # 深棕色主文字 (截圖風格)
    'text_secondary': '#9C8E7E',# 淺灰褐
    'accent_dark': '#3E3A36',   # 底部導覽列背景 / 選中日期背景
    'accent_gold': '#DEB887',   # 點綴金
    'line_light': '#E0DCD8',    # 線條
    'selected_text': '#FFFFFF', # 選中文字色
}

# 注入 CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Shippori+Mincho:wght@400;500;700&display=swap');

    /* 1. 全局設定 */
    :root {{
        --primary-color: {COLORS['accent_dark']};
        --background-color: {COLORS['bg_main']};
        --secondary-background-color: {COLORS['surface']};
        --text-color: {COLORS['text_primary']};
    }}

    .stApp {{
        background-color: {COLORS['bg_main']} !important;
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif;
        color: {COLORS['text_primary']} !important;
        padding-bottom: 100px; /* 為了避開底部導覽列 */
    }}
    
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {{
        color: {COLORS['text_primary']} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* -----------------------------------------
       ★ 底部固定導覽列 (Floating Bottom Bar) ★
       ----------------------------------------- */
    
    /* 定位容器 */
    .bottom-nav-container {{
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        width: 90%;
        max-width: 400px;
        background-color: {COLORS['accent_dark']};
        border-radius: 50px;
        padding: 10px 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        display: flex;
        justify-content: space-around;
        align-items: center;
    }}

    /* 為了讓 Streamlit 的按鈕能放進去，我們需要針對特定的 key 做 CSS Hack */
    /* 這裡我們會在 Python 端用特殊的容器包裝底部按鈕 */

    div[data-testid="stHorizontalBlock"][gap="large"] {{
        background-color: {COLORS['accent_dark']};
        border-radius: 40px;
        padding: 10px 15px;
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
        width: 90%;
        max-width: 380px;
        box-shadow: 0 8px 20px rgba(62, 58, 54, 0.3);
        justify-content: space-around !important;
    }}

    /* 底部按鈕樣式 */
    div[data-testid="stHorizontalBlock"][gap="large"] button {{
        background-color: transparent !important;
        border: none !important;
        color: #888 !important; /* 未選中顏色 */
        font-size: 1.5rem !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    
    /* 底部按鈕 - 選中/懸停 */
    div[data-testid="stHorizontalBlock"][gap="large"] button:hover,
    div[data-testid="stHorizontalBlock"][gap="large"] button:focus {{
        color: #FFFFFF !important; /* 選中變白 */
    }}
    
    /* -----------------------------------------
       ★ 日期選擇器 (In-Page Date Selector) ★
       ----------------------------------------- */
    
    /* 日期捲軸容器 */
    div[data-testid="stHorizontalBlock"][gap="medium"] {{
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        padding-bottom: 10px;
        gap: 10px !important;
        /* 隱藏捲軸 */
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none; 
    }}
    div[data-testid="stHorizontalBlock"][gap="medium"]::-webkit-scrollbar {{ 
        display: none; 
    }}

    /* 日期按鈕通用樣式 (方圓形) */
    div[data-testid="stHorizontalBlock"][gap="medium"] button {{
        border-radius: 16px !important; /* 方圓角 */
        width: 55px !important;
        height: 65px !important;
        min-width: 55px !important;
        padding: 5px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid #EEE !important;
        transition: all 0.2s ease;
        line-height: 1.2 !important;
    }}

    /* 日期按鈕 - 未選中 */
    div[data-testid="stHorizontalBlock"][gap="medium"] button[kind="secondary"] {{
        background-color: #FFFFFF !important;
        color: {COLORS['text_primary']} !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }}

    /* 日期按鈕 - 選中 (Primary) - 深色背景 */
    div[data-testid="stHorizontalBlock"][gap="medium"] button[kind="primary"] {{
        background-color: {COLORS['accent_dark']} !important;
        color: #FFFFFF !important;
        border: 1px solid {COLORS['accent_dark']} !important;
        box-shadow: 0 4px 12px rgba(62, 58, 54, 0.3) !important;
    }}
    /* 強制覆蓋內部文字顏色 */
    div[data-testid="stHorizontalBlock"][gap="medium"] button[kind="primary"] p {{
        color: #FFFFFF !important;
    }}


    /* -----------------------------------------
       通用元件樣式 (卡片、按鈕)
       ----------------------------------------- */

    /* 標題樣式 */
    .page-title {{
        font-family: 'Shippori Mincho', serif;
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 20px;
    }}

    /* 簡約卡片 */
    .minimal-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line_light']};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}

    /* 住宿卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLORS['line_light']} !important;
        border-radius: 16px !important;
        background-color: {COLORS['surface']} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}
    
    /* 一般功能按鈕 */
    .stButton button {{
        height: auto !important;
        padding: 8px 20px !important;
        background-color: #FFFFFF !important;
        border: 1px solid {COLORS['line_light']} !important;
        color: {COLORS['text_secondary']} !important;
        border-radius: 24px;
        font-weight: 500 !important;
    }}
    .stButton button:hover {{
        border-color: {COLORS['accent_gold']} !important;
        color: {COLORS['accent_gold']} !important;
    }}

    /* Google Map Link */
    a[href*="maps.google.com"] {{
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #FFFFFF !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['line_light']} !important;
        border-radius: 24px !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        width: 100%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }}

    /* Expander */
    div[data-testid="stExpander"] {{
        background-color: #FFFFFF !important;
        border: 1px solid {COLORS['line_light']} !important;
        color: {COLORS['text_primary']} !important;
        box-shadow: none !important;
        margin-top: 10px;
    }}
    div[data-testid="stExpander"] summary {{
        background-color: transparent !important;
        color: {COLORS['text_primary']} !important;
    }}
    div[data-testid="stExpander"] svg {{
        fill: {COLORS['text_secondary']} !important;
        color: {COLORS['text_secondary']} !important;
    }}

    /* Checkbox */
    div[data-testid="stCheckbox"] label span[data-baseweb="checkbox"] {{
        background-color: #FFFFFF !important;
        border-color: {COLORS['line_light']} !important;
    }}
    div[data-testid="stCheckbox"] label[aria-checked="true"] span[data-baseweb="checkbox"] {{
        background-color: {COLORS['accent_gold']} !important;
        border-color: {COLORS['accent_gold']} !important;
    }}

    /* Timeline */
    .timeline-point {{
        width: 9px;
        height: 9px;
        background-color: {COLORS['text_primary']};
        border-radius: 50%;
        margin-right: 12px;
        border: 2px solid {COLORS['bg_main']}; 
    }}
    .timeline-line {{
        position: absolute;
        left: 3px;
        top: 24px;
        bottom: -20px;
        width: 1px;
        background-color: {COLORS['line_light']};
    }}
    
    /* Delete Btn */
    .delete-btn button {{
        border: none !important;
        color: #E57373 !important;
        padding: 0px 8px !important;
        background: transparent !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 ---
# 初始化 Session State
if 'view_tab' not in st.session_state: st.session_state.view_tab = 'home' # home, itinerary, packing
if 'selected_day' not in st.session_state: st.session_state.selected_day = 0 # 0-4
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing_list' not in st.session_state:
    st.session_state.packing_list = [
        { "category": "Documents", "items": ["護照", "VJW QR", "機票截圖"] },
        { "category": "Clothing", "items": ["發熱衣", "防風外套", "毛帽"] },
        { "category": "Electronics", "items": ["網卡", "行動電源", "充電線"] }
    ]

APP_DATA = {
  "flight": { 
    "outbound": { "code": "TR892", "time": "12:30", "arrival": "17:20" }, 
    "inbound": { "code": "TR893", "time": "18:40", "arrival": "22:15" } 
  },
  "days": [
    { 
      "id": 0, "date": "08", "weekday": "MON", "full_date": "12/08 (一)", 
      "location": "Sapporo", "coords": { "lat": 43.0618, "lon": 141.3545 }, 
      "hotel": "JR-EAST METS", "hotel_note": "札幌站北口", 
      "activities": [
        { "time": "17:20", "text": "航班抵達 CTS", "type": "transport", "desc": "往 B1 搭 JR。", "guideText": "新千歲機場結構簡單...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=New+Chitose+Airport" },
        { "time": "19:45", "text": "飯店 Check-in", "type": "hotel", "desc": "JR-EAST METS", "guideText": "這間飯店最大優勢是...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=JR-EAST+HOTEL+METS+SAPPORO", "contact": "+81-11-729-0011" },
        { "time": "20:15", "text": "晚餐：湯咖哩", "type": "food", "desc": "Suage+ / GARAKU", "menu": ["知床雞野菜湯咖哩", "起司飯"], "notes": ["不可預約"], "guideText": "北海道靈魂美食...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Suage+Plus+Sapporo", "contact": "現場候位", "stayTime": "1.5 小時" },
        { "time": "22:30", "text": "夜間咖啡", "type": "food", "desc": "ESPRESSO D WORKS", "menu": ["巴斯克起司蛋糕"], "notes": ["營業至24:00"], "guideText": "札幌有「收尾聖代」文化...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=ESPRESSO+D+WORKS+Sapporo", "contact": "營業至 23:30", "stayTime": "1 小時" }
      ]
    },
    { 
      "id": 1, "date": "09", "weekday": "TUE", "full_date": "12/09 (二)", 
      "location": "Sapporo → Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "Ski-in Ski-out", 
      "activities": [
          { "time": "11:30", "text": "午餐：Uni Murakami", "type": "food", "desc": "海膽丼", "menu": ["生海膽丼"], "notes": ["建議訂位"], "guideText": "函館名店的分店...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Uni+Murakami+Sapporo", "contact": "011-290-1000", "stayTime": "1.5 小時" },
          { "time": "15:00", "text": "JR 移動", "type": "transport", "desc": "往俱知安", "guideText": "這段鐵路風景極美...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Sapporo+Station" },
          { "time": "18:00", "text": "Check-in", "type": "hotel", "desc": "Park Hyatt", "guideText": "二世谷頂級奢華代表...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Park+Hyatt+Niseko+Hanazono", "contact": "+81-136-27-1234" }
      ]
    },
    { 
      "id": 2, "date": "10", "weekday": "WED", "full_date": "12/10 (三)", 
      "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 2", 
      "activities": [
          { "time": "09:00", "text": "全日滑雪", "type": "activity", "desc": "粉雪天堂", "guideText": "Hanazono雪場對新手友善...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Hanazono+Resort" },
          { "time": "12:00", "text": "午餐：Hanazono EDGE", "type": "food", "desc": "雪場餐廳", "menu": ["蟹肉拉麵"], "notes": ["人潮眾多"], "guideText": "近年翻新的雪場餐廳...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Hanazono+EDGE", "contact": "無預約服務", "stayTime": "1 小時" },
          { "time": "18:00", "text": "Hirafu 晚餐", "type": "food", "desc": "居酒屋/燒肉", "menu": ["成吉思汗烤肉"], "notes": ["需提前預約"], "guideText": "Hirafu是二世谷最熱鬧的區域...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Hirafu+Niseko+Restaurants", "contact": "需查閱特定餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 3, "date": "11", "weekday": "THU", "full_date": "12/11 (四)", 
      "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 3", 
      "activities": [
          { "time": "13:00", "text": "午餐：手工蕎麥麵", "type": "food", "desc": "Ichimura", "menu": ["鴨肉蕎麥麵"], "notes": ["Cash Only"], "guideText": "使用二世谷清甜泉水...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Sobadokoro+Rakuichi", "contact": "0136-23-0603", "stayTime": "1 小時" },
          { "time": "18:00", "text": "晚餐：China Kitchen", "type": "food", "desc": "飯店內中餐", "menu": ["北京烤鴨"], "notes": ["Smart Casual"], "guideText": "玩累了不想出門...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=China+Kitchen+Park+Hyatt+Niseko", "contact": "內線直撥餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 4, "date": "12", "weekday": "FRI", "full_date": "12/12 (五)", 
      "location": "CTS Airport", "coords": {"lat": 42.7752, "lon": 141.6923}, 
      "hotel": "Home Sweet Home", "hotel_note": "機場日", 
      "activities": [
          { "time": "09:20", "text": "巴士出發", "type": "transport", "desc": "前往機場", "guideText": "從二世谷搭巴士直達機場...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Welcome+Center" },
          { "time": "13:00", "text": "拉麵道場", "type": "food", "desc": "一幻 / 白樺山莊", "menu": ["鮮蝦鹽味拉麵"], "notes": ["行李需寄放"], "guideText": "機場國內線3樓的拉麵一級戰區...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Hokkaido+Ramen+Dojo", "contact": "機場國內線 3F", "stayTime": "1 小時" },
          { "time": "14:30", "text": "甜點 & 伴手禮巡禮", "type": "food", "desc": "國內線 2F 掃貨", "menu": ["北菓樓 夢不思議泡芙"], "notes": ["保冷袋必備"], "guideText": "新千歲機場國內線2F是伴手禮一級戰區！", "mapUrl": "https://www.google.com/maps/search/?api=1&query=New+Chitose+Airport+Domestic+Terminal+2F", "contact": "國內線 2F", "stayTime": "2.5 小時" },
          { "time": "18:40", "text": "TR893 起飛", "type": "transport", "desc": "返台", "guideText": "酷航櫃台通常在起飛前3小時...", "mapUrl": "https://www.google.com/maps/search/?api=1&query=New+Chitose+Airport+International+Terminal" }
      ]
    }
  ]
}

# --- 3. 核心功能函式 ---
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=Asia%2FTokyo"
        res = requests.get(url, timeout=2).json()
        if 'current' in res:
            temp = res['current']['temperature_2m']
            code = res['current']['weather_code']
            w_text = "陰"
            if code == 0: w_text = "晴"
            elif code in [1,2,3]: w_text = "多雲"
            elif code in [61,63,65,80,81,82]: w_text = "雨"
            elif code in [71,73,75,85,86]: w_text = "雪"
            return temp, w_text
        return None, None
    except:
        return -2, "雪(預測)"

def get_exchange_rate():
    try:
        url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.json"
        res = requests.get(url, timeout=2).json()
        rate = res['jpy']['twd']
        return rate
    except:
        return 0.215

# --- 4. 票券視窗 ---
@st.dialog("Digital Voucher")
def ticket_modal(ticket_key, title):
    default_ticket = {"orderNumber": "", "url": "", "note": "", "image": None}
    existing = st.session_state.tickets.get(ticket_key, default_ticket)
    
    if 'is_editing' not in st.session_state:
        st.session_state.is_editing = not (existing.get("orderNumber") or existing.get("url"))

    if not st.session_state.is_editing:
        st.markdown(f"""
        <div class="wallet-pass">
            <div class="pass-header">
                <div style="font-size: 10px; font-weight: bold; color: {COLORS['text_secondary']}; letter-spacing: 1px;">RESERVATION</div>
                <div style="font-size: 20px; font-weight: 500; color: {COLORS['text_primary']}; margin-top:4px; font-family: 'Shippori Mincho', serif;">{title}</div>  
                <div style="font-size: 12px; color: {COLORS['text_secondary']}; margin-top: 6px;">{existing.get('note', '')}</div>
                <div style="margin-top: 30px;">
                    <div style="font-size: 10px; font-weight: bold; color: {COLORS['text_secondary']}; letter-spacing: 1px;">CONFIRMATION NO.</div>
                    <div style="font-size: 22px; font-weight: 500; font-family: monospace; color: {COLORS['text_primary']}; letter-spacing: 1px;">{existing.get('orderNumber', '—')}</div>
                </div>
            </div>
            <div class="pass-notch-container">
                <div class="pass-notch-left"></div>
                <div class="pass-dashed-line"></div>
                <div class="pass-notch-right"></div>
            </div>
            <div style="padding: 20px; text-align: center; background: #FAFAFA;">
                <div style="display: inline-flex; align-items: center; gap: 6px; color: #6B8E23; font-weight: 500; font-size: 0.9rem;">
                    <span>✅</span> <span>Ready to Use</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if existing.get('image'):
            st.image(existing['image'], caption="E-Ticket", use_container_width=True)
        if existing.get('url'): st.link_button("🔗 OPEN LINK", existing['url'], use_container_width=True)
        if st.button("Edit Voucher", key="edit_btn", use_container_width=True):
            st.session_state.is_editing = True
            st.rerun()
    else:
        st.markdown("### Edit Details")
        new_order = st.text_input("Confirmation No.", value=existing.get("orderNumber", ""))
        new_url = st.text_input("Link URL", value=existing.get("url", ""))
        new_note = st.text_area("Notes", value=existing.get("note", ""))
        new_image = st.file_uploader("Upload Ticket Image", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Save Changes", type="primary", use_container_width=True):
            final_image = new_image if new_image else existing.get('image')
            st.session_state.tickets[ticket_key] = {"orderNumber": new_order, "url": new_url, "note": new_note, "image": final_image}
            st.session_state.is_editing = False
            st.rerun()

# --- 5. 頁面元件與邏輯 ---

def render_home_page():
    # Home Header
    st.markdown(f"""
    <div style='text-align:center; padding: 40px 0 20px;'>
        <h1 style='font-family: "Shippori Mincho", serif; font-size: 2.5rem; margin-bottom: 8px; letter-spacing: 1px; font-weight: 500;'>Hokkaido</h1>
        <p style='color:{COLORS['text_secondary']}; letter-spacing: 0.3em; font-size: 0.8rem; font-weight: 400;'>DECEMBER 2025</p>
        <div style="width: 60px; height: 1px; background-color: {COLORS['line_light']}; margin: 20px auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # VJW
    vjw_url = "https://vjw-lp.digital.go.jp/en/"
    st.markdown(f"""<a href="{vjw_url}" target="_blank" style="text-decoration:none;"><div class="minimal-card" style="display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:20px;">✈️</span>
            <div><div style="font-size:16px; font-weight:500; color:{COLORS['text_primary']};">Visit Japan Web</div><div style="font-size:12px; color:{COLORS['text_secondary']};">入境日本必須申請</div></div>
        </div>
        <div style="color:{COLORS['text_secondary']};">→</div>
    </div></a>""", unsafe_allow_html=True)

    # Info Grid
    rate = get_exchange_rate()
    temp1, weather1 = get_weather(43.06, 141.35)
    temp2, weather2 = get_weather(42.80, 140.68)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background:{COLORS['surface']}; border-radius:16px; padding:15px; border:1px solid {COLORS['line_light']}; height:100%;">
            <div style="font-size:0.7rem; font-weight:700; color:{COLORS['text_secondary']}; margin-bottom:6px;">EXCHANGE</div>
            <div style="font-family:'Shippori Mincho', serif; font-size:1.6rem; font-weight:600;">{rate:.4f}</div>
            <div style="font-size:0.7rem; color:{COLORS['text_secondary']};">JPY / TWD</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:{COLORS['surface']}; border-radius:16px; padding:15px; border:1px solid {COLORS['line_light']}; height:100%;">
            <div style="font-size:0.7rem; font-weight:700; color:{COLORS['text_secondary']}; margin-bottom:6px;">WEATHER</div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;"><span>Sapporo</span><strong>{temp1}°</strong></div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem;"><span>Niseko</span><strong>{temp2}°</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")

    # Flights
    st.markdown(f'<div class="minimal-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1rem; margin-bottom:1rem; font-weight: 500; border-bottom: 1px solid {COLORS['line_light']}; padding-bottom: 8px;'>✈️ 航班</h3>", unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:0.8rem; color:{COLORS['text_secondary']};'>DEC 08 (OUT)</div><div style='font-size:1.4rem; font-weight:500; font-family:\"Shippori Mincho\", serif;'>{APP_DATA['flight']['outbound']['time']}</div><div style='font-size:0.8rem; color:{COLORS['text_secondary']};'>↓</div><div style='font-size:1.4rem; font-weight:500; font-family:\"Shippori Mincho\", serif;'>{APP_DATA['flight']['outbound']['arrival']}</div><div style='font-size:0.9rem; font-weight:bold; margin-top:4px;'>{APP_DATA['flight']['outbound']['code']}</div></div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Ticket", key="fw_w", use_container_width=True): ticket_modal("flight_wei", "Flight Out")
    with f2:
        st.markdown(f"<div style='text-align:center; border-left:1px solid {COLORS['line_light']};'><div style='font-size:0.8rem; color:{COLORS['text_secondary']};'>DEC 12 (IN)</div><div style='font-size:1.4rem; font-weight:500; font-family:\"Shippori Mincho\", serif;'>{APP_DATA['flight']['inbound']['time']}</div><div style='font-size:0.8rem; color:{COLORS['text_secondary']};'>↓</div><div style='font-size:1.4rem; font-weight:500; font-family:\"Shippori Mincho\", serif;'>{APP_DATA['flight']['inbound']['arrival']}</div><div style='font-size:0.9rem; font-weight:bold; margin-top:4px;'>{APP_DATA['flight']['inbound']['code']}</div></div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Ticket", key="fi_c", use_container_width=True): ticket_modal("flight_chien", "Flight In")
    st.markdown('</div>', unsafe_allow_html=True)

    # Emergency
    st.markdown(f"""
    <div class="minimal-card" style="margin-top: 20px;">
        <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS['alert_red']}; letter-spacing: 0.1em; margin-bottom: 10px; border-bottom: 1px solid {COLORS['line_light']}; padding-bottom: 5px;">緊急求助 / EMERGENCY</div>
        <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
             <div style="text-align: center;"><div style="font-size: 1.4rem; font-weight: 500;">110</div><div style="font-size: 0.7rem; color: {COLORS['text_secondary']};">報警</div></div>
             <div style="text-align: center;"><div style="font-size: 1.4rem; font-weight: 500;">119</div><div style="font-size: 0.7rem; color: {COLORS['text_secondary']};">救護</div></div>
        </div>
        <div style="background: #F9F9F9; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid {COLORS['line_light']};">
             <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">札幌辦事處</div>
             <div style="font-size: 1.1rem; font-weight: 500;">080-1460-2568</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_itinerary_page():
    # Itinerary Title
    st.markdown(f"""<div class="page-title">行程表</div>""", unsafe_allow_html=True)
    
    # ★ Date Horizontal Scroll ★ (In-Page Navigation)
    # 使用 gap="medium" 來與底部導覽列的 CSS 區隔
    with st.container():
        cols = st.columns(5, gap="medium")
        for i, day in enumerate(APP_DATA['days']):
            with cols[i]:
                # 判斷此日期是否被選中
                is_selected = (st.session_state.selected_day == i)
                # 顯示日期方塊
                if st.button(f"{day['date']}\n{day['weekday']}", key=f"date_sel_{i}", type="primary" if is_selected else "secondary"):
                    st.session_state.selected_day = i
                    st.rerun()
    
    st.write("") # Spacer

    # Display Selected Day Content
    day_idx = st.session_state.selected_day
    day = APP_DATA['days'][day_idx]
    
    # Day Header
    st.markdown(f"""
    <div style="text-align:center; margin: 10px 0 20px 0;">
        <div style="font-size: 1.5rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 5px;">{day['full_date']}</div>
        <div style="font-size: 0.9rem; color: {COLORS['text_secondary']}; display:flex; align-items:center; justify-content:center; gap:6px;">
            <span>📍</span> {day['location']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hotel
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div style="font-size:0.7rem; font-weight:600; color:{COLORS['text_secondary']}; letter-spacing:0.1em; margin-bottom:6px;">ACCOMMODATION</div>
                <div style="font-weight:500; font-size:1.2rem; margin-bottom:4px; font-family:'Shippori Mincho', serif;">{day['hotel']}</div>
                <div style="font-size:0.85rem; color:{COLORS['text_secondary']};">{day['hotel_note']}</div>
            </div>
            <div style="font-size:1.8rem; color:{COLORS['line_light']};">🛏️</div>
        </div>
        <div style="border-top: 1px dashed {COLORS['line_light']}; margin: 16px 0 12px 0;"></div>
        """, unsafe_allow_html=True)
        if st.button("Booking Info", key=f"h_btn_{day_idx}", use_container_width=True):
            ticket_modal(f"hotel_{day_idx}", f"Hotel: {day['hotel']}")

    st.write("")

    # Timeline Activities
    for i, act in enumerate(day['activities']):
        st.markdown(f"""
        <div style="position: relative; padding-left: 24px; margin-bottom: 1.5rem;">
            <div class="timeline-point" style="position: absolute; left: 0; top: 6px;"></div>
            {'<div class="timeline-line"></div>' if i < len(day['activities']) - 1 else ''}
            <div style="font-family:'Shippori Mincho', serif; font-size:0.9rem; font-weight:600; color:{COLORS['text_primary']}; margin-bottom: 8px;">{act['time']}</div>
            <div class="minimal-card" style="display:flex; justify-content:space-between; align-items:center; padding: 1.2rem;">
                <div>
                    <div style="font-weight:500; font-size:1.1rem; color:{COLORS['text_primary']}; font-family: 'Shippori Mincho', serif; margin-bottom: 4px;">{act['text']}</div>
                    <div style="font-size:0.85rem; color:{COLORS['text_secondary']};">{act['desc']}</div>
                </div>
                <div style="font-size:1.5rem; color:{COLORS['line_light']};">{'🍴' if act['type'] == 'food' else '🚆' if act['type'] == 'transport' else '📍'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("查看詳情"):
            if 'guideText' in act:
                st.markdown(f"<p style='font-size:0.9rem; color:{COLORS['text_primary']};'>{act['guideText']}</p>", unsafe_allow_html=True)
            if act['type'] == 'food' and 'menu' in act:
                st.markdown(f"""
                <div style="background:#FFF; border:1px solid {COLORS['line_light']}; padding:12px; border-radius:8px; margin-top:10px;">
                    <div style="font-size:0.7rem; color:{COLORS['accent_warm']}; font-weight:600; margin-bottom:5px;">RECOMMENDED</div>
                    <ul style="margin:0; padding-left:20px; font-size:0.9rem;">{''.join([f'<li>{m}</li>' for m in act['menu']])}</ul>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
            if 'mapUrl' in act:
                st.markdown(f'<a href="{act["mapUrl"]}" target="_blank" style="display:flex; align-items:center; justify-content:center; background-color:#FFFFFF; color:{COLORS["text_primary"]}; border:1px solid {COLORS["line_light"]}; border-radius:24px; padding:0.5rem 1rem; text-decoration:none; font-weight:500; width:100%; box-shadow:0 1px 2px rgba(0,0,0,0.05); margin-bottom:10px;">📍 Google Map</a>', unsafe_allow_html=True)
            
            # Buttons
            if act['type'] == 'transport':
                c1, c2 = st.columns(2)
                if c1.button("Ticket (W)", key=f"t_{day_idx}_{i}_w"): ticket_modal(f"t_{day_idx}_{i}_w", "Ticket W")
                if c2.button("Ticket (C)", key=f"t_{day_idx}_{i}_c"): ticket_modal(f"t_{day_idx}_{i}_c", "Ticket C")


def render_packing_page():
    st.markdown(f"""<div class="page-title" style="text-align:center;">Packing List</div>""", unsafe_allow_html=True)
    
    total = sum(len(cat['items']) for cat in st.session_state.packing_list)
    checked = sum(1 for k, v in st.session_state.packing.items() if v)
    st.markdown(f"""<style>.stProgress > div > div > div > div {{ background-color: {COLORS['accent_gold']}; }}</style>""", unsafe_allow_html=True)
    st.progress(checked / total if total > 0 else 0)
    st.write("")

    for i, cat in enumerate(st.session_state.packing_list[:]):
        with st.container(border=True):
            c1, c2 = st.columns([8,1])
            c1.markdown(f"**{cat['category']}**")
            if c2.button("🗑️", key=f"del_cat_{i}"):
                st.session_state.packing_list.pop(i)
                st.rerun()
            
            st.markdown(f"<div style='border-bottom:1px solid {COLORS['line_light']}; margin-bottom:10px;'></div>", unsafe_allow_html=True)
            
            for j, item in enumerate(cat['items']):
                rc1, rc2 = st.columns([6,1])
                with rc1:
                    key = f"pack_{item}"
                    st.session_state.packing[key] = st.checkbox(item, value=st.session_state.packing.get(key, False), key=key)
                with rc2:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("✕", key=f"del_item_{i}_{j}"):
                        st.session_state.packing_list[i]['items'].pop(j)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2, c3 = st.columns([2,3,1])
    new_cat = c1.text_input("Cat", placeholder="Category", label_visibility="collapsed")
    new_item = c2.text_input("Item", placeholder="Item Name", label_visibility="collapsed")
    if c3.button("Add", use_container_width=True):
        if new_item:
            target = new_cat if new_cat else "Personal"
            found = next((c for c in st.session_state.packing_list if c['category'] == target), None)
            if found: found['items'].append(new_item)
            else: st.session_state.packing_list.append({"category": target, "items": [new_item]})
            st.rerun()


# --- 7. 主程式邏輯 (Main Logic) ---

# 根據當前 tab 渲染內容
if st.session_state.view_tab == 'home':
    render_home_page()
elif st.session_state.view_tab == 'itinerary':
    render_itinerary_page()
elif st.session_state.view_tab == 'packing':
    render_packing_page()

# --- 8. 底部導覽列 (放在最後，使用 columns 模擬) ---
# 使用 gap="large" 作為 CSS 選擇器來抓取這個特定的區塊
st.write("")
st.write("")
st.write("")

# 底部導覽列容器
bottom_nav = st.columns(3, gap="large")

with bottom_nav[0]:
    if st.button("🏠", key="btm_home", type="primary" if st.session_state.view_tab == 'home' else "secondary"):
        st.session_state.view_tab = 'home'
        st.rerun()

with bottom_nav[1]:
    if st.button("📅", key="btm_cal", type="primary" if st.session_state.view_tab == 'itinerary' else "secondary"):
        st.session_state.view_tab = 'itinerary'
        st.rerun()

with bottom_nav[2]:
    if st.button("🎒", key="btm_pack", type="primary" if st.session_state.view_tab == 'packing' else "secondary"):
        st.session_state.view_tab = 'packing'
        st.rerun()
