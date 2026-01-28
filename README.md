# 🚄 距離ベース運賃・所要時間 概算アプリ（Streamlit × Supabase）

出発地と目的地（駅名など）を入力すると、**直線距離**をもとに「新幹線/特急」「在来線/バス」「タクシー/車」の **運賃と所要時間を概算**して表示するWebアプリです。  
さらに、検索履歴を **Supabase（PostgreSQL）に永続保存**し、アプリ内で **直近10件の履歴**を確認できます。

---

## 🔗 アプリURL（試用はこちら）

- https://blank-app-om9q62hnmgi.streamlit.app/

---

## ✅ 主な機能

- **ルート概算（直線距離ベース）**
  - 出発地・目的地を入力（例：熊本駅 → 大阪駅）
  - ジオコーディング（地名→緯度経度）を行い直線距離を計算
  - 距離に応じた係数で概算し、以下の3パターンを表示
    - 新幹線/特急（推奨）
    - 在来線/バス
    - タクシー/車

- **検索ログをSupabaseに永続保存**
  - 入力（origin / destination）
  - 距離（distance_km）
  - 結果（result: JSON）
  - エラー（error: 失敗理由）
  - session_id（ユーザーセッション識別）

- **直近の検索履歴（10件）表示**
  - Supabaseから取得し、アプリ下部に表示

---

## 🛠️ 使用技術

- Streamlit（UI）
- geopy（Nominatim / geodesic）
- Supabase（PostgreSQL / 永続化）
- pandas（履歴の表表示）

---

## ▶️ ローカル実行手順（任意）

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
