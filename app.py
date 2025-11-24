import streamlit as st
import requests
import datetime
import google.generativeai as genai
import json
import os

# --- 1. 設定頁面與 CSS (Modern Japanese Earth Style) ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# 全新大地色系定義 (Modern Earth Tones)
COLORS = {
    'bg_main': '#FDFBF7',       # 極淺暖米白背景 (Warm Off-White)
    'surface': '#FFFFFF',       # 純白卡片表面
    'text_primary': '#4A4238',  # 暖深炭棕色
    'text_secondary': '#8C8376',# 暖灰褐
    'accent_warm': '#C7B299',   # 燕麥色/淺駝色
    'accent_deep': '#9C8E7E',   # 深卡其
    'terracotta': '#B07D62',    # 柔和陶土色
    'shadow_warm': 'rgba(74, 66, 56, 0.08)' # 極柔和暖陰影
}

# 注入 CSS
st.markdown(f"""
    <style>
    /* 引入現代無襯線字體 */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg_main']};
        /* 微妙的紙張紋理 */
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
        font-family: 'Montserrat', 'Noto Sans TC', sans-serif;
        color: {COLORS['text_primary']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Montserrat', 'Noto Sans TC', sans-serif !important;
        font-weight: 600 !important;
        color: {COLORS['text_primary']} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    /* 現代日式卡片 (無邊框，柔和陰影) */
    .modern-card {{
        background: {COLORS['surface']};
        border: none;
        border-radius: 24px;
        box-shadow: 0 8px 24px {COLORS['shadow_warm']}, 0 2px 8px {COLORS['shadow_warm']};
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    /* 現代按鈕樣式 */
    .stButton button {{
        background-color: {COLORS['surface']};
        border: none !important;
        color: {COLORS['text_secondary']};
        border-radius: 30px;
        padding: 8px 20px;
        font-weight: 500;
        box-shadow: 0 2px 6px {COLORS['shadow_warm']};
        transition: all 0.2s ease;
    }}
    .stButton button:hover {{
        color: {COLORS['text_primary']};
        background-color: {COLORS['bg_main']};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px {COLORS['shadow_warm']};
    }}
    .stButton button[kind="primary"] {{
        background-color: {COLORS['accent_warm']} !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(199, 178, 153, 0.4) !important;
    }}

    /* 天氣與匯率區塊 */
    .info-grid-modern {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .info-box-modern {{
        background: {COLORS['surface']};
        border-radius: 20px;
        padding: 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        height: 110px;
        box-shadow: 0 4px 16px {COLORS['shadow_warm']};
        border: none;
    }}
    .info-label-modern {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 6px;
    }}
    .info-value-modern {{
        font-family: 'Montserrat', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        line-height: 1.1;
    }}

    /* Expander 優化 */
    div[data-testid="stExpander"] {{
        background-color: transparent;
        border: none;
        box-shadow: none;
    }}
    
    /* Ticket Style */
    .wallet-pass {{
        background-color: #FFFFFF;
        border-radius: 24px;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0,0,0,0.06);
        position: relative;
        font-family: 'Montserrat', 'Noto Sans TC', sans-serif;
        margin-bottom: 20px;
        border: none;
    }}
    .pass-header {{
        padding: 28px;
        background: linear-gradient(to bottom right, #F8F4F0, #FDFBF7);
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
        background-color: rgba(0,0,0,0.5);
        border-radius: 50%;
        position: absolute;
        top: 0;
        z-index: 10;
    }}
    .pass-notch-left {{ left: -12px; }}
    .pass-notch-right {{ right: -12px; }}
    .pass-dashed-line {{
        width: 85%;
        border-top: 2px dashed {COLORS['accent_warm']};
        opacity: 0.5;
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
        return "目前為離線模式，請設定 API Key 以啟用 AI 功能。"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_prompt = f"You are a helpful travel assistant for a Hokkaido trip. Keep answers short."
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
                <div style="font-size: 10px; font-weight: bold; color: {COLORS['accent_deep']}; letter-spacing: 2px;">RESERVATION</div>
                <div style="font-size: 22px; font-weight: 700; color: {COLORS['text_primary']}; margin-top:4px;">{title}</div>  
                <div style="font-size: 12px; color: {COLORS['text_secondary']}; margin-top: 8px;">{existing.get('note', '')}</div>
                <div style="margin-top: 35px;">
                    <div style="font-size: 10px; font-weight: bold; color: {COLORS['accent_deep']}; letter-spacing: 2px;">CONFIRMATION NO.</div>
                    <div style="font-size: 24px; font-weight: 700; font-family: 'Montserrat', monospace; color: {COLORS['text_primary']}; letter-spacing: 1px;">{existing.get('orderNumber', '—')}</div>
                </div>
            </div>
            <div class="pass-notch-container">
                <div class="pass-notch-left" style="background-color: #262730;"></div>
                <div class="pass-dashed-line"></div>
                <div class="pass-notch-right" style="background-color: #262730;"></div>
            </div>
            <div style="padding: 24px; text-align: center; background: #FAFAFA;">
                <div style="display: inline-flex; align-items: center; gap: 6px; color: #6B8E23; font-weight: 600; font-size: 0.9rem;">
                    <span>✅</span> <span>Ready to Use</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if existing.get('url'): st.link_button("🔗 OPEN LINK", existing['url'], use_container_width=True)
        if st.button("Edit Voucher", key="edit_btn", use_container_width=True):
            st.session_state.is_editing = True
            st.rerun()
    else:
        st.markdown("### Edit Details")
        new_order = st.text_input("Confirmation No.", value=existing.get("orderNumber", ""))
        new_url = st.text_input("Link URL", value=existing.get("url", ""))
        new_note = st.text_area("Notes", value=existing.get("note", ""))
        if st.button("Save Changes", type="primary", use_container_width=True):
            st.session_state.tickets[ticket_key] = {"orderNumber": new_order, "url": new_url, "note": new_note}
            st.session_state.is_editing = False
            st.rerun()

# --- 5. 頁面視圖 ---

def view_overview():
    st.markdown(f"""
    <div style='text-align:center; padding: 40px 0 30px;'>
        <h1 style='font-size: 2.8rem; margin-bottom: 8px; letter-spacing: -1px;'>Hokkaido</h1>
        <p style='color:{COLORS['accent_deep']}; letter-spacing: 0.3em; font-size: 0.85rem; font-weight: 500;'>DECEMBER 2025</p> 
    </div>
    """, unsafe_allow_html=True)
    
    # VJW Card
    vjw_url = "https://vjw-lp.digital.go.jp/en/"
    st.markdown(f"""
    <style>
    .vjw-card-modern {{
        display: block; text-decoration: none;
        background: linear-gradient(135deg, {COLORS['accent_warm']} 0%, {COLORS['accent_deep']} 100%); 
        border-radius: 28px; padding: 20px 24px; margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(166, 155, 141, 0.25);
        transition: all 0.3s ease; position: relative; overflow: hidden; border: none;
    }}
    .vjw-card-modern:hover {{ transform: translateY(-3px); box-shadow: 0 15px 40px rgba(166, 155, 141, 0.35); }}
    .vjw-content-m {{ display: flex; align-items: center; justify-content: space-between; color: white; }}
    .vjw-icon-m {{ font-size: 24px; margin-right: 16px; background: rgba(255,255,255,0.25); width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; border-radius: 50%; backdrop-filter: blur(4px); }}
    .vjw-text-m {{ flex-grow: 1; }}
    .vjw-title-m {{ font-size: 18px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 4px; }}
    .vjw-subtitle-m {{ font-size: 13px; opacity: 0.95; font-weight: 400; }}
    .vjw-bg-pattern-m {{ position: absolute; top: -20%; right: 5%; font-size: 120px; opacity: 0.08; color: white; pointer-events: none; }}
    </style>
    <a href="{vjw_url}" target="_blank" class="vjw-card-modern">
        <div class="vjw-bg-pattern-m">🇯🇵</div>
        <div class="vjw-content-m">
            <div class="vjw-icon-m">✈️</div>
            <div class="vjw-text-m"><div class="vjw-title-m">Visit Japan Web</div><div class="vjw-subtitle-m">入境審查 / 海關申報 / 免稅 QR</div></div>
            <div>➜</div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    # Info Grid
    rate = get_exchange_rate()
    temp, weather = get_weather(43.06, 141.35)
    
    st.markdown(f"""
    <div class="info-grid-modern">
        <div class="info-box-modern">
            <div class="info-label-modern">JPY / TWD</div>
            <div class="info-value-modern">{rate:.4f}</div>
            <div style="font-size:0.7rem; color:{COLORS['text_secondary']}; margin-top:4px;">匯率參考</div>
        </div>
        <div class="info-box-modern">
            <div class="info-label-modern">Sapporo Now</div>
            <div class="info-value-modern">{temp}°<span style="font-size:1rem; margin-left:4px;">{weather}</span></div>
            <div style="font-size:0.7rem; color:{COLORS['text_secondary']}; margin-top:4px;">即時天氣</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Flights Card
    st.markdown(f'<div class="modern-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1.1rem; margin-bottom:1.2rem; display:flex; align-items:center; gap:8px;'>✈️ Flights</h3>", unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.caption("OUTBOUND (12/08)")
        st.markdown(f"<div style='font-size:1.2rem; font-weight:700; color:{COLORS['text_primary']}'>12:30 <span style='color:{COLORS['accent_deep']}; font-size:1rem;'>TR892</span></div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Ticket (W)", key="fw_w", use_container_width=True): ticket_modal("flight_wei", "機票 (W)")
    with f2:
        st.caption("INBOUND (12/12)")
        st.markdown(f"<div style='font-size:1.2rem; font-weight:700; color:{COLORS['text_primary']}'>18:40 <span style='color:{COLORS['accent_deep']}; font-size:1rem;'>TR893</span></div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Ticket (C)", key="fi_c", use_container_width=True): ticket_modal("flight_chien", "機票 (C)")
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Button
    st.write("")
    if st.button("✨ AI Travel Assistant", use_container_width=True, type="primary" if st.session_state.show_chat else "secondary"): 
        st.session_state.show_chat = not st.session_state.show_chat
    if st.session_state.show_chat: view_assistant()

    # Emergency Card
    st.markdown(f"""
    <div style="margin-top: 2.5rem; padding: 1.8rem; background: #FAF7F5; border-radius: 24px; box-shadow: inset 0 0 0 1px rgba(176, 125, 98, 0.1);">
        <div style="color:{COLORS['terracotta']}; font-weight:700; font-size:0.9rem; margin-bottom:0.8rem; display:flex; align-items:center; gap:6px;">🆘 EMERGENCY CONTACTS</div>
        <div style="display:flex; gap:1.5rem; font-size:0.85rem; color:{COLORS['text_primary']}; font-weight:600;">
            <span>🇯🇵 110 Police</span> <span>🚑 119 Ambulance</span>
        </div>
        <div style="margin-top:16px; padding:14px; background:white; border-radius: 16px; box-shadow: 0 4px 12px {COLORS['shadow_warm']}; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:0.8rem; color:{COLORS['text_secondary']}; font-weight:500;">札幌辦事處 (緊急聯絡)</div>
            <div style="font-weight:700; color:{COLORS['text_primary']}; font-size:1rem;">080-1460-2568</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def view_day(day_id):
    day = APP_DATA['days'][day_id]
    
    # Weather Data
    lat = day['coords']['lat']
    lon = day['coords']['lon']
    temp, w_text = get_weather(lat, lon) 

    weather_icon = "🌥️"
    if "晴" in w_text: weather_icon = "☀️"
    elif "雨" in w_text: weather_icon = "🌧️"
    elif "雪" in w_text: weather_icon = "❄️"

    # --- 修正處：移除縮排，確保 HTML 正確渲染 ---
    weather_html = f"""
<div style="text-align:center; margin-bottom: 2rem; padding-top: 20px;">
    <h2 style="font-size: 3rem; margin:0 0 8px 0; color:{COLORS['text_primary']}; letter-spacing:-1px;">{day['date'].split(' ')[0]}</h2>
    <div style="color:{COLORS['accent_deep']}; font-size:0.95rem; letter-spacing:0.2em; text-transform:uppercase; margin-bottom: 20px; font-weight:600;">{day['location']}</div>
    
    <div style="display: inline-flex; align-items: center; gap: 16px; background: {COLORS['surface']}; padding: 12px 28px; border-radius: 50px; box-shadow: 0 8px 20px {COLORS['shadow_warm']};">
            <span style="font-size: 2.2rem; line-height: 1;">{weather_icon}</span>
            <div style="text-align: left; line-height: 1.1;">
                <div style="font-size: 1.4rem; font-weight: 700; color: {COLORS['text_primary']}; font-family: 'Montserrat', sans-serif;">{temp}° <span style="font-size:1rem;">{w_text}</span></div>
                <div style="font-size: 0.65rem; color: {COLORS['accent_deep']}; font-weight: 600; letter-spacing: 1px; margin-top:2px;">LIVE FORECAST</div>
            </div>
    </div>
</div>
"""
    st.markdown(weather_html, unsafe_allow_html=True)

    # Hotel Card
    st.markdown(f"""
    <div class="modern-card" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:0.75rem; font-weight:600; color:{COLORS['accent_deep']}; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:6px;">Accommodation</div>
            <div style="font-weight:700; font-size:1.2rem; margin-bottom:4px;">{day['hotel']}</div>
            <div style="font-size:0.85rem; color:{COLORS['text_secondary']}; font-weight:500;">{day['hotel_note']}</div>
        </div>
        <div style="font-size:1.8rem; color:{COLORS['accent_warm']}; opacity:0.8; background:{COLORS['bg_main']}; width:50px; height:50px; display:flex; align-items:center; justify-content:center; border-radius:50%;">🛏️</div>
    </div>
    """, unsafe_allow_html=True)

    # Timeline
    for i, act in enumerate(day['activities']):
        st.markdown(f"""
        <div style="display:flex; align-items:baseline; gap:12px; margin-top:1.8rem; margin-bottom:0.8rem;">
            <span style="font-family:'Montserrat', monospace; font-size:0.9rem; font-weight:600; color:{COLORS['accent_deep']}">{act['time']}</span>
            <span style="font-weight:700; font-size:1.1rem; color:{COLORS['text_primary']}">{act['text']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"查看詳情 / {act['desc']}"):
            # Guide Note
            if 'guideText' in act:
                st.markdown(f"""
                <div style="background:{COLORS['bg_main']}; padding:16px; border-radius:16px; margin-bottom:16px; box-shadow: inset 0 2px 6px {COLORS['shadow_warm']};">
                    <strong style="color:{COLORS['accent_deep']}; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; display:block; margin-bottom:8px;">💡 Guide Note</strong>
                    <p style="font-size:0.95rem; line-height:1.7; color:{COLORS['text_primary']}; white-space: pre-wrap; margin:0;">{act['guideText']}</p>
                </div>
                """, unsafe_allow_html=True)

            if act['type'] == 'food' and 'menu' in act:
                st.markdown(f"<div style='font-size:0.85rem; font-weight:600; color:{COLORS['accent_deep']}; margin-bottom:8px;'>RECOMMENDED</div>", unsafe_allow_html=True)
                for m in act['menu']: st.markdown(f"<div style='margin-bottom:4px; color:{COLORS['text_primary']}; font-weight:500;'>• {m}</div>", unsafe_allow_html=True)
            
            st.write("")

            # Actions Buttons
            actions = []
            if 'mapUrl' in act: actions.append("map")
            if act['type'] == 'transport':
                actions.append("ticket_w")
                actions.append("ticket_c")
            
            if actions:
                cols = st.columns(len(actions))
                col_idx = 0
                if "map" in actions:
                    with cols[col_idx]: st.link_button("📍 Google Map", act['mapUrl'], use_container_width=True)
                    col_idx += 1
                if "ticket_w" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (W)", key=f"t_{day_id}_{i}_w", use_container_width=True): ticket_modal(f"t_{day_id}_{i}_w", f"Ticket (W) - {act['text']}")
                    col_idx += 1
                if "ticket_c" in actions:
                    with cols[col_idx]:
                        if st.button("🎫 Ticket (C)", key=f"t_{day_id}_{i}_c", use_container_width=True): ticket_modal(f"t_{day_id}_{i}_c", f"Ticket (C) - {act['text']}")

def view_packing():
    st.markdown(f"<h2 style='text-align:center; margin-bottom:1.5rem;'>Packing List</h2>", unsafe_allow_html=True)
    
    total = sum(len(c['items']) for c in APP_DATA['packing'])
    checked = sum(1 for k, v in st.session_state.packing.items() if v)
    
    st.markdown(f"""<style>
        .stProgress > div > div > div > div {{ background-color: {COLORS['accent_warm']}; }}
    </style>""", unsafe_allow_html=True)
    st.progress(checked / total if total > 0 else 0)
    
    st.write("")
    
    for cat in APP_DATA['packing']:
        with st.container():
            st.markdown(f"<div class='modern-card' style='padding: 1.2rem;'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='margin-bottom:1rem; color:{COLORS['accent_deep']};'>{cat['category']}</h4>", unsafe_allow_html=True)
            for item in cat['items']:
                key = f"pack_{item}"
                val = st.checkbox(item, value=st.session_state.packing.get(key, False), key=key)
                st.session_state.packing[key] = val
            st.markdown("</div>", unsafe_allow_html=True)

def view_assistant():
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""<style>
        .stChatMessage {{ background: {COLORS['surface']}; border-radius: 20px; box-shadow: 0 4px 12px {COLORS['shadow_warm']}; border: none; padding: 1rem; }}
        .stChatMessage[data-testid="user-message"] {{ background: {COLORS['accent_warm']}; color: white; }}
        .stChatInput textarea {{ border-radius: 20px; border: 1px solid {COLORS['accent_warm']}50; }}
    </style>""", unsafe_allow_html=True)

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
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
nav_cols = st.columns([1.2, 1, 1, 1, 1, 1, 1.2])
nav_items = [("🏠 Home", "overview"), ("08", 0), ("09", 1), ("10", 2), ("11", 3), ("12", 4), ("🎒 List", "packing")]

st.markdown(f"""<style>
div[data-testid="column"] button {{
    border-radius: 40px !important;
    padding: 6px 12px !important;
    font-size: 0.85rem !important;
    box-shadow: 0 4px 10px {COLORS['shadow_warm']} !important;
    border: none !important;
}}
</style>""", unsafe_allow_html=True)

for i, (label, view_name) in enumerate(nav_items):
    is_active = st.session_state.view == view_name
    if nav_cols[i].button(label, key=f"nav_{view_name}", type="primary" if is_active else "secondary", use_container_width=True):
        st.session_state.view = view_name
        st.rerun()

# --- 7. 渲染主畫面 ---
if st.session_state.view == 'overview': view_overview()
elif st.session_state.view == 'packing': view_packing()
elif isinstance(st.session_state.view, int): view_day(st.session_state.view)
