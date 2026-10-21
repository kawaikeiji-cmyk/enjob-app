import streamlit as st

st.title("エンジョブ企業研究")
st.header("ホーム")

# ホームのボタンを、スマートフォンでも押しやすい高さにします。
st.html("<style>.st-key-home_actions button { min-height: 4rem; }</style>")

with st.container(key="home_actions"):
    if st.button("企業を探す", type="primary", width="stretch"):
        st.switch_page("screens/search.py")

    if st.button("企業を登録する", type="primary", width="stretch"):
        st.switch_page("screens/register.py")
