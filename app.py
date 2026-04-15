import streamlit as st

st.set_page_config(page_title="Quick Dialer Pro", page_icon="📞")

st.title("📞 クイック電話発信")

# 1. 現在のURLパラメータを取得
current_params = st.query_params
default_tel = current_params.get("tel", "")

# 2. 電話番号入力欄
# on_changeを使って、入力が確定した瞬間にURLを書き換える
def update_url():
    new_tel = st.session_state.phone_input
    # URLの末尾を ?tel=入力番号 に書き換え
    st.query_params["tel"] = new_tel

phone_number = st.text_input(
    "発信先番号を入力（URLに自動保存されます）", 
    value=default_tel, 
    key="phone_input",
    on_change=update_url,
    placeholder="09012345678"
)

# 3. 発信リンクの表示
if phone_number:
    # 数字のみ抽出
    clean_number = "".join(filter(str.isdigit, phone_number))
    
    if clean_number:
        st.write(f"---")
        # 目立つ大きなボタンリンク
        html_code = f"""
            <a href="tel:{clean_number}" style="
                text-decoration: none;
                display: block;
                padding: 20px;
                background-color: #007bff;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 24px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                📞 {phone_number} へ発信
            </a>
        """
        st.markdown(html_code, unsafe_allow_html=True)
        
        st.success("現在のURLをブックマークすると、この番号がデフォルトになります。")
    else:
        st.warning("有効な数字を入力してください。")

# 共有用リンクの表示
if phone_number:
    current_url = st.secrets.get("BASE_URL", "http://localhost:8501") # 本番環境では自身のURLに
    st.info(f"この番号専用のリンク: `{current_url}/?tel={phone_number}`")
