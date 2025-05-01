import asyncio
from construction_chatbot.chatbot import ConstructionChatbot
import typer

app = typer.Typer()

@app.command()
def chat(question: str):
    """Ask a question to the construction bot"""
    bot = ConstructionChatbot()
    result = asyncio.run(bot.chat(question))
    print(result["answer"])

def main():
    app()

if __name__ == "__main__":
    main()