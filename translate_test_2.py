from googletrans import Translator
import asyncio

async def translate(text, src_lang, dest_lang):
    async with Translator() as translator:
        result = await translator.translate(text, src=src_lang, dest=dest_lang)
        return result

eng_version = asyncio.run(translate("Heureux qui comme Ulysse a fait un bon voyage.", src_lang="fr", dest_lang="en"))
print(eng_version)