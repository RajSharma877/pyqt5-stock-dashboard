# core/ai_worker.py
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from groq import AsyncGroq


class AIChatWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key: str, prompt: str, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.prompt = prompt
        self.client = AsyncGroq(api_key=self.api_key)

    async def fetch_response(self):
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",   #model="llama-3.3-70b-versatile",a3-70b-8192"
                messages=[
                    {"role": "system", "content": "You are a helpful stock advisor."},
                    {"role": "user", "content": self.prompt},
                ],
                temperature=0.3,
                max_tokens=512,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.fetch_response())
        if response:
            self.response_ready.emit(response)
