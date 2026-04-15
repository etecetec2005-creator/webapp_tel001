import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import io
import os
import base64

# --- セキュリティ設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()

genai.configure(api_key=api_key)

# --- 基本設定 ---
st.set_page_config(page_title="e-Photo_Pro", layout="centered")
st.title("📸 e-Photo + Speed Call")

# --- URLパラメータから電話番号を取得（個人ごとに独立） ---
# 例: URLの末尾に ?tel=09011112222 と入れると自動セットされます
query_params = st.query_params
default_tel = query_params.get("tel", "")

# --- 電話番号設定エリア（サイドバー） ---
with st.sidebar:
    st.header("⚙️ 個人専用設定")
    st.write("ここで番号を入力して「専用URLを発行」を押すと、あなた専用のリンクが作れます。")
    input_tel = st.text_input("発信先電話番号", value=default_tel)
    
    if st.button("専用URLを発行（保存の代わり）"):
        # URLパラメータを更新してリロード
        st.query_params["tel"] = input_tel
        st.success("専用URLに切り替わりました。この画面をブックマークまたはホーム画面に追加してください。")

# --- リセット機能 ---
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reset_app():
    # パラメータ以外のセッションをクリア
    for key in list(st.session_state.keys()):
        if key != "uploader_key":
            del st.session_state[key]
    st.session_state["uploader_key"] += 1
    st.rerun()

if st.button("🔄 リセット / 次の撮影へ"):
    reset_app()

# 画像アップローダー
img_file = st.file_uploader(
    "撮影または画像を選択", 
    type=["jpg", "jpeg", "png"], 
    key=f"uploader_{st.session_state['uploader_key']}",
    accept_multiple_files=False
)

if img_file:
    try:
        # ファイルサイズチェック
        file_size_mb = img_file.size / (1024 * 1024)
        raw_img = Image.open(img_file)
        img = ImageOps.exif_transpose(raw_img)
        
        # 1MB以上なら1/3にリサイズ
        original_width, original_height = img.size
        if file_size_mb >= 1.0:
            new_width, new_height = original_width // 3, original_height // 3
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width, new_height = original_width, original_height
        
        st.image(img, use_container_width=True)

        # 1. AI解析
        ai_title = "名称未設定"
        with st.spinner("AI解析中..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                prompt = "この写真の内容を分析し、20文字以内の日本語タイトルを1つ出力してください。"
                response = model.generate_content([prompt, img])
                if response and response.text:
                    ai_title = response.text.strip().replace("\n", "").replace("/", "-")
            except:
                pass

        # 2. 画像のBase64変換
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # 3. JavaScript（自動保存 ＋ 電話ボタン即時生成）
        st.success(f"解析完了: {ai_title}")
        
        auto_process_script = f"""
        <div id="action-area" style="margin-top:20px; text-align:center;">
            <div id="status" style="font-size:13px; color:gray; margin-bottom:15px;">📍 位置情報を取得中...</div>
            <div id="call-container"></div>
        </div>

        <script>
        (async function() {{
            const status = document.getElementById('status');
            const callContainer = document.getElementById('call-container');
            const phone = "{input_tel}";
            const imgBase64 = "data:image/jpeg;base64,{img_str}";
            const aiTitle = "{ai_title}";
            
            const now = new Date();
            const dateStr = now.getFullYear().toString().slice(-2) + ('0'+(now.getMonth()+1)).slice(-2) + ('0'+now.getDate()).slice(-2) + ('0'+now.getHours()).slice(-2) + ('0'+now.getMinutes()).slice(-2);

            navigator.geolocation.getCurrentPosition(async (pos) => {{
                let addr = "住所不明";
                try {{
                    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{pos.coords.latitude}}&lon=${{pos.coords.longitude}}&accept-language=ja`);
                    const data = await res.json();
                    addr = data.address ? (data.address.city || data.address.town || "") + (data.address.suburb || "") + (data.address.road || "") : "不明";
                }} catch(e) {{}}

                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = function() {{
                    canvas.width = {new_width};
                    canvas.height = {new_height};
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    
                    const fontSize = Math.floor(canvas.height / 40);
                    ctx.font = "bold " + fontSize + "px sans-serif";
                    ctx.fillStyle = "rgba(0,0,0,0.6)";
                    ctx.fillRect(10, 10, ctx.measureText(aiTitle + " " + addr).width + 20, fontSize + 20);
                    ctx.fillStyle = "white";
                    ctx.fillText(aiTitle + " " + addr, 20, 20);

                    const link = document.createElement('a');
                    link.download = dateStr + "_" + aiTitle + ".jpg";
                    link.href = canvas.toDataURL('image/jpeg', 0.85);
                    link.click();
                    
                    status.innerHTML = "✅ 保存完了。";
                    
                    if(phone) {{
                        callContainer.innerHTML = `
                            <a href="tel:${{phone}}" style="
                                display: inline-block;
                                width: 80%;
                                padding: 20px;
                                background-color: #28a745;
                                color: white;
                                text-decoration: none;
                                border-radius: 50px;
                                font-size: 20px;
                                font-weight: bold;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                            ">📞 電話をかける (${{phone}})</a>
                        `;
                    }}
                }};
                img.src = imgBase64;
            }}, (err) => {{ 
                status.innerText = "位置情報エラー";
            }}, {{ timeout: 7000 }});
        }})();
        </script>
        """
        st.components.v1.html(auto_process_script, height=200)

    except Exception as e:
        st.error(f"エラー: {e}")
else:
    st.info("カメラを起動して撮影してください。")
