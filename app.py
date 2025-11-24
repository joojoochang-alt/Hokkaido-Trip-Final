import streamlit as st
import pandas as pd
import requests
import datetime

# --- 1. 頁面設定與無印風 CSS ---
st.set_page_config(page_title="Hokkaido Trip 2025", page_icon="❄️", layout="centered")

# 定義配色 (Muji Style)
COLORS = {
    'bg': '#F9F8F6',       # 生成色
    'card': '#FFFFFF',     # 純白
    'text': '#464646',     # 深灰
    'sub_text': '#7F7268', # 亞麻灰
    'accent': '#8E8071',   # 栗色/亞麻色
    'line': '#E6E2DE',     # 淺灰褐
    'red': '#B94047'       # 傳統紅 (重點標示用)
}

# 注入 CSS
st.markdown(f"""
    <style>
    /* 全局字體與背景 */
    .stApp {{
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
    }}
    
    /* 隱藏預設選單 */
    #MainMenu, footer {{visibility: hidden;}}

    /* 卡片風格 */
    .muji-card {{
        background-color: {COLORS['card']};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        border: 1px solid {COLORS['line']};
    }}

    /* 標題優化 */
    h1, h2, h3 {{
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'STHeiti', sans-serif; 
        font-weight: 600;
        color: {COLORS['text']};
    }}
    
    /* 時間軸樣式 */
    .time-tag {{
        background-color: {COLORS['line']};
        color: {COLORS['text']};
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-family: monospace;
        font-weight: bold;
    }}
    
    /* 按鈕樣式微調 */
    .stButton button {{
        border-radius: 20px;
        border: 1px solid {COLORS['line']};
        background-color: white;
        color: {COLORS['sub_text']};
        transition: all 0.3s;
    }}
    .stButton button:hover {{
        border-color: {COLORS['accent']};
        color: {COLORS['accent']};
        background-color: {COLORS['bg']};
    }}
    
    /* Expander 樣式 */
    .streamlit-expanderHeader {{
        font-size: 0.9rem;
        color: {COLORS['sub_text']};
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料準備 (模擬 Pandas DataFrame) ---

# 行程資料 (從 React constants.ts 轉換)
ITINERARY_DATA = {
    "12/08 (一)": {
        "location": "Sapporo",
        "coords": {"lat": 43.06, "lon": 141.35},
        "hotel": "JR-EAST METS Sapporo",
        "activities": [
            {"time": "17:20", "text": "航班抵達 CTS", "type": "transport", "desc": "前往 B1 搭乘 JR", "tickets": True, "map": "https://goo.gl/maps/NewChitoseAirport"},
            {"time": "19:45", "text": "飯店 Check-in", "type": "hotel", "desc": "JR-EAST METS (北口直結)", "map": "https://maps.app.goo.gl/SapporoStationNorth"},
            {"time": "20:15", "text": "晚餐：湯咖哩 Suage+", "type": "food", "desc": "北海道必吃湯咖哩", "menu": ["知床雞野菜湯咖哩", "起司飯", "炸舞菇"], "info": "不可預約 / 現場排隊約30分", "map": "https://maps.app.goo.gl/SuagePlus"},
            {"time": "22:30", "text": "夜間咖啡", "type": "food", "desc": "ESPRESSO D WORKS", "menu": ["巴斯克起司蛋糕", "熱拿鐵"], "info": "營業至 23:30", "map": "https://maps.app.goo.gl/EspressoDWorks"}
        ]
    },
    "12/09 (二)": {
        "location": "Sapporo → Niseko",
        "coords": {"lat": 42.80, "lon": 140.68},
        "hotel": "Park Hyatt Niseko",
        "activities": [
            {"time": "11:30", "text": "午餐：Uni Murakami", "type": "food", "desc": "函館海膽名店", "menu": ["無添加生海膽丼", "海膽天婦羅"], "info": "建議提前訂位 / 價格較高", "map": "https://maps.app.goo.gl/UniMurakamiSapporo"},
            {"time": "15:00", "text": "JR 移動", "type": "transport", "desc": "前往俱知安 (Kutchan)", "tickets": True, "map": "https://maps.app.goo.gl/KutchanStation"},
            {"time": "18:00", "text": "Check-in", "type": "hotel", "desc": "Park Hyatt Niseko", "map": "https://maps.app.goo.gl/ParkHyattNiseko"}
        ]
    },
    "12/10 (三)": {
        "location": "Niseko",
        "coords": {"lat": 42.80, "lon": 140.68},
        "hotel": "Park Hyatt Niseko",
        "activities": [
            {"time": "09:00", "text": "全日滑雪", "type": "activity", "desc": "Hanazono 粉雪天堂", "map": "https://maps.app.goo.gl/HanazonoResort"},
            {"time": "12:00", "text": "午餐：Hanazono EDGE", "type": "food", "desc": "雪場餐廳", "menu": ["蟹肉拉麵", "炸豬排咖哩"], "info": "人潮眾多建議 11:30 前抵達", "map": "https://maps.app.goo.gl/HanazonoEDGE"},
            {"time": "18:00", "text": "晚餐：Hirafu 居酒屋", "type": "food", "desc": "成吉思汗烤肉", "menu": ["生羊肉燒烤", "北海道生啤酒"], "info": "需預約 / 搭飯店接駁車", "map": "https://maps.app.goo.gl/HirafuVillage"}
        ]
    },
    "12/11 (四)": {
        "location": "Niseko",
        "coords": {"lat": 42.80, "lon": 140.68},
        "hotel": "Park Hyatt Niseko",
        "activities": [
            {"time": "13:00", "text": "午餐：手打蕎麥麵", "type": "food", "desc": "Ichimura", "menu": ["鴨肉蕎麥麵", "天婦羅"], "info": "Cash Only / 賣完為止", "map": "https://maps.app.goo.gl/NisekoIchimura"},
            {"time": "18:00", "text": "晚餐：China Kitchen", "type": "food", "desc": "飯店內中餐廳", "menu": ["北京烤鴨", "四川擔擔麵"], "info": "Smart Casual / 房客優先", "map": "https://maps.app.goo.gl/ParkHyattChinaKitchen"}
        ]
    },
    "12/12 (五)": {
        "location": "CTS Airport",
        "coords": {"lat": 42.77, "lon": 141.69},
        "hotel": "溫暖的家",
        "activities": [
            {"time": "09:20", "text": "巴士出發", "type": "transport", "desc": "前往新千歲機場", "tickets": True, "map": "https://maps.app.goo.gl/HirafuBusStop"},
            {"time": "13:00", "text": "午餐：拉麵道場", "type": "food", "desc": "一幻 / 白樺山莊", "menu": ["鮮蝦鹽味拉麵", "味噌拉麵"], "info": "行李需寄放 / 排隊約20分", "map": "https://maps.app.goo.gl/CTSRamenDojo"},
            {"time": "14:30", "text": "機場採買", "type": "activity", "desc": "國內線 2F 伴手禮巡禮", "map": "https://www.new-chitose-airport.jp/tw/floor/2f.html"},
            {"time": "18:40", "text": "TR893 起飛", "type": "transport", "desc": "返台", "tickets": True, "map": "https://maps.app.goo.gl/NewChitoseIntl"}
        ]
    }
}

# 購物/預算清單 (初始化 Session State)
if 'shopping_df' not in st.session_state:
    data = {
        "商品名稱": ["北菓樓泡芙", "六花亭夾心", "LeTAO蛋糕", "薯條三兄弟", "白色戀人", "藥妝"],
        "類別": ["甜點", "甜點", "甜點", "零食", "零食", "雜貨"],
        "預算 (JPY)": [1500, 3000, 2000, 5000, 1500, 10000],
        "已購買": [False, False, False, False, False, False],
        "實際花費 (JPY)": [0, 0, 0, 0, 0, 0]
    }
    st.session_state.shopping_df = pd.DataFrame(data)

# --- 3. 輔助函式 ---

@st.cache_data(ttl=3600)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=Asia%2FTokyo"
        res = requests.get(url, timeout=2).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        # 簡易天氣判斷
        desc = "晴"
        if code in [1, 2, 3]: desc = "多雲"
        elif code in [61, 63, 65, 80, 81, 82]: desc = "雨"
        elif code in [71, 73, 75, 85, 86]: desc = "雪"
        return temp, desc
    except:
        return None, None

@st.dialog("Digital Ticket")
def show_ticket(title, type_label):
    st.markdown(f"### {title}")
    st.info(f"這是 {type_label} 的電子票券憑證")
    st.markdown("---")
    st.markdown("**訂單編號**: `HOK-2025-8888`")
    st.markdown("**乘客**: W & C")
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150, caption="請出示此 QR Code")
    if st.button("關閉"):
        st.rerun()

# --- 4. 主程式介面 ---

# 側邊欄：日期選擇
with st.sidebar:
    st.title("📅 行程日期")
    selected_date = st.radio(
        "選擇日期",
        list(ITINERARY_DATA.keys()),
        index=0
    )
    st.markdown("---")
    st.caption("Designed for Hokkaido Trip 2025")

# 主分頁
tab1, tab2, tab3 = st.tabs(["📍 每日行程", "🛍️ 購物清單", "💰 預算統計"])

# --- Tab 1: 每日行程 ---
with tab1:
    day_data = ITINERARY_DATA[selected_date]
    
    # 標題區
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h1 style='margin-bottom:0;'>{selected_date.split(' ')[0]}</h1><p style='color:{COLORS['sub_text']};'>{day_data['location']}</p></div>", unsafe_allow_html=True)
    
    # 天氣與飯店
    temp, weather_desc = get_weather(day_data['coords']['lat'], day_data['coords']['lon'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="muji-card" style="text-align:center; padding:15px;">
            <div style="font-size:0.8rem; color:{COLORS['sub_text']};">WEATHER</div>
            <div style="font-size:1.5rem; font-weight:bold;">{temp}°C {weather_desc}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="muji-card" style="text-align:center; padding:15px;">
            <div style="font-size:0.8rem; color:{COLORS['sub_text']};">HOTEL</div>
            <div style="font-size:1.1rem; font-weight:bold;">{day_data['hotel']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 行程列表
    st.markdown("### Itinerary")
    
    for i, act in enumerate(day_data['activities']):
        # 外層容器 (模擬卡片)
        with st.container():
            st.markdown(f"""
            <div class="muji-card">
                <div style="display:flex; align-items:center; margin-bottom:8px;">
                    <span class="time-tag">{act['time']}</span>
                    <span style="margin-left:10px; font-weight:bold; font-size:1.1rem;">{act['text']}</span>
                </div>
                <div style="color:{COLORS['sub_text']}; font-size:0.9rem; margin-bottom:10px;">{act['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 功能按鈕區 (使用 columns 來對齊)
            c1, c2, c3 = st.columns([1, 1, 2])
            
            # 1. 票券按鈕 (Transport)
            if act.get('type') == 'transport' and act.get('tickets'):
                with c1:
                    if st.button("🎫 車票 (W)", key=f"t_w_{selected_date}_{i}"):
                        show_ticket(act['text'], "W")
                with c2:
                    if st.button("🎫 車票 (C)", key=f"t_c_{selected_date}_{i}"):
                        show_ticket(act['text'], "C")
            
            # 2. 餐廳隱藏菜單 (Food)
            if act.get('type') == 'food':
                with st.expander("🍽️ 推薦菜單與資訊"):
                    st.markdown(f"**推薦菜單**: {', '.join(act.get('menu', []))}")
                    st.markdown(f"**貼心提醒**: {act.get('info', '')}")
            
            # 3. 地圖按鈕 (Map)
            if act.get('map'):
                st.link_button("📍 Google Map 導航", act['map'])
            
            st.write("") # 間距

# --- Tab 2: 購物清單 (Pandas 互動) ---
with tab2:
    st.title("🛍️ Shopping List")
    st.caption("勾選「已購買」並填入實際金額，系統會自動統計。")
    
    # 使用 Data Editor 讓使用者編輯 DataFrame
    edited_df = st.data_editor(
        st.session_state.shopping_df,
        column_config={
            "已購買": st.column_config.CheckboxColumn(
                "Status",
                help="是否已購買",
                default=False,
            ),
            "預算 (JPY)": st.column_config.NumberColumn(
                "預算 (¥)",
                format="¥%d",
            ),
            "實際花費 (JPY)": st.column_config.NumberColumn(
                "實際花費 (¥)",
                format="¥%d",
                help="請輸入實際購買金額"
            )
        },
        disabled=["商品名稱", "類別"], # 禁止修改名稱，只能改狀態和金額
        hide_index=True,
        use_container_width=True
    )
    
    # 更新 Session State
    st.session_state.shopping_df = edited_df

# --- Tab 3: 預算統計 ---
with tab3:
    st.title("💰 Budget Analysis")
    
    df = st.session_state.shopping_df
    
    # 計算邏輯
    total_budget = df["預算 (JPY)"].sum()
    
    # 只計算「已購買」項目的實際花費
    spent_df = df[df["已購買"] == True]
    total_spent = spent_df["實際花費 (JPY)"].sum()
    
    # 預算剩餘 (總預算 - 實際花費)
    remaining = total_budget - total_spent
    
    # 顯示指標
    col1, col2, col3 = st.columns(3)
    col1.metric("總預算", f"¥{total_budget:,}")
    col2.metric("目前花費", f"¥{total_spent:,}", delta=f"-{total_spent/total_budget:.1%}" if total_budget > 0 else 0)
    col3.metric("剩餘預算", f"¥{remaining:,}", delta_color="normal" if remaining >= 0 else "inverse")
    
    st.markdown("---")
    
    # 進度條
    if total_budget > 0:
        progress = min(total_spent / total_budget, 1.0)
        st.progress(progress, text=f"預算使用率: {progress:.1%}")
        if progress > 1.0:
            st.error("⚠️ 警告：已超出預算！")
    
    # 類別統計圖表
    st.subheader("各類別預算佔比")
    category_chart = df.groupby("類別")["預算 (JPY)"].sum()
    st.bar_chart(category_chart, color=COLORS['accent'])
