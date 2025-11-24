import streamlit as st
import requests
import datetime
import json
import os
from PIL import Image

# --- 1. 設定頁面與 CSS (Muji Refined Light Style) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# 配色定義
COLORS = {
    'bg_main': '#F9F8F6',       # 背景: 極淺暖灰
    'surface': '#FFFFFF',       # 純白
    'text_primary': '#5B5551',  # 文字: 深暖棕
    'text_secondary': '#9C8E7E',# 文字: 淺灰褐
    'accent_warm': '#C7B299',   # 燕麥色
    'accent_deep': '#8C8376',   # 深卡其
    'linen_mist': '#FAF0E6',    # 亞麻色 (Hover)
    'warm_gold': '#DEB887',     # 暖金沙 (Active)
    'nav_bg_inactive': '#F0EFEA', # 導覽列未選中
    'line_light': '#E0DCD8',    # 線條顏色
    'alert_red': '#B94047',     # 警示紅
}

# 注入 CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Shippori+Mincho:wght@400;500;700&display=swap');

    /* 1. 強制亮色主題變數 (覆蓋手機深色模式) */
    :root {{
        --primary-color: {COLORS['warm_gold']};
        --background-color: {COLORS['bg_main']};
        --secondary-background-color: {COLORS['surface']};
        --text-color: {COLORS['text_primary']};
        --font: "sans-serif";
    }}

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg_main']} !important;
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif;
        color: {COLORS['text_primary']} !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {COLORS['text_primary']} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* -----------------------------------------
       導覽列樣式 (橫向 + 縮小寬度 + 居中)
       ----------------------------------------- */
    
    /* 電腦版預設 */
    div[data-testid="column"] button {{
        background-color: {COLORS['nav_bg_inactive']} !important;
        border: none !important;
        color: {COLORS['text_secondary']} !important;
        font-weight: 500 !important;
        border-radius: 50% !important; /* 圓形 */
        width: 42px !important;        /* 固定寬度 */
        height: 42px !important;       /* 固定高度 */
        padding: 0 !important;
        margin: 0 auto !important;     /* 自身居中 */
        transition: all 0.2s ease !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    /* 手機版優化 */
    @media (max-width: 640px) {{
        /* 導覽列容器 */
        div[data-testid="stHorizontalBlock"] {{
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            justify-content: center !important; /* 整體居中 */
            gap: 8px !important; /* 按鈕間距 */
            padding-bottom: 5px; /* 預留滑動條空間 */
        }}
        
        /* 欄位寬度縮小 (不再撐滿) */
        div[data-testid="column"] {{
            min-width: auto !important;
            width: auto !important;
            flex: 0 0 auto !important; /* 不放大也不縮小，依內容大小 */
        }}

        /* 按鈕本體縮小 */
        div[data-testid="column"] button {{
            width: 36px !important;
            height: 36px !important;
            font-size: 0.85rem !important;
        }}
    }}

    /* 懸停 (Hover) */
    div[data-testid="column"] button:hover {{
        background-color: {COLORS['linen_mist']} !important;
        color: {COLORS['text_primary']} !important;
        transform: translateY(-1px);
    }}
    /* 選中 (Active) - 白底金邊 */
    div[data-testid="column"] button[kind="primary"] {{
        background-color: #FFFFFF !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['warm_gold']} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(222, 184, 135, 0.25) !important;
    }}

    /* -----------------------------------------
       通用元件樣式
       ----------------------------------------- */

    /* 簡約日式卡片 */
    .minimal-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line_light']};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }}

    /* 住宿卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLORS['line_light']} !important;
        border-radius: 16px !important;
        background-color: {COLORS['surface']} !important;
    }}
    
    /* 一般按鈕 (票券、訂單等) */
    .stButton button {{
        height: auto !important;
        padding: 8px 20px !important;
        background-color: #FFFFFF !important;
        border: 1px solid {COLORS['line_light']} !important;
        color: {COLORS['text_primary']} !important;
        border-radius: 24px;
        font-weight: 500 !important;
    }}
    .stButton button:hover {{
        border-color: {COLORS['warm_gold']} !important;
        color: {COLORS['warm_gold']} !important;
        box-shadow: 0 4px 12px rgba(222, 184, 135, 0.15);
    }}

    /* ★★★ Google Map 連結按鈕強制修正 (去黑底) ★★★ */
    /* 針對 link_button 且 href 包含 google maps 的元素 */
    a[href*="google.com/maps"] {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #FFFFFF !important; /* 白底 */
        color: {COLORS['text_primary']} !important; /* 深字 */
        border: 1px solid {COLORS['line_light']} !important; /* 淺灰框 */
        border-radius: 24px !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        width: 100%; /* 滿版 */
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }}
    a[href*="google.com/maps"]:hover {{
        border-color: {COLORS['warm_gold']} !important;
        color: {COLORS['warm_gold']} !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(222, 184, 135, 0.15) !important;
    }}
    /* 確保 icon 顏色也正確 */
    a[href*="google.com/maps"]::before {{
        content: "📍 ";
        margin-right: 5px;
    }}

    /* Expander (查看詳情) */
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
    div[data-testid="stExpander"] summary:hover {{
        color: {COLORS['warm_gold']} !important;
    }}
    div[data-testid="stExpander"] svg {{
        fill: {COLORS['text_secondary']} !important;
        color: {COLORS['text_secondary']} !important;
    }}

    /* 輸入框 */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
        background-color: #FFFFFF !important;
        color: {COLORS['text_primary']} !important;
        border-color: {COLORS['line_light']} !important;
    }}
    div[data-testid="stFileUploader"] {{
        background-color: #FFFFFF !important;
    }}
    section[data-testid="stFileUploaderDropzone"] {{
        background-color: #FAFAFA !important;
        color: {COLORS['text_secondary']} !important;
    }}

    /* Ticket Style */
    .wallet-pass {{
        background-color: #FFFFFF;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid {COLORS['line_light']};
        font-family: 'Shippori Mincho', serif;
        margin-bottom: 20px;
    }}
    .pass-header {{
        padding: 24px;
        background: {COLORS['bg_main']};
    }}
    .pass-dashed-line {{
        width: 90%;
        border-top: 1px dashed {COLORS['line_light']}; 
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

    /* Timeline */
    .timeline-point {{
        width: 9px;
        height: 9px;
        background-color: {COLORS['warm_gold']};
        border-radius: 50%;
        margin-right: 12px;
        border: 2px solid {COLORS['bg_main']}; 
        box-shadow: 0 0 0 1px {COLORS['warm_gold']};
    }}
    .timeline-line {{
        position: absolute;
        left: 3px;
        top: 24px;
        bottom: -20px;
        width: 1px;
        background-color: {COLORS['line_light']};
    }}
    
    /* 刪除按鈕 */
    .delete-btn button {{
        border: none !important;
        color: #E57373 !important;
        padding: 0px 8px !important;
        font-size: 0.8rem !important;
        background: transparent !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 (連結更新) ---
if 'view' not in st.session_state: st.session_state.view = 'overview'
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing' not in st.session_state: st.session_state.packing = {}

# 預設清單
DEFAULT_PACKING = [
    { "category": "Documents", "items": ["護照", "VJW QR", "機票截圖"] },
    { "category": "Clothing", "items": ["發熱衣", "防風外套", "毛帽"] },
    { "category": "Electronics", "items": ["網卡", "行動電源", "充電線"] }
]

if 'packing_list' not in st.session_state:
    st.session_state.packing_list = DEFAULT_PACKING

# ★★★ 更新真實 Google Maps 連結 ★★★
APP_DATA = {
  "flight": { 
    "outbound": { "code": "TR892", "time": "12:30", "arrival": "17:20" }, 
    "inbound": { "code": "TR893", "time": "18:40", "arrival": "22:15" } 
  },
  "days": [
    { 
      "id": 0, 
      "date": "12/08 (一)", 
      "location": "Sapporo", 
      "coords": { "lat": 43.0618, "lon": 141.3545 }, 
      "hotel": "JR-EAST METS", 
      "hotel_note": "札幌站北口", 
      "activities": [
        { "time": "17:20", "text": "航班抵達 CTS", "type": "transport", "desc": "往 B1 搭 JR。", "guideText": "新千歲機場結構簡單，國際線出來後沿著指示標誌走約10分鐘可達國內線B1搭乘JR。建議先買好Kitaca或在售票機買票。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=New+Chitose+Airport+JR+Station" },
        { "time": "19:45", "text": "飯店 Check-in", "type": "hotel", "desc": "JR-EAST METS", "guideText": "這間飯店最大優勢是「與車站直結」，北口出來步行2分鐘即達。大廳備品豐富，記得拿一些泡澡粉舒緩搭機疲勞。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=JR-East+Hotel+Mets+Sapporo", "contact": "+81-11-729-0011" },
        { "time": "20:15", "text": "晚餐：湯咖哩", "type": "food", "desc": "Suage+ / GARAKU", "menu": ["知床雞野菜湯咖哩", "起司飯", "炸舞菇"], "notes": ["不可預約", "辣度選3", "現場排隊約30分"], "guideText": "北海道靈魂美食！Suage+特色是串籤素炸，保留食材原味；GARAKU湯頭較濃郁。推薦點「知床雞」搭配起司飯，將飯浸入湯中享用是道地吃法。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Soup+Curry+Suage+", "contact": "不可預約 / 現場候位", "stayTime": "1.5 小時" },
        { "time": "22:30", "text": "夜間咖啡", "type": "food", "desc": "ESPRESSO D WORKS", "menu": ["巴斯克起司蛋糕", "拿鐵"], "notes": ["營業至24:00"], "guideText": "札幌有「收尾聖代」文化，這間則是深夜也能吃到的高品質巴斯克蛋糕。氛圍時髦放鬆，適合第一晚整理心情。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=ESPRESSO+D+WORKS+Sapporo", "contact": "營業至 23:30", "stayTime": "1 小時" }
      ]
    },
    { 
      "id": 1, "date": "12/09 (二)", "location": "Sapporo → Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "Ski-in Ski-out", 
      "activities": [
          { "time": "11:30", "text": "午餐：Uni Murakami", "type": "food", "desc": "海膽丼", "menu": ["生海膽丼", "海膽天婦羅", "海鮮燒烤"], "notes": ["價格較高", "建議訂位"], "guideText": "函館名店的分店，主打「無添加明礬」的生海膽，吃起來完全沒有苦味，只有濃郁的甜味與海水香氣，價格稍高但絕對值得。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Uni+Murakami+Sapporo", "contact": "011-290-1000", "stayTime": "1.5 小時" },
          { "time": "15:00", "text": "JR 移動", "type": "transport", "desc": "往俱知安", "guideText": "這段鐵路風景極美，這季節會經過銀白色的雪原與海岸線。若遇大雪JR容易停駛，請務必隨時關注JR北海道官網運行狀況。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Sapporo+Station" },
          { "time": "18:00", "text": "Check-in", "type": "hotel", "desc": "Park Hyatt", "guideText": "二世谷頂級奢華代表。位於Hanazono雪場正下方，Ski-in/out極度方便。大廳的挑高落地窗能直接看到羊蹄山，Check-in 時請準備好相機。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Park+Hyatt+Niseko+Hanazono", "contact": "+81-136-27-1234" }
      ]
    },
    { 
      "id": 2, "date": "12/10 (三)", "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 2", 
      "activities": [
          { "time": "09:00", "text": "全日滑雪", "type": "activity", "desc": "粉雪天堂", "guideText": "Hanazono雪場對新手友善，有魔毯設施；高手則可挑戰樹林區。粉雪(Japow)摔倒也不痛。記得做好防寒，風鏡和面罩是必備品。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Hanazono+Resort" },
          { "time": "12:00", "text": "午餐：Hanazono EDGE", "type": "food", "desc": "雪場餐廳", "menu": ["蟹肉拉麵", "炸豬排咖哩", "披薩"], "notes": ["建議11:30前到", "人潮眾多"], "guideText": "近年翻新的雪場餐廳，挑高設計視野極佳。蟹肉拉麵湯頭鮮美，滑雪後喝熱湯最過癮。午餐時段一位難求，強烈建議提早11:30前入座。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Hanazono+EDGE", "contact": "無預約服務", "stayTime": "1 小時" },
          { "time": "18:00", "text": "Hirafu 晚餐", "type": "food", "desc": "居酒屋/燒肉", "menu": ["成吉思汗烤肉", "北海道生啤酒", "烤羊肉"], "notes": ["需提前預約", "搭飯店接駁車"], "guideText": "Hirafu是二世谷最熱鬧的區域，充滿異國風情。成吉思汗烤羊肉沒有腥味，搭配冰涼的Sapporo Classic啤酒是絕配。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Hirafu+Village", "contact": "需查閱特定餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 3, "date": "12/11 (四)", "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 3", 
      "activities": [
          { "time": "13:00", "text": "午餐：手工蕎麥麵", "type": "food", "desc": "Ichimura", "menu": ["鴨肉蕎麥麵", "炸蝦天婦羅", "蕎麥湯"], "notes": ["Cash Only", "賣完為止"], "guideText": "使用二世谷清甜泉水製作的手打十割蕎麥麵，麵條香氣十足。鴨肉蕎麥麵是招牌，湯頭甘甜。注意只收現金，且常常賣完提早打烊。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Niseko+Sobadokoro+Rakuichi", "contact": "0136-23-0603", "stayTime": "1 小時" },
          { "time": "18:00", "text": "晚餐：China Kitchen", "type": "food", "desc": "飯店內中餐", "menu": ["北京烤鴨", "四川擔擔麵", "港式點心"], "notes": ["Smart Casual", "房客優先"], "guideText": "玩累了不想出門，飯店內的China Kitchen水準極高。週末有早午餐吃到飽，晚餐則推薦烤鴨與擔擔麵，口味精緻道地，服務也是一流。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=China+Kitchen+Park+Hyatt+Niseko", "contact": "內線直撥餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 4, "date": "12/12 (五)", "location": "CTS Airport", "coords": {"lat": 42.7752, "lon": 141.6923}, 
      "hotel": "Home Sweet Home", "hotel_note": "機場日", 
      "activities": [
          { "time": "09:20", "text": "巴士出發", "type": "transport", "desc": "前往機場", "guideText": "從二世谷搭巴士直達機場最方便，不用扛行李轉車。冬天路況難料，巴士時間通常抓很寬裕，上車即可補眠欣賞雪景。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Park+Hyatt+Niseko+Bus+Stop" },
          { "time": "13:00", "text": "拉麵道場", "type": "food", "desc": "一幻 / 白樺山莊", "menu": ["鮮蝦鹽味拉麵", "味噌拉麵", "免費水煮蛋"], "notes": ["行李需寄放", "排隊人潮多"], "guideText": "機場國內線3樓的拉麵一級戰區。「一幻」主打濃郁蝦湯，鮮味衝擊；「白樺山莊」則有無限供應的水煮蛋，味噌湯頭偏油香。登機前的最後美味！", "mapUrl": "https://www.google.com/maps/search/?api=1&query=Hokkaido+Ramen+Dojo+New+Chitose", "contact": "機場國內線 3F", "stayTime": "1 小時" },
          { "time": "14:30", "text": "甜點 & 伴手禮巡禮", "type": "food", "desc": "國內線 2F 掃貨", "menu": ["北菓樓 夢不思議泡芙 (必吃!)", "LeTAO 起司霜淇淋", "Calbee+ 現炸薯條", "雪印 北海道牛奶霜淇淋", "Kinotoya 起司塔"], "notes": ["國內線比較好逛", "保冷袋必備"], "guideText": "新千歲機場國內線2F是伴手禮一級戰區！\n\n【機場必買 Top 10】\n1. 北菓樓 (妖精之森/夢不思議泡芙)\n2. 六花亭 (奶油葡萄夾心/草莓巧克力)\n3. ROYCE (生巧克力/洋芋片)\n4. LeTAO (雙層起司蛋糕)\n5. Snaffle's (起司舒芙蕾)\n6. Calbee+ (薯條三兄弟)\n7. 白色戀人\n8. HORI (哈密瓜果凍)\n9. Kitaichi Glass (玻璃杯)\n10. 十勝牛奶布丁", "mapUrl": "https://www.new-chitose-airport.jp/tw/floor/2f.html", "contact": "國內線 2F", "stayTime": "2.5 小時" },
          { "time": "18:40", "text": "TR893 起飛", "type": "transport", "desc": "返台", "guideText": "酷航櫃台通常在起飛前3小時開櫃，建議提早去排隊托運，因為新千歲國際線免稅店排隊結帳人潮通常非常驚人。", "mapUrl": "https://www.google.com/maps/search/?api=1&query=New+Chitose+Airport+International+Terminal" }
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
        # 檢視模式
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
            st.image(existing['image'], caption="E-Ticket / Booking Confirmation", use_container_width=True)

        if existing.get('url'): st.link_button("🔗 OPEN LINK", existing['url'], use_container_width=True)
        
        if st.button("Edit Voucher", key="edit_btn", use_container_width=True):
            st.session_state.is_editing = True
            st.rerun()
    else:
        # 編輯模式
        st.markdown("### Edit Details")
        new_order = st.text_input("Confirmation No.", value=existing.get("orderNumber", ""))
        new_url = st.text_input("Link URL", value=existing.get("url", ""))
        new_note = st.text_area("Notes", value=existing.get("note", ""))
        
        new_image = st.file_uploader("Upload Ticket Image", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Save Changes", type="primary", use_container_width=True):
            final_image = new_image if new_image else existing.get('image')
            st.session_state.tickets[ticket_key] = {
                "orderNumber": new_order, 
                "url": new_url, 
                "note": new_note,
                "image": final_image
            }
            st.session_state.is_editing = False
            st.rerun()

# --- 5. 頂部導覽列 ---
st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# 使用 7 個等寬欄位 (手機版 CSS 已強制縮小)
nav_cols = st.columns(7)
nav_items = [
    ("🏠", "overview"), 
    ("08", 0), 
    ("09", 1), 
    ("10", 2), 
    ("11", 3), 
    ("12", 4), 
    ("🎒", "packing")
]

for i, (label, view_name) in enumerate(nav_items):
    is_active = st.session_state.view == view_name
    if nav_cols[i].button(label, key=f"nav_{i}", type="primary" if is_active else "secondary", use_container_width=True):
        st.session_state.view = view_name
        st.rerun()

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# --- 6. 頁面視圖 ---

def view_overview():
    # Header
    st.markdown(f"""
    <div style='text-align:center; padding: 30px 0 20px;'>
        <h1 style='font-family: "Shippori Mincho", serif; font-size: 2.5rem; margin-bottom: 8px; letter-spacing: 1px; font-weight: 500;'>Hokkaido</h1>
        <p style='color:{COLORS['text_secondary']}; letter-spacing: 0.3em; font-size: 0.8rem; font-weight: 400;'>DECEMBER 2025</p>
        <div style="width: 60px; height: 1px; background-color: {COLORS['line_light']}; margin: 20px auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # VJW Card
    vjw_url = "https://vjw-lp.digital.go.jp/en/"
    st.markdown(f"""
    <style>
    .vjw-card-minimal {{
        display: flex; align-items: center; justify-content: space-between;
        text-decoration: none !important;
        background: {COLORS['surface']}; 
        border: 1px solid {COLORS['line_light']};
        border-radius: 12px; padding: 16px 24px; margin-bottom: 24px;
        transition: all 0.2s ease;
    }}
    .vjw-card-minimal:hover {{ border-color: {COLORS['accent_warm']}; text-decoration: none !important; }}
    .vjw-content-min {{ display: flex; align-items: center; color: {COLORS['text_primary']}; }}
    .vjw-icon-min {{ font-size: 20px; margin-right: 16px; color: {COLORS['text_secondary']}; }}
    .vjw-title-min {{ font-size: 16px; font-weight: 500; letter-spacing: 0.5px; margin-bottom: 4px; font-family: 'Shippori Mincho', serif; text-decoration: none !important; }}
    .vjw-subtitle-min {{ font-size: 12px; opacity: 0.8; font-weight: 400; color: {COLORS['text_secondary']}; text-decoration: none !important; }}
    .vjw-arrow-min {{ font-size: 18px; opacity: 0.6; color: {COLORS['text_secondary']}; }}
    .vjw-card-minimal * {{ text-decoration: none !important; }}
    </style>
    <a href="{vjw_url}" target="_blank" class="vjw-card-minimal">
        <div class="vjw-content-min">
            <div class="vjw-icon-min">✈️</div>
            <div><div class="vjw-title-min">Visit Japan Web</div><div class="vjw-subtitle-min">入境日本必須申請</div></div>
        </div>
        <div class="vjw-arrow-min">→</div>
    </a>
    """, unsafe_allow_html=True)

    # Info Grid
    rate = get_exchange_rate()
    temp1, weather1 = get_weather(43.06, 141.35) # Sapporo
    temp2, weather2 = get_weather(42.80, 140.68) # Niseko

    st.markdown(f"""
    <div class="info-grid-minimal">
        <div class="info-box-minimal">
            <div class="info-label-minimal">EXCHANGE</div>
            <div style="display: flex; align-items: baseline;">
                <span style="font-size: 0.9rem; color: {COLORS['text_secondary']}; margin-right: 4px;">¥1000 ≈</span>
                <div class="info-value-minimal">{int(rate*1000) if rate else '...'}</div>
                <span style="font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-left: 4px;">TWD</span>
            </div>
            <div style="font-size:0.7rem; color:{COLORS['text_secondary']}; margin-top:4px;">1 JPY = {rate:.3f}</div>
        </div>
        <div class="info-box-minimal">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid {COLORS['line_light']}; padding-bottom: 4px;">
                <div class="info-label-minimal" style="margin-bottom: 0; border: none;">WEATHER</div>
                <div class="info-label-minimal" style="margin-bottom: 0; color: {COLORS['text_secondary']}; border: none;">TODAY</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="font-family: 'Shippori Mincho', serif; font-size: 1rem;">Sapporo</div>
                <div><span style="font-family: 'Shippori Mincho', serif; font-size: 1rem; font-weight: 500;">{temp1}°</span> <span style="font-size: 0.8rem; color: {COLORS['text_secondary']}; background: #F0EFEA; padding: 2px 6px; border-radius: 4px;">{weather1}</span></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-family: 'Shippori Mincho', serif; font-size: 1rem;">Niseko</div>
                <div><span style="font-family: 'Shippori Mincho', serif; font-size: 1rem; font-weight: 500;">{temp2}°</span> <span style="font-size: 0.8rem; color: {COLORS['text_secondary']}; background: #F0EFEA; padding: 2px 6px; border-radius: 4px;">{weather2}</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Flights Card
    st.markdown(f'<div class="minimal-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1rem; margin-bottom:1rem; display:flex; align-items:center; gap:8px; font-weight: 500; border-bottom: 1px solid {COLORS['line_light']}; padding-bottom: 8px;'>✈️ 航班 <span style='margin-left: auto; color: {COLORS['text_secondary']}; font-size: 1.2rem;'>•••</span></h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns(2)
    
    with f1:
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-bottom: 4px;'>DEC 08 (OUT)</div>
            <div style='font-size: 1.4rem; font-weight: 500; font-family: "Shippori Mincho", serif; color: {COLORS['text_primary']};'>
                {APP_DATA['flight']['outbound']['time']}
            </div>
            <div style='color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 2px 0;'>↓</div>
            <div style='font-size: 1.4rem; font-weight: 500; font-family: "Shippori Mincho", serif; color: {COLORS['text_primary']};'>
                {APP_DATA['flight']['outbound']['arrival']}
            </div>
            <div style='font-size: 0.9rem; color: {COLORS['text_secondary']}; margin-top:6px; font-weight:bold;'>{APP_DATA['flight']['outbound']['code']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Input Ticket", key="fw_w", use_container_width=True): ticket_modal("flight_wei", "Flight (Outbound)")

    with f2:
        st.markdown(f"""
        <div style='text-align: center; border-left: 1px solid {COLORS['line_light']};'>
            <div style='font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-bottom: 4px;'>DEC 12 (IN)</div>
            <div style='font-size: 1.4rem; font-weight: 500; font-family: "Shippori Mincho", serif; color: {COLORS['text_primary']};'>
                {APP_DATA['flight']['inbound']['time']}
            </div>
            <div style='color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 2px 0;'>↓</div>
            <div style='font-size: 1.4rem; font-weight: 500; font-family: "Shippori Mincho", serif; color: {COLORS['text_primary']};'>
                {APP_DATA['flight']['inbound']['arrival']}
            </div>
            <div style='font-size: 0.9rem; color: {COLORS['text_secondary']}; margin-top:6px; font-weight:bold;'>{APP_DATA['flight']['inbound']['code']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Input Ticket", key="fi_c", use_container_width=True): ticket_modal("flight_chien", "Flight (Inbound)")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Emergency Card
    st.markdown(f"""
    <div class="minimal-card" style="border-color: {COLORS['line_light']}; background: {COLORS['surface']}; margin-top: 30px;">
        <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS['alert_red']}; letter-spacing: 0.1em; margin-bottom: 12px; border-bottom: 1px solid {COLORS['line_light']}; padding-bottom: 8px;">緊急求助 / EMERGENCY</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
             <div style="text-align: center; width: 48%;">
                 <div style="font-family: 'Shippori Mincho', serif; font-size: 1.4rem; font-weight: 500; color: {COLORS['text_primary']};">110</div>
                 <div style="font-size: 0.7rem; color: {COLORS['text_secondary']};">報警 Police</div>
             </div>
             <div style="text-align: center; width: 48%; border-left: 1px solid {COLORS['line_light']};">
                 <div style="font-family: 'Shippori Mincho', serif; font-size: 1.4rem; font-weight: 500; color: {COLORS['text_primary']};">119</div>
                 <div style="font-size: 0.7rem; color: {COLORS['text_secondary']};">救護 Ambulance</div>
             </div>
        </div>
        <div style="background: #F9F9F9; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid {COLORS['line_light']};">
             <div style="font-size: 0.75rem; color: {COLORS['text_secondary']}; margin-bottom: 4px;">札幌辦事處 Sapporo Office</div>
             <div style="font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 500; color: {COLORS['text_primary']};">080-1460-2568</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def view_day(day_id):
    day = APP_DATA['days'][day_id]
    
    # Weather
    lat = day['coords']['lat']
    lon = day['coords']['lon']
    temp, w_text = get_weather(lat, lon) 

    # Header
    weather_html = f"""
<div style="text-align:center; margin-bottom: 2rem; padding-top: 10px;">
<h2 style="font-family: 'Shippori Mincho', serif; font-size: 3rem; margin:0 0 4px 0; color:{COLORS['text_primary']}; letter-spacing: 1px; font-weight: 500;">{day['date'].split(' ')[0]}</h2>
<div style="color:{COLORS['text_secondary']}; font-size:0.9rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom: 16px; display: flex; align-items: center; justify-content: center; gap: 6px;"><span style="font-size: 1rem;">📍</span> {day['location']}</div>
<div style="display: inline-flex; align-items: center; gap: 8px; background: {COLORS['surface']}; padding: 6px 16px; border-radius: 20px; border: 1px solid {COLORS['line_light']};">
<span style="font-family: 'Shippori Mincho', serif; font-size: 1.1rem; font-weight: 500; color: {COLORS['text_primary']}">{temp}°</span>
<span style="font-size: 0.9rem; color: {COLORS['text_secondary']}; border-left: 1px solid {COLORS['line_light']}; padding-left: 8px;">{w_text}</span>
</div>
</div>
"""
    st.markdown(weather_html, unsafe_allow_html=True)

    # Hotel Card
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div style="font-size:0.7rem; font-weight:600; color:{COLORS['text_secondary']}; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:6px;">ACCOMMODATION</div>
                <div style="font-weight:500; font-size:1.2rem; margin-bottom:4px; font-family: 'Shippori Mincho', serif;">{day['hotel']}</div>
                <div style="font-size:0.85rem; color:{COLORS['text_secondary']};">{day['hotel_note']}</div>
            </div>
            <div style="font-size:1.8rem; color:{COLORS['line_light']};">🛏️</div>
        </div>
        <div style="border-top: 1px dashed {COLORS['line_light']}; margin: 16px 0 12px 0;"></div>
        """, unsafe_allow_html=True)
        
        if st.button("Booking Info / 訂單資料", key=f"hotel_btn_{day_id}", use_container_width=True):
            ticket_modal(f"hotel_{day_id}", f"Hotel: {day['hotel']}")

    st.write("")

    # Timeline
    for i, act in enumerate(day['activities']):
        timeline_html = f"""
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
"""
        st.markdown(timeline_html, unsafe_allow_html=True)
        
        with st.expander(f"查看詳情"):
            if 'guideText' in act:
                st.markdown(f"""
                <div style="padding:12px; border-radius:8px; margin-bottom:12px; background: #F0EFEA;">
                    <strong style="color:{COLORS['accent_deep']}; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; display:block; margin-bottom:4px;">💡 Note</strong>
                    <p style="font-size:0.9rem; line-height:1.6; color:{COLORS['text_primary']}; margin:0;">{act['guideText']}</p>
                </div>
                """, unsafe_allow_html=True)

            if act['type'] == 'food' and 'menu' in act:
                # 白色背景
                st.markdown(f"""
                <div style="padding:16px; border-radius:10px; margin-bottom:12px; background: #FFFFFF; border: 1px solid {COLORS['line_light']};">
                    <div style="font-size:0.75rem; font-weight:600; color:{COLORS['accent_warm']}; margin-bottom:8px; letter-spacing: 0.1em; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom:4px;">🍽️ RECOMMENDED MENU</div>
                    <ul style="margin: 0; padding-left: 20px; color: {COLORS['text_primary']}; font-size: 0.95rem;">
                        {''.join([f'<li style="margin-bottom:4px;">{m}</li>' for m in act['menu']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")

            # ★★★ Google Map 按鈕修正 ★★★
            if 'mapUrl' in act:
                # 使用 CSS class 來確保樣式，並使用 st.link_button (需 Streamlit 1.27+) 或 HTML
                st.link_button("📍 Google Map", act['mapUrl'], use_container_width=True)
                st.write("") # Spacer

            actions = []
            if act['type'] == 'transport':
                actions.append("ticket_w")
                actions.append("ticket_c")
            
            if actions:
                cols = st.columns(len(actions))
                col_idx = 0
                if "ticket_w" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (W)", key=f"t_{day_id}_{i}_w", use_container_width=True): ticket_modal(f"t_{day_id}_{i}_w", f"Ticket (W) - {act['text']}")
                    col_idx += 1
                if "ticket_c" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (C)", key=f"t_{day_id}_{i}_c", use_container_width=True): ticket_modal(f"t_{day_id}_{i}_c", f"Ticket (C) - {act['text']}")

def view_packing():
    st.markdown(f"<h2 style='text-align:center; margin-bottom:1.5rem; font-family: \"Shippori Mincho\", serif;'>Packing List</h2>", unsafe_allow_html=True)
    
    total = sum(len(cat['items']) for cat in st.session_state.packing_list)
    checked = sum(1 for k, v in st.session_state.packing.items() if v)
    
    st.markdown(f"""<style>
        .stProgress > div > div > div > div {{ background-color: {COLORS['warm_gold']}; }}
    </style>""", unsafe_allow_html=True)
    st.progress(checked / total if total > 0 else 0)
    
    st.write("")
    
    # 顯示清單 (含刪除功能)
    for i, cat in enumerate(st.session_state.packing_list[:]):
        with st.container():
            col_title, col_del_cat = st.columns([8, 1])
            with col_title:
                st.markdown(f"""
                <div style="padding: 1.2rem 1.2rem 0.5rem 1.2rem; background: {COLORS['surface']}; border: 1px solid {COLORS['line_light']}; border-bottom:none; border-top-left-radius: 12px; border-top-right-radius: 12px;">
                    <h4 style='margin:0; color:{COLORS['text_primary']}; font-family: "Shippori Mincho", serif;'>{cat['category']}</h4>
                </div>
                """, unsafe_allow_html=True)
            with col_del_cat:
                if st.button("🗑️", key=f"del_cat_{i}", help="Delete Category"):
                    st.session_state.packing_list.pop(i)
                    st.rerun()

            st.markdown(f"""<div style="padding: 0 1.2rem 1.2rem 1.2rem; background: {COLORS['surface']}; border: 1px solid {COLORS['line_light']}; border-top:none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin-bottom: 1rem;">""", unsafe_allow_html=True)
            
            for j, item in enumerate(cat['items']):
                c1, c2 = st.columns([8, 1])
                with c1:
                    key = f"pack_{item}"
                    val = st.checkbox(item, value=st.session_state.packing.get(key, False), key=key)
                    st.session_state.packing[key] = val
                with c2:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("✕", key=f"del_item_{i}_{j}"):
                        st.session_state.packing_list[i]['items'].pop(j)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
    # 新增物品/分類區塊
    st.markdown("---")
    st.markdown("##### ➕ Add New Item")
    
    col_cat, col_item, col_add = st.columns([2, 3, 1])
    with col_cat:
        new_cat_input = st.text_input("Category", placeholder="分類 (選填)", label_visibility="collapsed")
    
    with col_item:
        new_item_input = st.text_input("Item Name", placeholder="物品名稱", label_visibility="collapsed")
        
    with col_add:
        if st.button("Add", use_container_width=True):
            if new_item_input:
                target_cat_name = new_cat_input if new_cat_input else "Personal"
                target_cat = next((c for c in st.session_state.packing_list if c['category'] == target_cat_name), None)
                
                if target_cat:
                    target_cat['items'].append(new_item_input)
                else:
                    st.session_state.packing_list.append({"category": target_cat_name, "items": [new_item_input]})
                
                st.rerun()

# --- 7. 渲染主畫面 ---
if st.session_state.view == 'overview': view_overview()
elif st.session_state.view == 'packing': view_packing()
elif isinstance(st.session_state.view, int): view_day(st.session_state.view)
