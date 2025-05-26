import os
from dotenv import load_dotenv # 確保這行在最上面

# 載入 .env 檔案中的變數 (應該在所有其他 import 之前或緊隨其後立即執行)
load_dotenv() 

# ===== 新增的偵錯行 (請保留它來幫助我們確認環境變數) =====
print(f"DEBUG: .env loaded. GOOGLE_APPLICATION_CREDENTIALS = {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
# ===== 偵錯行結束 =====

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.cloud import translate_v3 as translate

# 初始化 Flask 應用程式
app = Flask(__name__, template_folder=".")
CORS(app)  # 啟用 CORS

# Google Translate 客戶端將會自動使用 GOOGLE_APPLICATION_CREDENTIALS 環境變數進行驗證
translate_client = None # 先給定一個預設值
try:
    # 檢查環境變數是否已設定 (由 .env 載入)
    google_app_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not google_app_creds:
        print("--------------------------------------------------------------------------------")
        print("嚴重錯誤：GOOGLE_APPLICATION_CREDENTIALS 環境變數未設定或為空。")
        print("請在專案根目錄下的 .env 檔案中設定此變數，使其指向您的服務帳號金鑰 JSON 檔案的「完整且正確」的路徑。")
        print("例如：GOOGLE_APPLICATION_CREDENTIALS=\"C:/path/to/your/service-account-file.json\"")
        print("--------------------------------------------------------------------------------")
        # translate_client 保持為 None
    elif not os.path.exists(google_app_creds):
        print("--------------------------------------------------------------------------------")
        print(f"嚴重錯誤：環境變數 GOOGLE_APPLICATION_CREDENTIALS 指向的檔案不存在。")
        print(f"路徑為: {google_app_creds}")
        print("請確認 .env 檔案中的路徑是否「完整且正確」，並且該 JSON 檔案確實存在於該路徑。")
        print("--------------------------------------------------------------------------------")
        # translate_client 保持為 None
    else:
        # 現在 Client() 不需要任何參數，它會自動尋找 GOOGLE_APPLICATION_CREDENTIALS
        translate_client = translate.Client()
        print("Google Translate 客戶端已透過服務帳號 (GOOGLE_APPLICATION_CREDENTIALS) 初始化。")
except Exception as e:
    print(f"初始化 Google Translate 客戶端時發生嚴重錯誤: {e}")
    # translate_client 保持為 None (或已是 None)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/translate', methods=['POST'])
def handle_translate_request():
    if not translate_client:
        return jsonify({"error": "翻譯服務未正確初始化。請檢查後端伺服器的日誌以獲取詳細資訊。"}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "請求中沒有 JSON 資料"}), 400

        text_to_translate = data.get('text')
        target_language = data.get('target_lang')
        source_language = data.get('source_lang', None)

        if not text_to_translate or not target_language:
            return jsonify({"error": "請求中缺少 'text' 或 'target_lang' 參數"}), 400

        if source_language and source_language.lower() == 'auto':
            source_language = None
            
        result = translate_client.translate(
            text_to_translate,
            target_language=target_language,
            source_language=source_language if source_language else ''
        )
        
        translated_text = result['translatedText']
        detected_source_language = result.get('detectedSourceLanguage', None)

        response_data = {
            "translated_text": translated_text
        }
        if detected_source_language:
            response_data["detected_source_language"] = detected_source_language
            
        return jsonify(response_data), 200

    except Exception as e:
        print(f"翻譯 API 呼叫時發生錯誤: {e}") # 更明確的錯誤日誌
        return jsonify({"error": f"翻譯過程中發生錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)