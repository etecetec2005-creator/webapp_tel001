import streamlit as st
import re

st.title("📞 電話発信アプリ")

# 電話番号の入力欄
# ローカルの電話番号（日本の場合は0から始まる番号）を想定
phone_number = st.text_input("発信先の電話番号を入力してください", placeholder="09012345678")

# 番号のクレンジング（ハイフンなどを除去）
clean_number = re.sub(r'\D', '', phone_number)

if st.button("発信準備"):
    if clean_number:
        # tel: スキームを利用したHTMLリンクを作成
        # st.markdownのunsafe_allow_htmlを使用して、ブラウザの電話機能を呼び出す
        st.success(f"番号 {phone_number} を確認しました。")
        
        # HTMLでボタン風のリンクを作成（直接Pythonから発信はできないため、ユーザーにクリックさせる）
        tel_link = f'<a href="tel:{clean_number}" style="display: inline-block; padding: 0.5em 1em; color: white; background-color: #25D366; text-decoration: none; border-radius: 5px;">📞 {phone_number} に発信</a>'
        st.markdown(tel_link, unsafe_allow_html=True)
        
        st.info("上のボタンをクリックすると、デバイスの電話アプリが起動します。")
    else:
        st.error("有効な電話番号を入力してください。")

# 補足説明
st.divider()
st.caption("※このアプリはブラウザの `tel:` リンク機能を使用しています。実際に電話をかけるには、実行しているデバイスに電話機能（SIMカードやIP電話ソフト）が必要です。")
