# workers/sentiment_worker.py
import asyncio
import json
from typing import List, Optional

from PyQt5.QtCore import QThread, pyqtSignal

# NOTE: import AsyncGroq lazily inside run() to avoid any network calls in main thread
from groq import AsyncGroq


class SentimentWorker(QThread):
    """
    Runs sentiment analysis using the Groq Async client inside a dedicated QThread
    with its own asyncio event loop. Supports safe cancellation via stop().
    Emits:
      - sentiment_ready: dict -> {"score": int, "label": str, "reasoning": str}
      - error_occurred: str
    """

    sentiment_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key: str, headlines: List[str], timeout: int = 30, parent=None):
        """
        :param api_key: Groq API key
        :param headlines: list of headline strings
        :param timeout: max seconds to wait for the LLM response
        """
        super().__init__(parent)
        self.api_key = api_key
        self.headlines = headlines or []
        self.timeout = timeout

        # internal references for cancellation
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None
        self._is_running = False

    def stop(self):
        """
        Request the worker to stop. This will attempt to cancel the running asyncio task
        and stop the event loop safely.
        """
        self._is_running = False
        if self._loop and self._task:
            try:
                # Cancel the task from the thread that owns the loop
                self._loop.call_soon_threadsafe(self._task.cancel)
            except Exception:
                pass

    async def _fetch_sentiment_async(self, client: AsyncGroq) -> Optional[dict]:
        """
        Actual async logic: call the Groq LLM, parse JSON, validate result.
        Runs inside the worker thread's event loop.
        """
        try:
            # Handle empty headlines quickly
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

Respond ONLY with valid JSON, no markdown formatting.
"""

            # Use wait_for to enforce a timeout and allow cancellation
            coro = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional market sentiment analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )

            # Await the LLM call with timeout (so it can be cancelled or fail fast)
            response = await asyncio.wait_for(coro, timeout=self.timeout)

            # If the task was cancelled, raise to upper layer
            if not self._is_running:
                return None

            result_text = response.choices[0].message.content.strip()

            # Strip common codeblock wrappers
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()

            sentiment_data = json.loads(result_text)

            # Validate structure
            if "score" not in sentiment_data or "label" not in sentiment_data:
                raise ValueError("Invalid sentiment response format")

            # Clamp score to [0, 100]
            sentiment_data["score"] = int(max(0, min(100, sentiment_data["score"])))

            # final check whether worker was canceled during parsing
            if not self._is_running:
                return None

            return sentiment_data

        except asyncio.CancelledError:
            # Task was cancelled (stop() was called)
            return None
        except asyncio.TimeoutError:
            self.error_occurred.emit(f"Sentiment request timed out after {self.timeout}s")
            return None
        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Failed to parse sentiment JSON: {e}")
            return None
        except Exception as e:
            # surface other errors via signal
            self.error_occurred.emit(f"Sentiment analysis error: {str(e)}")
            return None

    def run(self):
        """
        Start an asyncio loop in this thread, create a client, and run the sentiment call.
        """
        # mark running
        self._is_running = True

        # Create a fresh event loop owned by this thread
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)

        client = None
        try:
            # Create AsyncGroq client inside worker thread (avoid network on main thread)
            client = AsyncGroq(api_key=self.api_key)

            # Create task and run until complete (cancellable)
            coro = self._fetch_sentiment_async(client)
            self._task = loop.create_task(coro)

            # Run the task
            result = loop.run_until_complete(self._task)

            # Emit result if present and not cancelled
            if result and self._is_running:
                self.sentiment_ready.emit(result)

        except Exception as e:
            # If any unexpected exception bubbles up, emit it
            try:
                self.error_occurred.emit(str(e))
            except Exception:
                pass
        finally:
            # Cleanup: ensure client closed if it supports an async close
            try:
                if client:
                    # Some async clients expose aclose or close; try both safely
                    if hasattr(client, "aclose"):
                        loop.run_until_complete(client.aclose())
                    elif hasattr(client, "close"):
                        maybe = client.close()
                        if asyncio.iscoroutine(maybe):
                            loop.run_until_complete(maybe)
            except Exception:
                pass

            # Cancel any pending task
            try:
                if self._task and not self._task.done():
                    self._task.cancel()
                    # let loop finish cancellations
                    loop.run_until_complete(asyncio.sleep(0))
            except Exception:
                pass

            # Close event loop
            try:
                loop.stop()
                loop.close()
            except Exception:
                pass

            # clear refs
            self._loop = None
            self._task = None
            self._is_running = False
