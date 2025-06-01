# import google.generativeai as genai
from google import genai
import os
import traceback # 用於印出更詳細的錯誤資訊

print("腳本開始執行...")

# ---------------------------------------------------------------------------
# 關於 API 金鑰的重要提示：
# 1. 優先推薦使用環境變數來設定您的 API 金鑰。
# 2. 如果您暫時想直接在程式碼中測試，可以取消下面一行的註解，
#    並將 "YOUR_GOOGLE_API_KEY" 替換成您真實的金鑰。
#    測試完成後，強烈建議您將其改回從環境變數讀取或移除，
#    尤其是當您要將程式碼上傳到 Git 時，絕對不要將金鑰寫死在程式碼中！
#

# ---------------------------------------------------------------------------
TEMP_API_KEY_FOR_TESTING = "AIzaSyAYO6cbSXIu7weheEcHlGSMB4hZMxUn_o4"
try:
    print("步驟 1: 準備讀取 API 金鑰...")
    api_key = None

    # 檢查是否設定了臨時測試金鑰 (如果取消了上面 TEMP_API_KEY_FOR_TESTING 的註解)
    if 'TEMP_API_KEY_FOR_TESTING' in locals() and TEMP_API_KEY_FOR_TESTING != "YOUR_GOOGLE_API_KEY_HERE":
        print("    偵測到使用 TEMP_API_KEY_FOR_TESTING。")
        api_key = TEMP_API_KEY_FOR_TESTING
    else:
        print("    嘗試從環境變數 'GOOGLE_API_KEY' 讀取...")
        api_key = os.environ.get('GOOGLE_API_KEY')

    if not api_key:
        print("    環境變數中未找到 API 金鑰，或臨時金鑰未設定/不正確。")
        print("    現在將提示您手動輸入 API 金鑰...")
        # 下一行會等待您在終端機輸入，然後按 Enter
        api_key = input("    請輸入您的 Google API Key 並按下 Enter：")
        if api_key:
            print(f"    您輸入的 API 金鑰長度為：{len(api_key)} (此訊息僅供確認，不代表金鑰有效性)")
        else:
            print("    您沒有輸入任何內容作為 API 金鑰。")

    if not api_key:
        print("錯誤：最終未能獲取 API 金鑰。腳本無法繼續執行。")
        exit() # 終止腳本

    print(f"步驟 2: 準備使用 API 金鑰 (長度: {len(api_key)}) 設定 genai...")
    # genai.configure(api_key=api_key)
    client = genai.Client(api_key=api_key)
    print("    genai.configure 完成。")

# ... (genai.configure 完成之後) ...
    print("步驟 2.5: 列出可用的模型 (支援 'generateContent')...")
    try:
        count = 0
        # for m in genai.list_models():
        #     if 'generateContent' in m.supported_generation_methods:
        #         print(f"    - {m.name} (顯示名稱: {m.display_name})")
        #         count += 1
        for m in client.models.list():
            if "generateContent" in m.supported_actions:
                print(f"    - {m.name} (display_name: {m.display_name})")
                count += 1
        if count == 0:
            print("    在此 API 金鑰下未找到支援 'generateContent' 的模型。")
        print("    模型列表顯示完畢。\n")
    except Exception as e:
        print(f"    列出模型時發生錯誤: {e}\n")
    # ... 接下來是步驟 3 (初始化模型) ...

    print("步驟 3: 準備初始化模型 'gemini-1.5-flash-latest'...")
    # model = genai.GenerativeModel('gemini-1.5-flash-latest')
    model = "gemini-1.5-flash-latest"
    print("    模型初始化完成。")

    # prompt = "你好！請用繁體中文簡單介紹一下你自己。"
    prompt = "What are the best french cheese?"
    print(f"步驟 4: 準備向模型發送提示：'{prompt}'")

    # response = model.generate_content(prompt)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    print("步驟 5: 已從模型收到回應。")


    print("\n模型的回應：")
    if response and hasattr(response, 'text') and response.text:
        print(response.text)
    else:
        print("收到的回應無效、為空或沒有 .text 屬性。")
        print("    可能的候選答案 (Candidates):")
        if response and hasattr(response, 'candidates'):
            for candidate in response.candidates:
                print(f"        - {candidate}") # 印出每個候選答案的內容
        else:
            print("        無法獲取候選答案。")
        print("    提示回饋 (Prompt Feedback):")
        if response and hasattr(response, 'prompt_feedback'):
            print(f"        {response.prompt_feedback}")
        else:
            print("        無法獲取提示回饋。")
        # 如果需要，可以取消註解下面這行來查看完整的回應物件
        # print("    完整的原始回應物件：", response)


except Exception as e:
    print(f"\n腳本執行過程中發生錯誤：")
    print(f"錯誤類型：{type(e).__name__}")
    print(f"錯誤訊息：{e}")
    print("詳細追蹤資訊：")
    traceback.print_exc() # 這會印出詳細的錯誤堆疊
    print("\n請檢查：")
    print("1. 您的 API 金鑰是否正確且已啟用 (針對 Gemini API)。")
    print("2. 您的網路連線是否正常。")
    print("3. 是否已正確安裝 'google-generativeai' 函式庫 (pip install -q -U google-generativeai)。")
    print("4. 如果您是手動輸入 API 金鑰，請確保沒有複製到多餘的空格或字元。")
    print("參考文件：https://ai.google.dev/gemini-api/docs/quickstart/python")

finally:
    print("\n腳本執行完畢。")