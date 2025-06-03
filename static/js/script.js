document.addEventListener('DOMContentLoaded', function () {
    const languageSelectionArea = document.getElementById('language-selection-area');
    const mainFeaturesArea = document.getElementById('main-features-area');
    const assistantContentOutput = document.getElementById('assistant-content-output');
    const assistantTitle = document.getElementById('assistant-title');

    const langButtons = document.querySelectorAll('.lang-btn');
    const featureButtons = document.querySelectorAll('.feature-btn');

    // --- Helper function for adjusting textarea height ---
    function adjustTextareaHeight(textareaElement) {
        if (textareaElement) {
            textareaElement.style.height = 'auto'; // Reset height to shrink if text is deleted
            textareaElement.style.height = (textareaElement.scrollHeight) + 'px';
        }
    }

    // --- Main function to handle translation requests ---
    async function handleTranslationRequest() {
        console.log("handleTranslationRequest 函數已呼叫。");

        const textToTranslateElement = document.getElementById('translate-input');
        const sourceLanguageElement = document.getElementById('source-language');
        const targetLanguageElement = document.getElementById('target-language');
        const translateOutputElement = document.getElementById('translate-output');
        const loaderElement = document.getElementById('loader');
        const submitTranslateButton = document.getElementById('submit-translate'); // Get the button

        const textToTranslate = textToTranslateElement.value;
        const sourceLanguage = sourceLanguageElement.value;
        const targetLanguage = targetLanguageElement.value;

        const currentUiLang = localStorage.getItem('croissantGPT_selectedLang') || 'zh';
        let errorMsg = "請輸入要翻譯的文字。";
        // let translatingMsg = "翻譯中..."; // Loader will replace this text

        if (currentUiLang === 'en') {
            errorMsg = "Please enter text to translate.";
        } else if (currentUiLang === 'fr') {
            errorMsg = "Veuillez entrer le texte à traduire.";
        }

        if (!textToTranslate.trim()) {
            console.log("錯誤：沒有輸入要翻譯的文字。");
            if (translateOutputElement) {
                translateOutputElement.textContent = errorMsg;
                translateOutputElement.style.color = 'red';
            }
            return;
        }

        console.log(`準備翻譯: "${textToTranslate}" 從 ${sourceLanguage} 到 ${targetLanguage}`);
        if (translateOutputElement) translateOutputElement.textContent = ''; // Clear previous result
        if (loaderElement) loaderElement.style.display = 'block'; // Show loader
        if (submitTranslateButton) submitTranslateButton.disabled = true; // Disable button

        const backendUrl = 'http://127.0.0.1:5000/translate';
        try {
            console.log(`正要發送 fetch 請求到: ${backendUrl}`);
            const requestBody = {
                text: textToTranslate,
                source_lang: sourceLanguage,
                target_lang: targetLanguage
            };
            console.log("請求的 body:", JSON.stringify(requestBody));

            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            console.log("收到 fetch 回應:", response);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "無法解析伺服器錯誤回應或網路錯誤" }));
                console.error("伺服器回傳錯誤:", response.status, errorData);
                throw new Error(errorData.error || `HTTP 錯誤! 狀態碼: ${response.status}`);
            }

            const data = await response.json();
            console.log("從後端收到的資料:", data);

            if (data.translated_text) {
                let finalText = data.translated_text;
                if (data.detected_source_language && sourceLanguage === 'auto') {
                    console.log(`偵測到的來源語言: ${data.detected_source_language}`);
                }
                if (translateOutputElement) translateOutputElement.textContent = finalText;
                if (translateOutputElement) translateOutputElement.style.color = '#333';
            } else if (data.error) {
                console.error("後端回傳的錯誤訊息:", data.error);
                if (translateOutputElement) translateOutputElement.textContent = `翻譯錯誤: ${data.error}`; // Display more specific error
                if (translateOutputElement) translateOutputElement.style.color = 'red';
            } else {
                console.warn("收到未知的回應格式:", data);
                if (translateOutputElement) translateOutputElement.textContent = "收到未知的回應格式。";
                if (translateOutputElement) translateOutputElement.style.color = 'orange';
            }

        } catch (error) {
            console.error('翻譯請求過程中發生JavaScript錯誤 (catch區塊):', error);
            if (translateOutputElement) {
                translateOutputElement.textContent = `翻譯請求失敗: ${error.message}`; // Display more specific error
                translateOutputElement.style.color = 'red';
            }
        } finally {
            if (loaderElement) loaderElement.style.display = 'none'; // Hide loader
            if (submitTranslateButton) submitTranslateButton.disabled = false; // Re-enable button
        }
    }

    langButtons.forEach(button => {
        button.addEventListener('click', function () {
            const selectedLang = this.dataset.lang;
            localStorage.setItem('croissantGPT_selectedLang', selectedLang);

            // UI text update logic based on selectedLang
            if (selectedLang === 'zh') {
                assistantTitle.textContent = "互動助手";
                document.getElementById('language-prompt-assistant').textContent = "請選擇您的語言：";
                document.getElementById('feature-prompt-assistant').textContent = "請選擇您需要的功能：";
                document.querySelector('.feature-btn[data-feature="translate"]').textContent = "即時翻譯";
                document.querySelector('.feature-btn[data-feature="sanxia-tour"]').textContent = "三峽區旅遊介紹";
                document.querySelector('.feature-btn[data-feature="customs"]').textContent = "台灣傳統風俗";
            } else if (selectedLang === 'en') {
                assistantTitle.textContent = "Interactive Assistant";
                document.getElementById('language-prompt-assistant').textContent = "Please select your language:";
                document.getElementById('feature-prompt-assistant').textContent = "Please select a feature:";
                document.querySelector('.feature-btn[data-feature="translate"]').textContent = "Translate";
                document.querySelector('.feature-btn[data-feature="sanxia-tour"]').textContent = "Sanxia Tour Info";
                document.querySelector('.feature-btn[data-feature="customs"]').textContent = "Taiwanese Customs";
            } else if (selectedLang === 'fr') {
                assistantTitle.textContent = "Assistant Interactif";
                document.getElementById('language-prompt-assistant').textContent = "Veuillez sélectionner votre langue :";
                document.getElementById('feature-prompt-assistant').textContent = "Veuillez sélectionner une fonctionnalité :";
                document.querySelector('.feature-btn[data-feature="translate"]').textContent = "Traduction";
                document.querySelector('.feature-btn[data-feature="sanxia-tour"]').textContent = "Info touristique Sanxia";
                document.querySelector('.feature-btn[data-feature="customs"]').textContent = "Coutumes taïwanaises";
            }
            // Reset content area when language changes after selection
            assistantContentOutput.innerHTML = `<p>歡迎使用！請選擇一個功能。</p>`;
            // languageSelectionArea.style.display = 'none';
            mainFeaturesArea.style.display = 'block';
        });
    });

    featureButtons.forEach(button => {
        button.addEventListener('click', function () {
            const feature = this.dataset.feature;
            const selectedLang = localStorage.getItem('croissantGPT_selectedLang') || 'zh';

            if (feature === 'translate') {
                let currentUiLang = localStorage.getItem('croissantGPT_selectedLang') || 'zh';
                let translateButtonText = "翻譯";
                let sourceLangText = "來源語言：";
                let targetLangText = "目標語言：";
                let autoDetectText = "自動偵測";
                let zhTwText = "中文 (繁體)";
                let enText = "English";
                let frText = "Français";
                let placeholderText = "在這裡輸入要翻譯的文字...";
                let resultText = "翻譯結果：";
                let clearButtonText = "清除";

                if (currentUiLang === 'en') {
                    translateButtonText = "Translate"; sourceLangText = "Source Language:"; targetLangText = "Target Language:";
                    autoDetectText = "Auto-detect"; zhTwText = "Chinese (Traditional)"; placeholderText = "Enter text to translate here...";
                    resultText = "Translation Result:"; clearButtonText = "Clear";
                } else if (currentUiLang === 'fr') {
                    translateButtonText = "Traduire"; sourceLangText = "Langue source :"; targetLangText = "Langue cible :";
                    autoDetectText = "Détection automatique"; zhTwText = "Chinois (Traditionnel)"; placeholderText = "Entrez le texte à traduire ici...";
                    resultText = "Résultat de la traduction :"; clearButtonText = "Effacer";
                }

                assistantContentOutput.innerHTML = `
              <h3>${document.querySelector('.feature-btn[data-feature="translate"]').textContent}</h3>
              <div class="translate-controls">
                  <div>
                      <label for="source-language">${sourceLangText}</label>
                      <select id="source-language">
                          <option value="auto">${autoDetectText}</option>
                          <option value="zh-TW">${zhTwText}</option>
                          <option value="en">${enText}</option>
                          <option value="fr">${frText}</option>
                      </select>
                  </div>
                  <div>
                      <label for="target-language">${targetLangText}</label>
                      <select id="target-language">
                          <option value="en">${enText}</option>
                          <option value="zh-TW">${zhTwText}</option>
                          <option value="fr">${frText}</option>
                      </select>
                  </div>
              </div>
              <textarea id="translate-input" placeholder="${placeholderText}" rows="3"></textarea> <div class="translate-buttons-container">
                  <button id="submit-translate" class="action-btn">${translateButtonText}</button>
                  <button id="clear-translate-input" class="action-btn" type="button">${clearButtonText}</button>
              </div>
              <div id="translate-output-container">
                  <div id="loader" style="display: none;"></div> <h4>${resultText}</h4>
                  <p id="translate-output">(翻譯結果將顯示於此)</p>
              </div>
          `;

                const targetLangDropdown = document.getElementById('target-language');
                if (currentUiLang === 'zh') targetLangDropdown.value = 'en';
                else if (currentUiLang === 'en') targetLangDropdown.value = 'zh-TW';
                else if (currentUiLang === 'fr') targetLangDropdown.value = 'zh-TW';

                const translateInputElement = document.getElementById('translate-input');
                if (translateInputElement) {
                    translateInputElement.addEventListener('input', function () { adjustTextareaHeight(this); });
                    adjustTextareaHeight(translateInputElement); // Initial adjustment
                }

                document.getElementById('submit-translate').addEventListener('click', handleTranslationRequest);
                document.getElementById('clear-translate-input').addEventListener('click', function () {
                    if (translateInputElement) translateInputElement.value = '';
                    const translateOutputElement = document.getElementById('translate-output');
                    if (translateOutputElement) translateOutputElement.textContent = '(翻譯結果將顯示於此)';
                    if (translateOutputElement) translateOutputElement.style.color = '#333'; // Reset color
                    if (translateInputElement) adjustTextareaHeight(translateInputElement); // Adjust height after clearing
                });

            } else if (feature === 'sanxia-tour') {
                assistantContentOutput.innerHTML = `<h3>三峽區旅遊介紹</h3><p>正在從 Gemini 獲取三峽區旅遊資訊 (語言: ${selectedLang})...</p>`;
            } else if (feature === 'customs') {
                assistantContentOutput.innerHTML = `<h3>台灣傳統風俗</h3><p>正在從 Gemini 獲取台灣風俗資訊 (語言: ${selectedLang})...</p>`;
            }
        });
    });

    const storedLang = localStorage.getItem('croissantGPT_selectedLang');
    if (storedLang) {
        const correspondingLangButton = document.querySelector(`.lang-btn[data-lang="${storedLang}"]`);
        if (correspondingLangButton) {
            correspondingLangButton.click();
        }
    }
});