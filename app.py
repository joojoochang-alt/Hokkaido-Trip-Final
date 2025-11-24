import streamlit as st
import requests
import datetime
import json
import os
from PIL import Image

# --- 1. 設定頁面與 CSS (Muji Lively Earth Style) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# Muji 風格配色 (加入 #FFE4E1 與 #DEB887)
COLORS = {
    'bg_main': '#F9F8F6',       # 背景: 極淺暖灰
    'surface': '#FFFFFF',       # 卡片: 純白
    'text_primary': '#5B5551',  # 文字: 深暖棕
    'text_secondary': '#9C8E7E',# 文字: 淺灰褐
    
    # --- 新增顏色 ---
    'rose_mist': '#FFE4E1',     # 霧玫瑰 (用於 hover, 美食背景)
    'warm_gold': '#DEB887',     # 暖金沙 (用於選中狀態, 時間軸點, 強調邊框)
    # ----------------
    
    'line_light': '#E0DCD8',    # 線條顏色
    'alert_red': '#B94047',     # 警示紅
    'nav_bg': '#F0EFEA',        # 導覽列預設背景
}

# 注入 CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Shippori+Mincho:wght@400;500;700&display=swap');

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg_main']};
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif;
        color: {COLORS['text_primary']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Shippori Mincho', 'Noto Serif TC', serif !important;
        color: {COLORS['text_primary']} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* 簡約日式卡片 (有邊框) */
    .minimal-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line_light']};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }}

    /* Streamlit Container 自定義邊框顏色 (用於住宿卡片) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLORS['line_light']} !important;
        border-radius: 16px !important;
        background-color: {COLORS['surface']};
    }}
    
    /* 按鈕樣式 */
    .stButton button {{
        background-color: transparent;
        border: 1px solid {COLORS['line_light']} !important;
        color: {COLORS['text_secondary']};
        border-radius: 24px;
        padding: 6px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
        font-family: 'Shippori Mincho', serif;
    }}
    /* Hover: 使用暖金沙色邊框與文字 */
    .stButton button:hover {{
        background-color: #FFFFFF !important;
        color: {COLORS['warm_gold']} !important; 
        border-color: {COLORS['warm_gold']} !important;
        box-shadow: 0 4px 12px rgba(222, 184, 135, 0.15); /* 金色暈影 */
        transform: translateY(-1px);
    }}
    /* Primary: 實心暖金沙色 */
    .stButton button[kind="primary"] {{
        background-color: #FFFFFF !important;
        color: {COLORS['warm_gold']} !important;
        border: 1px solid {COLORS['warm_gold']} !important;
        font-weight: 700;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}

    /* 導覽列按鈕 (色塊風格 - 新顏色應用) */
    div[data-testid="column"] button {{
        background-color: {COLORS['nav_bg']} !important;
        border: none !important;
        color: {COLORS['text_secondary']} !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        height: auto !important;
        padding: 8px 4px !important;
    }}
    /* Nav Hover: 霧玫瑰色背景 */
    div[data-testid="column"] button:hover {{
        background-color: {COLORS['rose_mist']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    /* Nav Active: 暖金沙色背景 */
    div[data-testid="column"] button[kind="primary"] {{
        background-color: {COLORS['warm_gold']} !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(222, 184, 135, 0.4) !important;
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
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid {COLORS['line_light']};
    }}
    .info-label-minimal {{
        font-size: 0.7rem;
        font-weight: 700;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        border-bottom: 1px solid {COLORS['line_light']};
        padding-bottom: 4px;
    }}
    .info-value-minimal {{
        font-family: 'Shippori Mincho', serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        line-height: 1.2;
        margin-top: 8px;
    }}

    /* Expander */
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

    /* 時間軸 - 使用暖金沙色 */
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
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 ---
if 'view' not in st.session_state: st.session_state.view = 'overview'
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing' not in st.session_state: st.session_state.packing = {}

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
        { "time": "17:20", "text": "航班抵達 CTS", "type": "transport", "desc": "往 B1 搭 JR。", "guideText": "新千歲機場結構簡單，國際線出來後沿著指示標誌走約10分鐘可達國內線B1搭乘JR。建議先買好Kitaca或在售票機買票。", "mapUrl": "https://goo.gl/maps/NewChitoseAirport" },
        { "time": "19:45", "text": "飯店 Check-in", "type": "hotel", "desc": "JR-EAST METS", "guideText": "這間飯店最大優勢是「與車站直結」，北口出來步行2分鐘即達。大廳備品豐富，記得拿一些泡澡粉舒緩搭機疲勞。", "mapUrl": "https://maps.app.goo.gl/SapporoStationNorth", "contact": "+81-11-729-0011" },
        { "time": "20:15", "text": "晚餐：湯咖哩", "type": "food", "desc": "Suage+ / GARAKU", "menu": ["知床雞野菜湯咖哩", "起司飯", "炸舞菇"], "notes": ["不可預約", "辣度選3", "現場排隊約30分"], "guideText": "北海道靈魂美食！Suage+特色是串籤素炸，保留食材原味；GARAKU湯頭較濃郁。推薦點「知床雞」搭配起司飯，將飯浸入湯中享用是道地吃法。", "mapUrl": "https://maps.app.goo.gl/SuagePlus", "contact": "不可預約 / 現場候位", "stayTime": "1.5 小時" },
        { "time": "22:30", "text": "夜間咖啡", "type": "food", "desc": "ESPRESSO D WORKS", "menu": ["巴斯克起司蛋糕", "拿鐵"], "notes": ["營業至24:00"], "guideText": "札幌有「收尾聖代」文化，這間則是深夜也能吃到的高品質巴斯克蛋糕。氛圍時髦放鬆，適合第一晚整理心情。", "mapUrl": "https://maps.app.goo.gl/EspressoDWorks", "contact": "營業至 23:30", "stayTime": "1 小時" }
      ]
    },
    { 
      "id": 1, "date": "12/09 (二)", "location": "Sapporo → Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "Ski-in Ski-out", 
      "activities": [
          { "time": "11:30", "text": "午餐：Uni Murakami", "type": "food", "desc": "海膽丼", "menu": ["生海膽丼", "海膽天婦羅", "海鮮燒烤"], "notes": ["價格較高", "建議訂位"], "guideText": "函館名店的分店，主打「無添加明礬」的生海膽，吃起來完全沒有苦味，只有濃郁的甜味與海水香氣，價格稍高但絕對值得。", "mapUrl": "https://maps.app.goo.gl/UniMurakamiSapporo", "contact": "011-290-1000", "stayTime": "1.5 小時" },
          { "time": "15:00", "text": "JR 移動", "type": "transport", "desc": "往俱知安", "guideText": "這段鐵路風景極美，這季節會經過銀白色的雪原與海岸線。若遇大雪JR容易停駛，請務必隨時關注JR北海道官網運行狀況。", "mapUrl": "https://maps.app.goo.gl/KutchanStation" },
          { "time": "18:00", "text": "Check-in", "type": "hotel", "desc": "Park Hyatt", "guideText": "二世谷頂級奢華代表。位於Hanazono雪場正下方，Ski-in/out極度方便。大廳的挑高落地窗能直接看到羊蹄山，Check-in 時請準備好相機。", "mapUrl": "https://maps.app.goo.gl/ParkHyattNiseko", "contact": "+81-136-27-1234" }
      ]
    },
    { 
      "id": 2, "date": "12/10 (三)", "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 2", 
      "activities": [
          { "time": "09:00", "text": "全日滑雪", "type": "activity", "desc": "粉雪天堂", "guideText": "Hanazono雪場對新手友善，有魔毯設施；高手則可挑戰樹林區。粉雪(Japow)摔倒也不痛。記得做好防寒，風鏡和面罩是必備品。", "mapUrl": "https://maps.app.goo.gl/HanazonoResort" },
          { "time": "12:00", "text": "午餐：Hanazono EDGE", "type": "food", "desc": "雪場餐廳", "menu": ["蟹肉拉麵", "炸豬排咖哩", "披薩"], "notes": ["建議11:30前到", "人潮眾多"], "guideText": "近年翻新的雪場餐廳，挑高設計視野極佳。蟹肉拉麵湯頭鮮美，滑雪後喝熱湯最過癮。午餐時段一位難求，強烈建議提早11:30前入座。", "mapUrl": "https://maps.app.goo.gl/HanazonoEDGE", "contact": "無預約服務", "stayTime": "1 小時" },
          { "time": "18:00", "text": "Hirafu 晚餐", "type": "food", "desc": "居酒屋/燒肉", "menu": ["成吉思汗烤肉", "北海道生啤酒", "烤羊肉"], "notes": ["需提前預約", "搭飯店接駁車"], "guideText": "Hirafu是二世谷最熱鬧的區域，充滿異國風情。成吉思汗烤羊肉沒有腥味，搭配冰涼的Sapporo Classic啤酒是絕配。", "mapUrl": "https://maps.app.goo.gl/HirafuVillage", "contact": "需查閱特定餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 3, "date": "12/11 (四)", "location": "Niseko", "coords": {"lat": 42.8048, "lon": 140.6874}, 
      "hotel": "Park Hyatt Niseko", "hotel_note": "連泊 Day 3", 
      "activities": [
          { "time": "13:00", "text": "午餐：手工蕎麥麵", "type": "food", "desc": "Ichimura", "menu": ["鴨肉蕎麥麵", "炸蝦天婦羅", "蕎麥湯"], "notes": ["Cash Only", "賣完為止"], "guideText": "使用二世谷清甜泉水製作的手打十割蕎麥麵，麵條香氣十足。鴨肉蕎麥麵是招牌，湯頭甘甜。注意只收現金，且常常賣完提早打烊。", "mapUrl": "https://maps.app.goo.gl/NisekoIchimura", "contact": "0136-23-0603", "stayTime": "1 小時" },
          { "time": "18:00", "text": "晚餐：China Kitchen", "type": "food", "desc": "飯店內中餐", "menu": ["北京烤鴨", "四川擔擔麵", "港式點心"], "notes": ["Smart Casual", "房客優先"], "guideText": "玩累了不想出門，飯店內的China Kitchen水準極高。週末有早午餐吃到飽，晚餐則推薦烤鴨與擔擔麵，口味精緻道地，服務也是一流。", "mapUrl": "https://maps.app.goo.gl/ParkHyattChinaKitchen", "contact": "內線直撥餐廳", "stayTime": "2 小時" }
      ]
    },
    { 
      "id": 4, "date": "12/12 (五)", "location": "CTS Airport", "coords": {"lat": 42.7752, "lon": 141.6923}, 
      "hotel": "Home Sweet Home", "hotel_note": "機場日", 
      "activities": [
          { "time": "09:20", "text": "巴士出發", "type": "transport", "desc": "前往機場", "guideText": "從二世谷搭巴士直達機場最方便，不用扛行李轉車。冬天路況難料，巴士時間通常抓很寬裕，上車即可補眠欣賞雪景。", "mapUrl": "https://maps.app.goo.gl/HirafuBusStop" },
          { "time": "13:00", "text": "拉麵道場", "type": "food", "desc": "一幻 / 白樺山莊", "menu": ["鮮蝦鹽味拉麵", "味噌拉麵", "免費水煮蛋"], "notes": ["行李需寄放", "排隊人潮多"], "guideText": "機場國內線3樓的拉麵一級戰區。「一幻」主打濃郁蝦湯，鮮味衝擊；「白樺山莊」則有無限供應的水煮蛋，味噌湯頭偏油香。登機前的最後美味！", "mapUrl": "https://maps.app.goo.gl/CTSRamenDojo", "contact": "機場國內線 3F", "stayTime": "1 小時" },
          { "time": "14:30", "text": "甜點 & 伴手禮巡禮", "type": "food", "desc": "國內線 2F 掃貨", "menu": ["北菓樓 夢不思議泡芙 (必吃!)", "LeTAO 起司霜淇淋", "Calbee+ 現炸薯條", "雪印 北海道牛奶霜淇淋", "Kinotoya 起司塔"], "notes": ["國內線比較好逛", "保冷袋必備"], "guideText": "新千歲機場國內線2F是伴手禮一級戰區！\n\n【機場必買 Top 10】\n1. 北菓樓 (妖精之森/夢不思議泡芙)\n2. 六花亭 (奶油葡萄夾心/草莓巧克力)\n3. ROYCE (生巧克力/洋芋片)\n4. LeTAO (雙層起司蛋糕)\n5. Snaffle's (起司舒芙蕾)\n6. Calbee+ (薯條三兄弟)\n7. 白色戀人\n8. HORI (哈密瓜果凍)\n9. Kitaichi Glass (玻璃杯)\n10. 十勝牛奶布丁", "mapUrl": "https://www.new-chitose-airport.jp/tw/floor/2f.html", "contact": "國內線 2F", "stayTime": "2.5 小時" },
          { "time": "18:40", "text": "TR893 起飛", "type": "transport", "desc": "返台", "guideText": "酷航櫃台通常在起飛前3小時開櫃，建議提早去排隊托運，因為新千歲國際線免稅店排隊結帳人潮通常非常驚人。", "mapUrl": "https://maps.app.goo.gl/NewChitoseIntl" }
      ]
    }
  ],
  "packing": [
    { "category": "Documents", "items": ["護照", "VJW QR", "機票截圖"] },
    { "category": "Clothing", "items": ["發熱衣", "防風外套", "毛帽"] },
    { "category": "Electronics", "items": ["網卡", "行動電源", "充電線"] }
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

# --- 5. 頂部導覽列 (色塊活潑化) ---
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
nav_cols = st.columns([1.2, 1, 1, 1, 1, 1, 1.2])
nav_items = [("🏠", "overview"), ("08", 0), ("09", 1), ("10", 2), ("11", 3), ("12", 4), ("🎒", "packing")]

# 導覽列 CSS
st.markdown(f"""<style>
/* 未選中狀態 */
div[data-testid="column"] button {{
    background-color: #F0EFEA !important; /* 淺色塊 */
    border: none !important;
    color: {COLORS['text_secondary']} !important;
    font-weight: 500 !important;
    border-radius: 12px !important;
    height: auto !important;
    padding: 8px 4px !important;
}}
/* 懸停狀態 - 霧玫瑰色 */
div[data-testid="column"] button:hover {{
    background-color: {COLORS['rose_mist']} !important;
    color: {COLORS['text_primary']} !important;
}}
/* 選中狀態 - 暖金沙色 */
div[data-testid="column"] button[kind="primary"] {{
    background-color: {COLORS['warm_gold']} !important; /* 深色塊 */
    color: #FFFFFF !important;
    box-shadow: 0 4px 10px rgba(140, 131, 118, 0.3) !important;
}}
</style>""", unsafe_allow_html=True)

for i, (label, view_name) in enumerate(nav_items):
    is_active = st.session_state.view == view_name
    if nav_cols[i].button(label, key=f"nav_{view_name}", type="primary" if is_active else "secondary", use_container_width=True):
        st.session_state.view = view_name
        st.rerun()

# --- 6. 渲染主畫面 ---
if st.session_state.view == 'overview': view_overview()
elif st.session_state.view == 'packing': view_packing()
elif isinstance(st.session_state.view, int): view_day(st.session_state.view)
