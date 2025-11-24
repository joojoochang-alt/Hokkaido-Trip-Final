import streamlit as st
import requests
import datetime
import google.generativeai as genai
import json
import os

# --- 1. 設定頁面與 CSS (Muji Style) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# Muji 配色定義
COLORS = {
    'bg': '#F9F8F6',       # 生成色 (Warm White)
    'surface': '#FFFFFF',  # 純白
    'line': '#E6E2DE',     # 淺灰褐線條
    'text_main': '#333333',# 墨黑
    'text_sub': '#7F7268', # 亞麻灰
    'accent': '#8E8071',   # 栗色/亞麻色
    'red': '#B94047'       # 傳統紅 (警示用)
}

# 注入 CSS
st.markdown(f"""
    <style>
    /* 引入 Google Fonts 作為備案，但主要強制使用微軟正黑體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+JP:wght@400;600;700&family=Shippori+Mincho:wght@400;500;700&display=swap');

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg']};
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%238e8071' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        
        /* 修改處：全局字體改為微軟正黑體 */
        font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
        color: {COLORS['text_main']};
    }}
    
    /* 標題強制微軟正黑體 */
    h1, h2, h3, .serif-font {{
        font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* 卡片風格 */
    .muji-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(100, 90, 80, 0.04);
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }}
    
    /* 按鈕樣式 */
    .stButton button {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        color: {COLORS['text_sub']};
        border-radius: 12px;
        font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
        font-weight: 500;
        transition: all 0.2s;
    }}
    .stButton button:hover {{
        color: {COLORS['accent']};
        border-color: {COLORS['accent']};
        background-color: #F5F4F2;
    }}
    .stButton button:focus:not(:active) {{
        color: {COLORS['surface']};
        background-color: {COLORS['accent']};
        border-color: {COLORS['accent']};
    }}

    /* 天氣 Grid */
    .info-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    .info-box {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 120px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}
    .info-label {{
        font-size: 0.65rem;
        font-weight: 700;
        color: {COLORS['text_sub']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 1px solid {COLORS['line']};
        padding-bottom: 4px;
        margin-bottom: 8px;
    }}
    .info-value {{
        font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS['text_main']};
    }}

    /* Ticket Style */
    .wallet-pass {{
        background-color: #FFFFFF;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        position: relative;
        font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
        margin-bottom: 20px;
        border: 1px solid {COLORS['line']};
    }}
    .pass-header {{
        padding: 24px;
        background-image: url("https://www.transparenttextures.com/patterns/stardust.png");
    }}
    .pass-notch-container {{
        height: 24px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #FFFFFF;
    }}
    .pass-notch-left, .pass-notch-right {{
        width: 24px;
        height: 24px;
        background-color: rgba(0,0,0,0.6);
        border-radius: 50%;
        position: absolute;
        top: 0;
        z-index: 10;
    }}
    .pass-notch-left {{ left: -12px; }}
    .pass-notch-right {{ right: -12px; }}
    .pass-dashed-line {{
        width: 85%;
        border-top: 2px dashed {COLORS['line']};
    }}
    
    div[data-testid="stExpander"] {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        border-radius: 8px;
        box-shadow: none;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 ---

if 'view' not in st.session_state: st.session_state.view = 'overview'
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing' not in st.session_state: st.session_state.packing = {}
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'show_chat' not in st.session_state: st.session_state.show_chat = False

APP_DATA = {
  "flight": { 
    "outbound": { "code": "TR892", "time": "12:30 - 17:20" }, 
    "inbound": { "code": "TR893", "time": "18:40 - 22:15" } 
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

def chat_with_gemini(user_input):
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        lower = user_input.lower()
        if "機票" in lower or "flight" in lower: return "班機是去程 TR892 (12:30)，回程 TR893 (18:40)。"
        if "天氣" in lower or "weather" in lower: return "北海道12月平均氣溫約 -2°C 至 -6°C，請務必穿著保暖。"
        if "吃" in lower or "food" in lower: return "推薦湯咖哩 (Suage+)、成吉思汗烤肉和海鮮丼！"
        return "目前為離線模式，我只能回答基本行程資訊。請設定 API Key 以啟用完整 AI 功能。"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_prompt = f"You are a helpful travel assistant for a Hokkaido trip. Itinerary: {json.dumps(APP_DATA['days'])}. Keep answers short."
        history = st.session_state.chat_history.copy()
        formatted_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in history]
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(system_prompt + "\nUser: " + user_input)
        return response.text
    except Exception as e:
        return f"AI 連線錯誤: {str(e)}"

# --- 4. 票券視窗 ---

@st.dialog("Digital Voucher")
def ticket_modal(ticket_key, title):
    existing = st.session_state.tickets.get(ticket_key, {"orderNumber": "", "url": "", "note": ""})
    if 'is_editing' not in st.session_state:
        st.session_state.is_editing = not (existing.get("orderNumber") or existing.get("url"))

    if not st.session_state.is_editing:
        st.markdown(f"""
        <div class="wallet-pass">
            <div class="pass-header">
                <div style="font-size: 10px; font-weight: bold; color: #aaa; letter-spacing: 2px;">RESERVATION</div>
                <div style="font-size: 24px; font-weight: bold; color: #333; font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;">{title}</div>  
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{existing.get('note', '')}</div>
                <div style="margin-top: 30px;">
                    <div style="font-size: 10px; font-weight: bold; color: #aaa; letter-spacing: 2px;">CONFIRMATION NO.</div>
                    <div style="font-size: 20px; font-weight: bold; font-family: monospace; color: #333;">{existing.get('orderNumber', '—')}</div>
                </div>
            </div>
            <div class="pass-notch-container">
                <div class="pass-notch-left" style="background-color: #262730;"></div>
                <div class="pass-dashed-line"></div>
                <div class="pass-notch-right" style="background-color: #262730;"></div>
            </div>
            <div style="padding: 20px; text-align: center;">
                <div style="display: inline-flex; align-items: center; gap: 5px; color: #2E7D32; font-weight: bold;">
                    <span>✅</span> <span>Ready to Use</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if existing.get('url'): st.link_button("🔗 OPEN LINK", existing['url'], use_container_width=True)
        if st.button("Edit", key="edit_btn"):
            st.session_state.is_editing = True
            st.rerun()
    else:
        st.markdown("### Edit Details")
        new_order = st.text_input("Confirmation No.", value=existing.get("orderNumber", ""))
        new_url = st.text_input("Link URL", value=existing.get("url", ""))
        new_note = st.text_area("Notes", value=existing.get("note", ""))
        if st.button("Save", type="primary", use_container_width=True):
            st.session_state.tickets[ticket_key] = {"orderNumber": new_order, "url": new_url, "note": new_note}
            st.session_state.is_editing = False
            st.rerun()

# --- 5. 頁面視圖 ---

def view_overview():
    st.markdown(f"""
    <div style='text-align:center; padding: 20px 0; border-bottom: 1px solid {COLORS['line']}'>
        <h1 style='color:{COLORS['text_main']}; font-size: 2rem; margin-bottom: 0;'>Hokkaido</h1>
        <p style='color:{COLORS['accent']}; letter-spacing: 0.2em; font-size: 0.8rem; font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;'>DECEMBER 2025</p> 
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # VJW Card (明亮棕色)
    vjw_url = "https://vjw-lp.digital.go.jp/en/"
    st.markdown(f"""
    <style>
    .vjw-card {{
        display: block; text-decoration: none;
        background: linear-gradient(135deg, #C79D6D 0%, #9C7247 100%); 
        border-radius: 16px; padding: 16px 20px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(199, 157, 109, 0.3);
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }}
    .vjw-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(199, 157, 109, 0.45); }}
    .vjw-content {{ display: flex; align-items: center; justify-content: space-between; color: white; font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif; }}
    .vjw-icon {{ font-size: 28px; margin-right: 15px; background: rgba(255,255,255,0.2); width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }}
    .vjw-text {{ flex-grow: 1; }}
    .vjw-title {{ font-size: 16px; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 2px; }}
    .vjw-subtitle {{ font-size: 12px; opacity: 0.9; font-weight: 300; }}
    .vjw-arrow {{ font-size: 18px; opacity: 0.8; }}
    .vjw-bg-pattern {{ position: absolute; top: -10px; right: -10px; font-size: 100px; opacity: 0.1; color: white; pointer-events: none; }}
    </style>
    <a href="{vjw_url}" target="_blank" class="vjw-card">
        <div class="vjw-bg-pattern">🇯🇵</div>
        <div class="vjw-content">
            <div class="vjw-icon">✈️</div>
            <div class="vjw-text"><div class="vjw-title">Visit Japan Web</div><div class="vjw-subtitle">入境審查 / 海關申報 / 免稅 QR</div></div>
            <div class="vjw-arrow">➜</div>
        </div>
    </a>
    """, unsafe_allow_html=True)
    st.write("")

    rate = get_exchange_rate()
    temp, weather = get_weather(43.06, 141.35)
    
    st.markdown(f"""
    <div class="info-grid">
        <div class="info-box">
            <div><div class="info-label">Exchange</div><div class="info-value">{int(rate*1000) if rate else '...'} <span style="font-size:0.8rem">TWD</span></div></div>
            <div style="font-size:0.7rem; color:#aaa; font-family:monospace;">¥1000 JPY</div>
        </div>
        <div class="info-box">
            <div><div class="info-label">Sapporo</div><div class="info-value">{temp}° <span style="font-size:0.8rem">{weather}</span></div></div>
            <div style="font-size:0.7rem; color:#aaa;">Today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="muji-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1rem; margin-bottom:1rem; color:{COLORS['text_main']}'>✈️ Flights</h3>", unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.caption("OUTBOUND (12/08)")
        st.markdown("**12:30** TR892")
        if st.button("Ticket (W)", key="fw_w"): ticket_modal("flight_wei", "機票 (W)")
    with f2:
        st.caption("INBOUND (12/12)")
        st.markdown("**18:40** TR893")
        if st.button("Ticket (C)", key="fi_c"): ticket_modal("flight_chien", "機票 (C)")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✨ AI Assistant", use_container_width=True): st.session_state.show_chat = not st.session_state.show_chat
    if st.session_state.show_chat: view_assistant()

    st.markdown(f"""
    <div style="margin-top: 2rem; padding: 1.5rem; background: #FFF5F5; border-radius: 12px; border: 1px solid {COLORS['red']}20;">
        <div style="color:{COLORS['red']}; font-weight:bold; font-size:0.9rem; margin-bottom:0.5rem;">🆘 EMERGENCY</div>
        <div style="display:flex; gap:1rem; font-size:0.8rem; color:{COLORS['text_sub']};"><span>110 Police</span> <span>|</span> <span>119 Ambulance</span></div>
        <div style="margin-top:10px; padding:10px; background:white; border-radius:4px; border:1px solid {COLORS['red']}10;">
            <div style="font-size:0.7rem; color:#999;">札幌辦事處 (緊急聯絡)</div><div style="font-weight:bold; color:{COLORS['text_main']};">080-1460-2568</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def view_day(day_id):
    day = APP_DATA['days'][day_id]
    
    # --- 即時天氣預報 (修正 HTML 縮排問題) ---
    lat = day['coords']['lat']
    lon = day['coords']['lon']
    temp, w_text = get_weather(lat, lon) 

    weather_icon = "🌥️"
    if "晴" in w_text: weather_icon = "☀️"
    elif "雨" in w_text: weather_icon = "🌧️"
    elif "雪" in w_text: weather_icon = "❄️"

    # 使用獨立變數並靠左對齊字串
    weather_html = f"""
<div style="text-align:center; margin-bottom: 1.5rem;">
    <h2 style="font-size: 2.5rem; margin:0; color:{COLORS['text_main']}">{day['date'].split(' ')[0]}</h2>
    <div style="color:{COLORS['text_sub']}; font-size:0.9rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom: 15px;">{day['location']}</div>
    <div style="display: inline-flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 10px 20px; border-radius: 30px; border: 1px solid {COLORS['line']}; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <span style="font-size: 1.8rem; line-height: 1;">{weather_icon}</span>
            <div style="text-align: left; line-height: 1.1;">
                <div style="font-size: 1.2rem; font-weight: bold; color: {COLORS['text_main']}">{temp}° {w_text}</div>
                <div style="font-size: 0.6rem; color: #AAA; font-weight: 700; letter-spacing: 1px;">REAL-TIME</div>
            </div>
    </div>
</div>
"""
    st.markdown(weather_html, unsafe_allow_html=True)
    # ---------------------------------------

    # Hotel
    st.markdown(f"""
    <div class="muji-card" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:0.7rem; font-weight:bold; color:{COLORS['text_sub']}; letter-spacing:0.1em; text-transform:uppercase;">Accommodation</div>
            <div style="font-weight:bold; font-size:1.1rem;">{day['hotel']}</div>
            <div style="font-size:0.8rem; color:{COLORS['text_sub']};">{day['hotel_note']}</div>
        </div>
        <div style="font-size:1.5rem; opacity:0.2;">🛏️</div>
    </div>
    """, unsafe_allow_html=True)

    # Timeline
    for i, act in enumerate(day['activities']):
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-top:1rem; margin-bottom:0.5rem;">
            <span style="font-family:monospace; font-size:0.8rem; background:{COLORS['line']}; padding:2px 6px; border-radius:4px; color:{COLORS['text_main']}">{act['time']}</span>
            <span style="font-weight:bold; color:{COLORS['text_main']}">{act['text']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"詳情 / {act['desc']}"):
            if 'guideText' in act:
                st.markdown(f"""
                <div style="background:{COLORS['bg']}; border:1px solid {COLORS['line']}; padding:12px; border-radius:8px; margin-bottom:15px;">
                    <strong style="color:{COLORS['accent']}; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;">💡 Guide Note</strong>
                    <p style="font-size:0.9rem; margin-top:5px; line-height:1.6; color:{COLORS['text_main']}; white-space: pre-wrap;">{act['guideText']}</p>
                </div>
                """, unsafe_allow_html=True)

            if act['type'] == 'food' and 'menu' in act:
                st.markdown(f"<div style='font-size:0.8rem; font-weight:bold; color:{COLORS['text_sub']}; margin-bottom:5px;'>RECOMMENDED</div>", unsafe_allow_html=True)
                for m in act['menu']: st.markdown(f"- {m}")
            
            st.write("") # Spacer

            # --- 按鈕區 (動態對齊) ---
            actions = []
            if 'mapUrl' in act:
                actions.append("map")
            if act['type'] == 'transport':
                actions.append("ticket_w")
                actions.append("ticket_c")
            
            if actions:
                cols = st.columns(len(actions))
                col_idx = 0
                
                if "map" in actions:
                    with cols[col_idx]:
                        st.link_button("📍 Google Map", act['mapUrl'], use_container_width=True)
                    col_idx += 1
                
                if "ticket_w" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (W)", key=f"t_{day_id}_{i}_w", use_container_width=True):
                            ticket_modal(f"t_{day_id}_{i}_w", f"Ticket (W) - {act['text']}")
                    col_idx += 1
                
                if "ticket_c" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (C)", key=f"t_{day_id}_{i}_c", use_container_width=True):
                            ticket_modal(f"t_{day_id}_{i}_c", f"Ticket (C) - {act['text']}")

def view_packing():
    st.header("Packing List")
    total = sum(len(c['items']) for c in APP_DATA['packing'])
    checked = sum(1 for k, v in st.session_state.packing.items() if v)
    st.progress(checked / total if total > 0 else 0)
    for cat in APP_DATA['packing']:
        with st.container(border=True):
            st.markdown(f"**{cat['category']}**")
            for item in cat['items']:
                key = f"pack_{item}"
                val = st.checkbox(item, value=st.session_state.packing.get(key, False), key=key)
                st.session_state.packing[key] = val

def view_assistant():
    st.markdown("---")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["text"])  
    if prompt := st.chat_input("Ask me about your trip..."):
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("model"):
            with st.spinner("Thinking..."):
                response = chat_with_gemini(prompt)
                st.write(response)
        st.session_state.chat_history.append({"role": "model", "text": response})

# --- 6. 頂部導覽列 ---
nav_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1.5])
nav_items = [("🏠 Home", "overview"), ("08", 0), ("09", 1), ("10", 2), ("11", 3), ("12", 4), ("🎒 List", "packing")]
for i, (label, view_name) in enumerate(nav_items):
    is_active = st.session_state.view == view_name
    if nav_cols[i].button(label, key=f"nav_{view_name}", type="primary" if is_active else "secondary", use_container_width=True):
        st.session_state.view = view_name
        st.rerun()

if st.session_state.view == 'overview': view_overview()
elif st.session_state.view == 'packing': view_packing()
elif isinstance(st.session_state.view, int): view_day(st.session_state.view)
