import streamlit as st

st.set_page_config(page_title="Quick Dialer", page_icon="📞")

st.title("📞 クイック電話発信")

# 1. URLパラメータからデフォルトの電話番号を取得
# 例: http://localhost:8501/?tel=09012345678 にアクセスすると自動入力される
query_params = st.query_params
default_tel = query_params.get("tel", "")

# 2. 電話番号入力欄（URLパラメータがあればそれが初期値になる）
phone_number = st.text_input(
    "発信先番号", 
    value=default_tel, 
    placeholder="090-0000-0000"
)

# 番号が入力されている場合のみ、即座に発信リンクを表示（ボタン押下をスキップ）
if phone_number:
    # 数字以外を除去
    clean_number = "".join(filter(str.isdigit, phone_number))
    
    if clean_number:
        st.info(f"宛先: {phone_number}")
        
        # HTMLボタンを常に表示させておくことで、「発信準備」ボタンを省略
        # これにより、ユーザーは「番号確認」→「発信リンククリック」の2ステップで済みます
        html_code = f"""
            <a href="tel:{clean_number}" target="_blank" style="
                text-decoration: none;
                display: inline-block;
                padding: 12px 24px;
                background-color: #00cc66;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
                text-align: center;
                width: 100%;
            ">
                この番号へ発信（外部アプリ起動）
            </a>
        """
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.warning("有効な数字を入力してください。")

# 使い方ガイド
with st.expander("複数人で使い分けるヒント"):
    st.write("""
    個別のリンク（ブックマーク）を作成することで、各自のデフォルト番号を固定できます。
    URLの末尾に `?tel=自分の番号` を付けてアクセスしてください。
    """)
    st.code(f"https://your-app-url.streamlit.app/?tel=090XXXXXXXX")
