# workers/sentiment_worker.py
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from groq import AsyncGroq
import json


class SentimentWorker(QThread):
    sentiment_ready = pyqtSignal(dict)  # {"score": 65, "label": "Bullish", "reasoning": "..."}
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key: str, headlines: list, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.headlines = headlines
        self.client = AsyncGroq(api_key=self.api_key)

    async def fetch_sentiment(self):
        try:
            # Handle empty headlines
            if not self.headlines:
                return {
                    "score": 50,
                    "label": "Neutral",
                    "reasoning": "No headlines available for analysis"
                }
            
            headlines_text = "\n".join([f"- {h}" for h in self.headlines])
            
            prompt = f"""Analyze the following stock market headlines and provide a sentiment analysis:

{headlines_text}

Provide your analysis in JSON format with:
1. "score": A number from 0-100 (0=Very Bearish, 50=Neutral, 100=Very Bullish)
2. "label": One of ["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"]
3. "reasoning": A brief explanation (2-3 sentences)

Example:
{{"score": 75, "label": "Bullish", "reasoning": "Headlines show positive market trends..."}}

Respond ONLY with valid JSON, no markdown formatting."""

            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional market sentiment analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            sentiment_data = json.loads(result_text)
            
            # Validate the response
            if "score" not in sentiment_data or "label" not in sentiment_data:
                raise ValueError("Invalid sentiment response format")
            
            # Ensure score is in valid range
            sentiment_data["score"] = max(0, min(100, sentiment_data["score"]))
            
            return sentiment_data
            
        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Failed to parse sentiment: {str(e)}")
            return None
        except Exception as e:
            self.error_occurred.emit(f"Sentiment analysis error: {str(e)}")
            return None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sentiment = loop.run_until_complete(self.fetch_sentiment())
        if sentiment:
            self.sentiment_ready.emit(sentiment)