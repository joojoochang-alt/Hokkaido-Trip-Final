import streamlit as st

st.set_page_config(layout="wide", page_title="Hokkaido Art Style")

# --- 核心設計：文藝暈染風 CSS ---
# 這裡面的 CSS 負責實現您的所有需求
css_artistic = """
<style>
    /* 1. 整個導覽列容器 */
    .nav-container {
        background-color: #ffffff; /* 全白背景 */
        padding: 40px 20px 20px 20px; /* 上方留多一點白，增加空氣感 */
        
        /* 2. 角落的暈染素描 (這裡是關鍵！) */
        /* 我先放一張網路上的水彩雪景圖當示意，您可以隨時換成自己喜歡的素描圖連結 */
        background-image: url('https://images.unsplash.com/photo-1516483638261-f4dbaf036963?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80');
        background-repeat: no-repeat;
        background-position: right bottom; /* 把圖放在右下角 */
        background-size: 200px; /* 設定圖片大小 */
        
        /* 讓內容排版整齊 */
        display: flex;
        align-items: center;
        border-bottom: 1px solid #f0f0f0; /* 非常淡的分隔線，幾乎看不見 */
    }

    /* 3. 選項文字樣式 */
    .nav-item {
        color: #4a4a4a; /* 深灰質感文字 */
        text-decoration: none; /* 移除底線 */
        margin-right: 40px; /* 選項之間的距離寬一點，更有呼吸感 */
        font-family: 'Microsoft JhengHei', sans-serif; /* 微軟正黑體 */
        font-size: 18px;
        letter-spacing: 2px; /* 字距拉開，顯得優雅 */
        transition: opacity 0.5s ease; /* 設定半透明的過渡動畫時間 */
        border: none !important; /* 強制移除所有框線 */
    }

    /* 4. 滑鼠滑過的效果 (半透明) */
    .nav-item:hover {
        opacity: 0.4; /* 變成 40% 不透明度 (半透明 ghost effect) */
        color: #4a4a4a; /* 顏色不變，只變透明度 */
    }

    /* 目前所在的頁面狀態 */
    .active {
        font-weight: bold;
        opacity: 1.0 !important; /* 當前頁面保持不透明 */
    }
</style>
"""

# 渲染 CSS
st.markdown(css_artistic, unsafe_allow_html=True)

# --- 渲染 HTML 結構 ---
html_content = """
<div class="nav-container">
    <div style="flex-grow: 1;"> <a href="#" class="nav-item active">雪國首頁</a>
        <a href="#" class="nav-item">冬日氣象</a>
        <a href="#" class="nav-item">旅費預算</a>
        <a href="#" class="nav-item">私房地圖</a>
    </div>
</div>
"""

st.markdown(html_content, unsafe_allow_html=True)

# --- 頁面內容示意 ---
st.write("")
st.write("")
st.markdown("### 🌨️ Winter in Hokkaido")
st.write("這是您的文藝風介面預覽。注意看右下角的暈染圖，以及滑鼠滑過文字時的優雅半透明效果。")
