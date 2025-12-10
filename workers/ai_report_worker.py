# workers/ai_report_worker.py - FIXED VERSION
import asyncio
import json
from PyQt5.QtCore import QThread, pyqtSignal
from groq import AsyncGroq

class AIReportWorker(QThread):
    """Worker thread for generating AI-powered stock reports using Groq API"""
    
    report_ready = pyqtSignal(str)  # Emits the generated report
    progress_update = pyqtSignal(str, int)  # Emits (message, percentage)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key: str, ticker: str, stock_data: dict, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.ticker = ticker
        self.stock_data = stock_data
        self.client = None  # Initialize in run() to avoid thread issues
        self._cancelled = False
        
    def cancel(self):
        """Cancel the report generation"""
        self._cancelled = True
        
    def prepare_data_summary(self):
        """Prepare a structured summary of stock data for the AI"""
        try:
            df = self.stock_data.get('dataframe')
            if df is None or df.empty:
                return None
                
            # Calculate key metrics
            latest_price = float(df['Close'].iloc[-1])
            avg_price = float(df['Close'].mean())
            min_price = float(df['Close'].min())
            max_price = float(df['Close'].max())
            price_change = float(df['Close'].iloc[-1] - df['Close'].iloc[0])
            price_change_pct = (price_change / df['Close'].iloc[0]) * 100
            
            # Volume analysis
            avg_volume = float(df['Volume'].mean())
            latest_volume = float(df['Volume'].iloc[-1])
            
            # Technical indicators (if available)
            indicators = {}
            if 'SMA_20' in df.columns:
                indicators['SMA_20'] = float(df['SMA_20'].iloc[-1])
            if 'EMA_20' in df.columns:
                indicators['EMA_20'] = float(df['EMA_20'].iloc[-1])
            if 'RSI' in df.columns:
                indicators['RSI'] = float(df['RSI'].iloc[-1])
            if 'MACD' in df.columns:
                indicators['MACD'] = float(df['MACD'].iloc[-1])
                
            # Trend analysis
            recent_trend = "upward" if price_change > 0 else "downward"
            volatility = float(df['Close'].std())
            
            summary = {
                "ticker": self.ticker,
                "period": f"{len(df)} days",
                "latest_price": round(latest_price, 2),
                "average_price": round(avg_price, 2),
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_pct, 2),
                "trend": recent_trend,
                "volatility": round(volatility, 2),
                "average_volume": int(avg_volume),
                "latest_volume": int(latest_volume),
                "technical_indicators": indicators,
                "forecast": self.stock_data.get('forecast', {})
            }
            
            return summary
            
        except Exception as e:
            print(f"Error preparing data summary: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_report(self):
        """Generate AI-powered report using Groq"""
        try:
            if self._cancelled:
                return None
                
            self.progress_update.emit("📊 Analyzing stock data...", 20)
            print("📊 Step 1: Analyzing stock data...")
            
            # Prepare data summary
            data_summary = self.prepare_data_summary()
            if not data_summary:
                self.error_occurred.emit("Failed to prepare data summary")
                return None
                
            print(f"✅ Data summary prepared for {self.ticker}")
            
            if self._cancelled:
                return None
                
            self.progress_update.emit("🤖 Generating AI insights...", 40)
            print("🤖 Step 2: Calling Groq API...")
            
            # Create comprehensive prompt
            prompt = self.create_report_prompt(data_summary)
            
            if self._cancelled:
                return None
                
            self.progress_update.emit("✍️ Writing report...", 60)
            print("✍️ Step 3: Writing report...")
            
            # Initialize client here to avoid thread issues
            if self.client is None:
                self.client = AsyncGroq(api_key=self.api_key)
            
            # Call Groq API
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a professional financial analyst with expertise in technical analysis, 
                        market trends, and risk assessment. Generate detailed, actionable stock reports in markdown format."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2048,
            )
            
            if self._cancelled:
                return None
                
            self.progress_update.emit("✅ Report complete!", 100)
            print("✅ Step 4: Report generation complete!")
            
            report_content = response.choices[0].message.content
            print(f"📄 Generated report length: {len(report_content)} characters")
            
            return report_content
            
        except Exception as e:
            error_msg = f"AI Report Generation Error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return None
    
    def create_report_prompt(self, data_summary):
        """Create a structured prompt for report generation"""
        
        # Format forecast info if available
        forecast_text = ""
        if data_summary.get('forecast'):
            forecast_data = data_summary['forecast']
            if isinstance(forecast_data, dict):
                forecast_text = f"""
                
**ML Forecast Data:**
- Forecasted Price: ${forecast_data.get('forecasted_price', 'N/A')}
- Prediction Confidence: {forecast_data.get('confidence', 'N/A')}
- Model Type: {forecast_data.get('model', 'Hybrid LSTM + Prophet')}
"""
        
        # Format technical indicators
        indicators_text = ""
        if data_summary.get('technical_indicators'):
            indicators_text = "\n".join([
                f"- {key}: {value}" 
                for key, value in data_summary['technical_indicators'].items()
            ])
        
        prompt = f"""
Generate a comprehensive stock analysis report for **{data_summary['ticker']}** based on the following data:

## 📊 PRICE ANALYSIS
- Current Price: ${data_summary['latest_price']}
- Average Price ({data_summary['period']}): ${data_summary['average_price']}
- Price Range: ${data_summary['min_price']} - ${data_summary['max_price']}
- Price Change: ${data_summary['price_change']} ({data_summary['price_change_percent']}%)
- Trend: {data_summary['trend']}
- Volatility (Std Dev): ${data_summary['volatility']}

## 📈 VOLUME ANALYSIS
- Average Volume: {data_summary['average_volume']:,}
- Latest Volume: {data_summary['latest_volume']:,}

## 🔧 TECHNICAL INDICATORS
{indicators_text if indicators_text else "- Not available"}
{forecast_text}

---

Please generate a structured markdown report with the following sections:

# 1. EXECUTIVE SUMMARY
Provide a 2-3 sentence overview of the stock's current state.

# 2. PRICE PERFORMANCE ANALYSIS
- Analyze the price movement over the period
- Discuss the {data_summary['price_change_percent']}% change
- Comment on volatility levels

# 3. TECHNICAL ANALYSIS
- Interpret the technical indicators (SMA, EMA, RSI, MACD if available)
- Identify support/resistance levels based on min/max prices
- Discuss momentum and trend strength

# 4. VOLUME ANALYSIS
- Analyze trading volume patterns
- Compare current volume to average

# 5. ML FORECAST INTERPRETATION
{f"- Explain the forecasted price of ${data_summary['forecast'].get('forecasted_price', 'N/A')}" if data_summary.get('forecast') else "- No forecast data available"}
- Discuss confidence level and limitations

# 6. RISK ASSESSMENT
- Identify key risks (volatility, trend reversal, market conditions)
- Rate overall risk: **Low/Medium/High**

# 7. RECOMMENDATION
Provide a clear recommendation: **BUY**, **HOLD**, or **SELL**

Include:
- Reasoning for the recommendation
- Entry/exit price suggestions
- Stop-loss recommendations

# 8. KEY TAKEAWAYS
List 3-5 bullet points summarizing the most important insights.

---

**Format the entire report in clean markdown with proper headings, bullet points, and bold text for emphasis.**
Make the report professional, data-driven, and actionable for investors.
"""
        return prompt
    
    def run(self):
        """Run the worker thread"""
        print(f"🚀 AIReportWorker started for {self.ticker}")
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            print("🔄 Running async report generation...")
            report = loop.run_until_complete(self.generate_report())
            
            if report and not self._cancelled:
                print("✅ Emitting report_ready signal")
                self.report_ready.emit(report)
            else:
                print("⚠️ Report generation cancelled or returned None")
                
        except Exception as e:
            error_msg = f"Worker thread error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            
            if not self._cancelled:
                self.error_occurred.emit(error_msg)
        finally:
            loop.close()
            print("🛑 AIReportWorker finished")