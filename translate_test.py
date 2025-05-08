import os
from dotenv import load_dotenv
import requests
import json # 用於更好地格式化輸出 JSON 回應

# 1. 從環境變數讀取 API 金鑰
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("錯誤：請先設定 GOOGLE_API_KEY 環境變數。")
else:
    # 2. 要翻譯的文字和目標語言
    text_to_translate = "Hello, world!"
    target_language = "zh-TW" # 繁體中文 (台灣)
    # 您也可以嘗試其他語言代碼，例如："fr" (法文), "es" (西班牙文), "ja" (日文)

    # 3. Google Translate API v2 的端點
    translate_url = "https://translation.googleapis.com/language/translate/v2"

    # 4. 準備請求的參數
    params = {
        'key': api_key,
        'q': text_to_translate,
        'target': target_language,
        'format': 'text' # 指定輸出格式為純文字
    }

    try:
        # 5. 發送 POST 請求
        response = requests.post(translate_url, data=params)
        response.raise_for_status() # 如果請求失敗 (例如狀態碼 4xx 或 5xx)，則拋出異常

        # 6. 解析回應並印出翻譯結果
        translation_data = response.json()
        
        # 印出完整的 JSON 回應，方便除錯
        print("完整的 API 回應:")
        print(json.dumps(translation_data, indent=2, ensure_ascii=False))
        print("-" * 30)

        # 提取並印出翻譯後的文字
        translated_text = translation_data['data']['translations'][0]['translatedText']
        print(f"原文 ({text_to_translate}) 的翻譯 ({target_language}): {translated_text}")

    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")
    except KeyError:
        print("錯誤：無法從 API 回應中解析翻譯結果。請檢查 API 回應結構。")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")