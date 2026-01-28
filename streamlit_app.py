import streamlit as st
import uuid
from supabase import create_client

# Supabase接続（Secretsから読む）
sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# 1行INSERTテスト（起動時に1回だけ）
if "db_test_done" not in st.session_state:
    sb.table("route_queries").insert({
        "session_id": str(uuid.uuid4()),
        "origin": "テスト出発",
        "destination": "テスト到着",
        "distance_km": 123.4,
        "result": {"ok": True},
        "error": None
    }).execute()
    st.session_state["db_test_done"] = True
    st.success("✅ Supabaseにテスト書き込みできました")

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# --- ページ設定 ---
st.set_page_config(page_title="ルート・運賃概算アプリ", page_icon="🚄")

# --- ロジック: 距離から金額と時間を推測する ---
def calculate_estimate(origin_name, destination_name):
    geolocator = Nominatim(user_agent="my_streamlit_app")
    
    try:
        # 1. 住所/駅名から緯度経度を取得
        loc_origin = geolocator.geocode(origin_name)
        loc_dest = geolocator.geocode(destination_name)
        
        if not loc_origin or not loc_dest:
            return None, "場所が見つかりませんでした。駅名や県名を含めて試してください。"

        # 2. 直線距離を計算 (km)
        coords_origin = (loc_origin.latitude, loc_origin.longitude)
        coords_dest = (loc_dest.latitude, loc_dest.longitude)
        distance_km = geodesic(coords_origin, coords_dest).km
        
        # 3. 移動手段ごとの係数設定 (あくまで概算用の目安です)
        # 新幹線: 平均時速200km, 40円/km (指定席相当) + 基本賃
        # 在来線: 平均時速60km, 15円/km
        # タクシー: 平均時速40km, 300円/km (長距離だと非現実的ですが計算として)
        
        results = [
            {
                "mode": "新幹線/特急 (推奨)",
                "price": int(distance_km * 40 + 1000),  # 距離x単価+基本料
                "minutes": int((distance_km / 200) * 60 + 20), # 距離/速度+乗り換え時間
                "desc": "スピード重視"
            },
            {
                "mode": "在来線/バス",
                "price": int(distance_km * 12 + 500),
                "minutes": int((distance_km / 50) * 60 + 40),
                "desc": "安さ重視"
            },
            {
                "mode": "タクシー/車",
                "price": int(distance_km * 350 + 700),
                "minutes": int((distance_km / 40) * 60),
                "desc": "プライベート"
            }
        ]
        
        return results, f"直線距離: 約{int(distance_km)}km"

    except Exception as e:
        return None, f"エラーが発生しました: {e}"

# --- UI構築 ---
st.title("🚄 距離ベース運賃概算アプリ")
st.caption("Google Maps APIを使わず、直線距離から一般的な相場を計算します")

with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("出発地", "熊本駅")
    with col2:
        destination = st.text_input("目的地", "大阪駅")
    
    submitted = st.form_submit_button("検索")

if submitted:
    with st.spinner("距離を計算中..."):
        # ジオコーディングAPIへの負荷を減らすため少し待機
        time.sleep(1)
        data, message = calculate_estimate(origin, destination)
    
    if data:
        st.success(f"計算完了！ ({message})")
        
        # 結果表示
        for item in data:
            with st.container():
                # カードのような見た目にする
                st.subheader(f"{item['mode']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("予想金額", f"約 ¥{item['price']:,}")
                
                # 時間の表示形式を整える (例: 150分 -> 2時間30分)
                hours = item['minutes'] // 60
                mins = item['minutes'] % 60
                time_str = f"{hours}時間{mins}分" if hours > 0 else f"{mins}分"
                
                c2.metric("所要時間", time_str)
                c3.write(item['desc'])
                st.divider()
    else:
        st.error(message)
