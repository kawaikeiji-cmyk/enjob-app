import streamlit as st

st.set_page_config(page_title="エンジョブ企業研究", layout="centered")

# 最初に開くホームと、ボタンで移動する2つの画面を登録します。
home_page = st.Page("screens/home.py", title="ホーム", default=True)
register_page = st.Page(
    "screens/register.py", title="企業を登録する", url_path="register"
)
search_page = st.Page("screens/search.py", title="企業を探す", url_path="search")

# 標準のナビゲーションを隠し、選択された画面だけを表示します。
page = st.navigation([home_page, register_page, search_page], position="hidden")
page.run()
