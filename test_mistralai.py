import os
from rich.markdown import Markdown
from rich.console import Console
from mistralai import Mistral

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
model = "mistral-large-latest"

def display_markdown(md):
    console = Console()
    md = Markdown(md)
    console.print(md)

client = Mistral(api_key=MISTRAL_API_KEY)

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
