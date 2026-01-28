import streamlit as st
import uuid
import time
from supabase import create_client
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# --- ページ設定 ---
st.set_page_config(page_title="ルート・運賃概算アプリ", page_icon="🚄")

# --- Supabase接続（Secretsから読む） ---
sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- セッションID（ユーザーごとに固定） ---
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# --- ロジック: 距離から金額と時間を推測する ---
def calculate_estimate(origin_name: str, destination_name: str):
    geolocator = Nominatim(user_agent="my_streamlit_app")

    try:
        loc_origin = geolocator.geocode(origin_name)
        loc_dest = geolocator.geocode(destination_name)

        if not loc_origin or not loc_dest:
            return None, None, "場所が見つかりませんでした。駅名や県名を含めて試してください。"

        coords_origin = (loc_origin.latitude, loc_origin.longitude)
        coords_dest = (loc_dest.latitude, loc_dest.longitude)
        distance_km = geodesic(coords_origin, coords_dest).km

        results = [
            {
                "mode": "新幹線/特急 (推奨)",
                "price": int(distance_km * 40 + 1000),
                "minutes": int((distance_km / 200) * 60 + 20),
                "desc": "スピード重視",
            },
            {
                "mode": "在来線/バス",
                "price": int(distance_km * 12 + 500),
                "minutes": int((distance_km / 50) * 60 + 40),
                "desc": "安さ重視",
            },
            {
                "mode": "タクシー/車",
                "price": int(distance_km * 350 + 700),
                "minutes": int((distance_km / 40) * 60),
                "desc": "プライベート",
            },
        ]

        message = f"直線距離: 約{int(distance_km)}km"
        return results, float(distance_km), message

    except Exception as e:
        return None, None, f"エラーが発生しました: {e}"

# --- UI ---
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
        time.sleep(1)
        data, distance_km, message = calculate_estimate(origin, destination)

    # --- Supabaseに検索ログ保存（成功/失敗どちらも保存） ---
    try:
        sb.table("route_queries").insert({
            "session_id": st.session_state["session_id"],
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "result": {"message": message, "data": data} if data else None,
            "error": None if data else message,
        }).execute()
    except Exception as e:
        st.warning(f"DB保存に失敗: {e}")

    # --- 結果表示 ---
    if data:
        st.success(f"計算完了！ ({message})")

        for item in data:
            st.subheader(item["mode"])
            c1, c2, c3 = st.columns(3)
            c1.metric("予想金額", f"約 ¥{item['price']:,}")

            hours = item["minutes"] // 60
            mins = item["minutes"] % 60
            time_str = f"{hours}時間{mins}分" if hours > 0 else f"{mins}分"

            c2.metric("所要時間", time_str)
            c3.write(item["desc"])
            st.divider()
    else:
        st.error(message)
