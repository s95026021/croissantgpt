import os
from rich.markdown import Markdown
from rich.console import Console
from mistralai import Mistral

API_KEY = "PbzkjJxzUAhDhPDN1aYh0oQFzSTgbVjW"
model = "mistral-large-latest"

def display_markdown(md):
    console = Console()
    md = Markdown(md)
    console.print(md)

client = Mistral(api_key=API_KEY)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
response = chat_response.choices[0].message.content

display_markdown(response)
