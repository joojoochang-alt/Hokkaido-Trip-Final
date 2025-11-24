import streamlit as st
import requests
import datetime
import google.generativeai as genai
import json
import os

# --- 1. 設定頁面與 CSS ---
st.set_page_config(page_title="Hokkaido Trip Dec 2025", layout="centered", page_icon="❄️")

# 定義配色 (對應 Tailwind 設定)
COLORS = {
    'bg': '#FDFCF8',
    'beige': '#EBE5D9',
    'accent': '#C4A484',
    'dark': '#464646',
    'line': '#D4D1C9',
    'red': '#B94047',
    'stone': '#F5F5F4'
}

# 注入 CSS (包含 Apple Wallet 風格與字型)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+JP:wght@400;700&family=Shippori+Mincho:wght@400;600;800&display=swap');

    /* 全局設定 */
    .stApp {{
        background-color: {COLORS['bg']};
        background-image: url("https://www.transparenttextures.com/patterns/stardust.png");
        font-family: 'Noto Sans TC', sans-serif;
        color: {COLORS['dark']};
    }}
    
    h1, h2, h3, .serif-font {{
        font-family: 'Shippori Mincho', 'Noto Serif JP', serif !important;
    }}

    /* 隱藏預設元素 */
    #MainMenu, footer, header {{visibility: hidden;}}

    /* 卡片風格 */
    .line-card {{
        background: #FFFFFF;
        border: 1px solid {COLORS['beige']};
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        padding: 1.25rem;
        margin-bottom: 1rem;
    }}
    
    /* 自訂按鈕 (模擬 React 版導覽列) */
    .nav-btn {{
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        margin: 0 2px;
    }}
    
    /* Apple Wallet Ticket Style (CSS 模擬) */
    .wallet-pass {{
        background-color: #FFFFFF;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        position: relative;
        font-family: sans-serif;
        margin-bottom: 20px;
    }}
    .pass-header {{
        padding: 20px;
        background-image: url("https://www.transparenttextures.com/patterns/stardust.png");
    }}
    .pass-notch-container {{
        height: 30px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .pass-notch-left, .pass-notch-right {{
        width: 30px;
        height: 30px;
        background-color: #262730; /* Streamlit Dark BG match or Modal BG */
        border-radius: 50%;
        position: absolute;
        top: 0;
    }}
    .pass-notch-left {{ left: -15px; }}
    .pass-notch-right {{ right: -15px; }}
    .pass-dashed-line {{
        width: 85%;
        border-top: 2px dashed #e5e5e5;
    }}
    .pass-footer {{
        padding: 20px;
        text-align: center;
        background-color: #FFFFFF;
    }}
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }}
    
    /* Streamlit 特定調整 */
    div[data-testid="stExpander"] {{
        background-color: white;
        border: 1px solid {COLORS['beige']};
        border-radius: 8px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料與狀態管理 ---

# 初始化 Session State
if 'view' not in st.session_state: st.session_state.view = 'overview'
if 'tickets' not in st.session_state: st.session_state.tickets = {}
if 'packing' not in st.session_state: st.session_state.packing = {}
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'show_chat' not in st.session_state: st.session_state.show_chat = False

# 資料常數 (從 constants.ts 轉換)
APP_DATA = {
    "flight": { 
        "outbound": { "code": "TR892", "time": "12:30 - 17:20" }, 
        "inbound": { "code": "TR893", "time": "18:40 - 22:15" } 
    },
    "days": [
        { 
            "id": 0, "date": "12/08 (一)", "location": "Sapporo", "coords": {"lat": 43.0618, "lon": 141.3545}, 
            "hotel": "JR-EAST METS", "hotel_note": "札幌站北口", 
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
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&hourly=temperature_2m,weather_code&timezone=Asia%2FTokyo"
        res = requests.get(url, timeout=3).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        # 簡單天氣代碼
        w_text = "陰"
        if code == 0: w_text = "晴"
        elif code in [1,2,3]: w_text = "多雲"
        elif code in [61,63,65,80,81,82]: w_text = "雨"
        elif code in [71,73,75,85,86]: w_text = "雪"
        
        # 24h 預報資料 (取每3小時)
        hourly = []
        now_h = datetime.datetime.now().hour
        for i in range(0, 24, 3):
            if 'hourly' in res and 'temperature_2m' in res['hourly']:
                t = res['hourly']['temperature_2m'][i]
                h_time = (now_h + i) % 24
                hourly.append((h_time, t))
            
        return temp, w_text, hourly
    except:
        return None, None, []

def get_exchange_rate():
    try:
        url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.json"
        res = requests.get(url, timeout=3).json()
        rate = res['jpy']['twd']
        return rate
    except:
        return None

# Gemini AI (使用 Streamlit Secrets 獲取 API Key)
def chat_with_gemini(user_input):
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "請先在 Streamlit Secrets 設定 GOOGLE_API_KEY"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = f"""
    You are a helpful travel assistant for a Hokkaido trip in December 2025.
    Here is the itinerary: {json.dumps(APP_DATA['days'])}
    Answer shortly and helpfully.
    """
    
    # 簡單的對話紀錄
    history = st.session_state.chat_history.copy()
    # 轉為 Gemini 格式
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        formatted_history.append({"role": role, "parts": [msg["text"]]})

    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(user_input)
    return response.text

# --- 4. 票券視窗 (st.dialog) ---
@st.dialog("Digital Voucher")
def ticket_modal(ticket_key, title):
    # 讀取現有資料
    existing = st.session_state.tickets.get(ticket_key, {"orderNumber": "", "url": "", "note": ""})
    
    # UI 狀態：是否在編輯模式 (預設無資料時編輯)
    if 'is_editing' not in st.session_state:
        st.session_state.is_editing = not (existing.get("orderNumber") or existing.get("url"))

    if not st.session_state.is_editing:
        # --- 檢視模式 (Apple Wallet 風格) ---
        
        # 使用 HTML 繪製票卡外觀
        st.markdown(f"""
        <div class="wallet-pass">
            <div class="pass-header">
                <div style="font-size: 10px; font-weight: bold; color: #aaa; letter-spacing: 2px;">RESERVATION</div>
                <div style="font-size: 24px; font-weight: bold; color: #333; font-family: 'Shippori Mincho', serif;">{title}</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{existing.get('note', '')}</div>
                
                <div style="margin-top: 30px;">
                    <div style="font-size: 10px; font-weight: bold; color: #aaa; letter-spacing: 2px;">CONFIRMATION NO.</div>
                    <div style="font-size: 20px; font-weight: bold; font-family: monospace; color: #333;">
                        {existing.get('orderNumber', '—')}
                    </div>
                </div>
            </div>
            
            <!-- 缺口裝飾 -->
            <div class="pass-notch-container">
                <div class="pass-notch-left"></div>
                <div class="pass-dashed-line"></div>
                <div class="pass-notch-right"></div>
            </div>
            
            <div class="pass-footer">
                <div class="status-badge">
                    <span>✅</span> <span>Digital Voucher Ready</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if existing.get('url'):
            st.link_button("🔗 OPEN LINK", existing['url'], use_container_width=True)
        
        if st.button("Edit Ticket", key="edit_btn"):
            st.session_state.is_editing = True
            st.rerun()
            
    else:
        # --- 編輯模式 ---
        st.markdown("### Edit Ticket Details")
        new_order = st.text_input("Confirmation No.", value=existing.get("orderNumber", ""))
        new_url = st.text_input("Link URL", value=existing.get("url", ""))
        new_note = st.text_area("Notes", value=existing.get("note", ""))
        
        if st.button("Save Ticket", type="primary", use_container_width=True):
            st.session_state.tickets[ticket_key] = {
                "orderNumber": new_order,
                "url": new_url,
                "note": new_note
            }
            st.session_state.is_editing = False
            st.rerun()

# --- 5. 畫面視圖 ---

def view_overview():
    # Header
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h1>Hokkaido 2025</h1><p style='color:#C4A484; letter-spacing: 2px; font-size: 0.8rem;'>DEC 08 — DEC 12</p></div>", unsafe_allow_html=True)
    
    # VJW Link
    st.link_button("🏛️ Visit Japan Web (入境必填)", "https://vjw-lp.digital.go.jp/en/", type="primary", use_container_width=True)
    
    st.write("") # Spacer

    # 匯率與天氣
    rate = get_exchange_rate()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="line-card" style="text-align:center;">
            <div style="font-size:0.7rem; color:#aaa; font-weight:bold;">JPY / TWD</div>
            <div style="font-weight:bold; font-size: 1.2rem;">{f'{rate:.4f}' if rate else '--'}</div>
            <div style="font-size:0.7rem; color:#888; font-family:monospace;">1000円 ≈ {int(rate*1000) if rate else '--'}元</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 簡單顯示札幌天氣
        temp, weather, _ = get_weather(43.06, 141.35)
        st.markdown(f"""
        <div class="line-card" style="text-align:center;">
            <div style="font-size:0.7rem; color:#aaa; font-weight:bold;">SAPPORO</div>
            <div style="font-weight:bold; font-size: 1.2rem;">{f'{temp}°' if temp else '--'}</div>
            <div style="font-size:0.7rem; color:#888;">{weather if weather else '--'}</div>
        </div>
        """, unsafe_allow_html=True)

    # 航班資訊
    st.markdown('<div class="line-card">', unsafe_allow_html=True)
    st.markdown("### ✈️ 航班資訊")
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.caption("去程 TR892")
        st.markdown("**12:30**")
    with f_c2:
        st.caption("回程 TR893")
        st.markdown("**18:40**")
    
    st.divider()
    
    b1, b2 = st.columns(2)
    if b1.button("機票 (W)", use_container_width=True):
        ticket_modal("flight_wei", "機票 (W)")
    if b2.button("機票 (C)", use_container_width=True):
        ticket_modal("flight_chien", "機票 (C)")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # AI 助理入口
    if st.button("✨ Ask AI Assistant", use_container_width=True):
        st.session_state.show_chat = not st.session_state.show_chat

    if st.session_state.show_chat:
        view_assistant()

    # 緊急求助 (最下方)
    st.markdown(f"""
    <div class="line-card" style="border-left: 4px solid {COLORS['red']}; background-color: #FEF2F2;">
        <h3 style="color:{COLORS['red']}; font-size: 1rem; margin-bottom: 0.5rem;">🆘 緊急求助</h3>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span>報警 110 / 救護 119</span>
        </div>
        <div style="margin-top:10px; padding:10px; background:white; border-radius:4px;">
            <div style="font-size:0.7rem; color:#999;">札幌辦事處 (台人專用)</div>
            <div style="font-weight:bold;">080-1460-2568</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def view_day(day_id):
    day = APP_DATA['days'][day_id]
    
    # Header
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0;">
        <h2 style="margin:0;">{day['date'].split()[0]}</h2>
        <p style="color:#999; font-size:0.9rem;">📍 {day['location']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Hotel
    st.markdown(f"""
    <div class="line-card" style="border-left: 4px solid {COLORS['accent']}; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-weight:bold;">{day['hotel']}</div>
            <div style="font-size:0.8rem; color:#888;">{day['hotel_note']}</div>
        </div>
        <div style="font-size:1.5rem;">🛏️</div>
    </div>
    """, unsafe_allow_html=True)

    # Activities
    for i, act in enumerate(day['activities']):
        # Timeline visual
        st.markdown(f"""
        <div style="display:flex; gap:10px; align-items:baseline; margin-bottom:5px;">
            <span style="font-family:monospace; color:#aaa; font-size:0.8rem;">{act['time']}</span>
            <span style="font-weight:bold;">{act['text']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"詳細資訊 ({act['desc']})"):
            # 導遊短評
            if 'guideText' in act:
                st.markdown(f"""
                <div style="background-color:{COLORS['stone']}; padding:10px; border-radius:8px; margin-bottom:10px;">
                    <strong style="color:{COLORS['accent']}; font-size:0.8rem;">💡 隨身導遊</strong>
                    <p style="font-size:0.9rem; margin:5px 0 0 0; white-space: pre-wrap;">{act['guideText']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 餐廳菜單
            if act['type'] == 'food' and 'menu' in act:
                st.markdown("**🍽️ 推薦菜單**")
                for m in act['menu']:
                    st.markdown(f"- {m}")
            
            # 連結與資訊
            c1, c2 = st.columns(2)
            if 'mapUrl' in act:
                c1.link_button("📍 Google Map", act['mapUrl'], use_container_width=True)
            if 'contact' in act:
                c2.caption(f"📞 {act['contact']}")
            
            # 交通票券
            if act['type'] == 'transport':
                t1, t2 = st.columns(2)
                if t1.button("車票 (W)", key=f"t_{day_id}_{i}_w"):
                    ticket_modal(f"t_{day_id}_{i}_w", f"車票 (W) - {act['text']}")
                if t2.button("車票 (C)", key=f"t_{day_id}_{i}_c"):
                    ticket_modal(f"t_{day_id}_{i}_c", f"車票 (C) - {act['text']}")

def view_packing():
    st.markdown("## 🎒 行李清單")
    
    # 進度條
    total_items = sum(len(c['items']) for c in APP_DATA['packing'])
    checked_count = sum(1 for k, v in st.session_state.packing.items() if v)
    progress = checked_count / total_items if total_items > 0 else 0
    st.progress(progress)
    
    for cat in APP_DATA['packing']:
        with st.container(border=True):
            st.markdown(f"**{cat['category']}**")
            for item in cat['items']:
                key = f"pack_{item}"
                checked = st.checkbox(item, value=st.session_state.packing.get(key, False), key=key)
                st.session_state.packing[key] = checked

def view_assistant():
    st.markdown("---")
    st.markdown("### 🤖 Travel Assistant")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])
            
    if prompt := st.chat_input("Ask about the trip..."):
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("model"):
            with st.spinner("Thinking..."):
                response = chat_with_gemini(prompt)
                st.write(response)
        st.session_state.chat_history.append({"role": "model", "text": response})

# --- 6. 頂部導覽列 (Top Navigation) ---
st.markdown('<div style="position:sticky; top:0; background:white; z-index:999; padding-bottom:10px; border-bottom:1px solid #eee;">', unsafe_allow_html=True)
cols = st.columns([1.2, 0.8, 0.8, 0.8, 0.8, 0.8, 1.2])

def nav_btn(col, label, view_name, is_active):
    style = "primary" if is_active else "secondary"
    if col.button(label, key=f"nav_{view_name}", type=style, use_container_width=True):
        st.session_state.view = view_name
        st.rerun()

nav_btn(cols[0], "🏠 總覽", "overview", st.session_state.view == "overview")
nav_btn(cols[1], "08", 0, st.session_state.view == 0)
nav_btn(cols[2], "09", 1, st.session_state.view == 1)
nav_btn(cols[3], "10", 2, st.session_state.view == 2)
nav_btn(cols[4], "11", 3, st.session_state.view == 3)
nav_btn(cols[5], "12", 4, st.session_state.view == 4)
nav_btn(cols[6], "🎒 清單", "packing", st.session_state.view == "packing")
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. 主畫面渲染 ---
if st.session_state.view == 'overview':
    view_overview()
elif st.session_state.view == 'packing':
    view_packing()
elif isinstance(st.session_state.view, int):
    view_day(st.session_state.view)