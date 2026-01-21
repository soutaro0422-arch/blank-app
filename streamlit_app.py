import streamlit as st
import random

# --- ページ設定 ---
st.set_page_config(
    page_title="最適ルート検索アプリ",
    page_icon="🚆",
    layout="centered"
)

# --- 関数: ルート検索の模擬ロジック ---
# 実際にはここでGoogle Maps APIなどを叩きます
def search_routes(origin, destination):
    # API連携までのプレースホルダーとして、ランダムな値を返します
    # 本番環境ではAPIからのレスポンスを整形して返してください
    base_price = random.randint(3, 15) * 100
    base_time = random.randint(15, 120)
    
    results = [
        {
            "type": "早さ優先",
            "mode": "新幹線/特急",
            "duration": f"{base_time}分",
            "cost": f"¥{base_price * 2:,}",
            "details": f"{origin}駅 -> {destination}駅 (直通)"
        },
        {
            "type": "安さ優先",
            "mode": "電車/バス",
            "duration": f"{int(base_time * 1.5)}分",
            "cost": f"¥{base_price:,}",
            "details": f"{origin}駅 -> (乗り換え1回) -> {destination}駅"
        },
        {
            "type": "快適さ優先",
            "mode": "タクシー",
            "duration": f"{int(base_time * 0.8)}分",
            "cost": f"¥{base_price * 10:,}",
            "details": "ドア・ツー・ドア"
        }
    ]
    return results

# --- UI構築 ---
st.title("🚆 スマート移動ルート検索")
st.markdown("出発地と目的地を入力すると、最適な移動手段を提案します。")

# 入力フォーム
with st.form("route_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("出発地", placeholder="例: 東京駅")
    with col2:
        destination = st.text_input("目的地", placeholder="例: 大阪駅")
    
    submitted = st.form_submit_button("検索開始")

# 結果表示
if submitted:
    if not origin or not destination:
        st.error("出発地と目的地を両方入力してください。")
    else:
        st.divider()
        st.subheader(f"📍 {origin} から {destination} へのルート")
        
        # 検索処理（模擬）を実行
        routes = search_routes(origin, destination)
        
        # 結果をカード風に表示
        for route in routes:
            with st.container():
                st.markdown(f"### {route['type']} ({route['mode']})")
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.metric("所要時間", route['duration'])
                with col_res2:
                    st.metric("料金", route['cost'])
                
                st.info(f"ルート詳細: {route['details']}")
                st.markdown("---")

# --- サイドバー（補足情報） ---
with st.sidebar:
    st.header("使い方")
    st.write("1. 出発地を入力")
    st.write("2. 目的地を入力")
    st.write("3. 検索ボタンをクリック")
    st.warning("※現在はデモモードのため、表示される時間と金額はシミュレーション値です。")
