import os
from dotenv import load_dotenv # 確保這行在最上面

# 載入 .env 檔案中的變數 (應該在所有其他 import 之前或緊隨其後立即執行)
load_dotenv() 

# ===== 新增的偵錯行 (請保留它來幫助我們確認環境變數) =====
print(f"DEBUG: .env loaded. GOOGLE_APPLICATION_CREDENTIALS = {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
# ===== 偵錯行結束 =====

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
# from google.cloud import translate_v3 as translate
from googletrans import Translator
import asyncio

# 初始化 Flask 應用程式
app = Flask(__name__, template_folder="./templates", static_folder="./static")
CORS(app)  # 啟用 CORS


async def translate(text, src_lang, dest_lang):
    async with Translator() as translator:
        result = await translator.translate(text, src=src_lang, dest=dest_lang)
        return result


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html",
                           logo="static/images/logo.png",
                           frank_image="static/images/frank.png",
                           xavier_image="static/images/xavier.png")


@app.route('/translate', methods=['POST'])
def handle_translate_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "請求中沒有 JSON 資料"}), 400

        text_to_translate = data.get('text')
        target_language = data.get('target_lang')
        source_language = data.get('source_lang', None)

        if not text_to_translate or not target_language:
            return jsonify({"error": "請求中缺少 'text' 或 'target_lang' 參數"}), 400

        result = asyncio.run(translate(text_to_translate, source_language, target_language))
        translated_text = result.text
        detected_source_language = result.src

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