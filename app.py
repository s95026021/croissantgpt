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
from mistralai import Mistral
from google import genai
import markdown
import asyncio

# 初始化 Flask 應用程式
app = Flask(__name__, template_folder="./templates", static_folder="./static")
# CORS(app)  # 啟用 CORS

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
mistral_model = "mistral-large-latest"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def translate(text, src_lang, dest_lang):
    async with Translator() as translator:
        result = await translator.translate(text, src=src_lang, dest=dest_lang)
        return result


def get_gemini_req(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-1.5-flash-latest"
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    print(response)
    if response and hasattr(response, "text") and response.text:
        return response.text


def get_mistral_req(prompt):
    client = Mistral(api_key=MISTRAL_API_KEY)

    chat_response = client.chat.complete(
        model = mistral_model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    return chat_response.choices[0].message.content


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


@app.route("/mistralai", methods=["POST"])
def handle_mistralai():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "請求中沒有 JSON 資料"}), 400
        question = data["prompt"]
        if question not in ("sanxia-tour", "customs"):
            return jsonify({"error": "question must be one of 'sanxia-tour' or 'customs'"})
        if question == "sanxia-tour":
            prompt = """
        Tu es un Taïwanais qui habite dans le district de Sanxia.
        Tu dois conseiller un touriste étranger qui souhaite visiter.
        Tu dois lui donner 5 choses à voir sous la forme d'une liste.
        Pas d'introduction, uniquement ces 5 points.""".strip()
        elif question == "customs":
            prompt = """
        Tu es un Taïwanais qui connait très bien la culture taïwanaise.
        Tu dois donner 5 coutumes et traditions taïwanaises, et les expliquer en quelques phrases.
        Pas d'introduction, uniquement les points principaux."""
        return jsonify(markdown.markdown(get_mistral_req(prompt)), 200)
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": f"API error: {str(e)}"}), 500


@app.route("/geminiai", methods=["POST"])
def handle_geminiai():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "請求中沒有 JSON 資料"}), 400
    
        question = data["prompt"]
        if question not in ("sanxia-tour", "customs"):
            return jsonify({"error": "question must be one of 'sanxia-tour' or 'customs'"})
    
        lang = data["language"] if data["language"] in ("en", "zh") else "zh"
        if lang == "en":
            prompt_sanxia = """
            You are a Taiwanese living in the Sanxia District.
            You have to advise a foreign tourist who wants to visit.
            You have to give them 5 things to see in the form of a list.
            No introduction, just these 5 points.""".strip()
            prompt_customs = """
            You are a Taiwanese person who is very familiar with Taiwanese culture.
            You must list five Taiwanese customs and traditions, and explain them in 3 or 4 phrases.
            No introduction, just the main points.""".strip()
        elif lang == "zh":
            prompt_sanxia = """
            你是住在三峽區的台灣人。
            你需要給一位想去三峽的外國遊客提出建議。
            你需要列出五個值得一看的地方。
            無需介紹，就這五點。""".strip()
            prompt_customs = """
            你是一位非常熟悉台灣文化的台灣人。
            你必須列舉五種台灣的風俗習慣，並用幾句話來解釋。
            無需介紹，只需概述要點。""".strip()

        if question == "sanxia-tour":
            return jsonify(markdown.markdown(get_gemini_req(prompt_sanxia)), 200)
        elif question == "customs":
            return jsonify(markdown.markdown(get_gemini_req(prompt_customs)), 200)

    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": f"API error: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)