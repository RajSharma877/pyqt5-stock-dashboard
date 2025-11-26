# workers/hybrid_forecast_worker.py
"""
Hybrid ML Forecast Worker - Prophet + XGBoost
"""

from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import numpy as np
from prophet import Prophet
import logging

# Suppress Prophet warnings
logging.getLogger('prophet').setLevel(logging.WARNING)


class HybridForecastWorker(QThread):
    """
    Worker thread for hybrid forecasting using:
    - Prophet (trend/seasonality)
    - XGBoost (technical patterns)
    
    Optimized for reliability and speed on 8GB RAM systems
    """
    forecast_ready = pyqtSignal(object, dict)  # Emits (forecast_df, metrics)
    progress_update = pyqtSignal(str, int)  # Emits (message, percentage)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, df, periods=30):
        super().__init__()
        self.df = df.copy()
        self.periods = periods
        self._is_cancelled = False

        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'Date' in self.df.columns:
                self.df['Date'] = pd.to_datetime(self.df['Date'])
                self.df.set_index('Date', inplace=True)
            
    def cancel(self):
        self._is_cancelled = True
    
    def run(self):
        try:
            # Step 1: Prophet Forecast
            self.progress_update.emit("🔮 Running Prophet model...", 15)
            prophet_forecast = self._forecast_prophet()
            
            if self._is_cancelled:
                return
            
            # Step 2: Feature Engineering
            self.progress_update.emit("📊 Engineering features...", 35)
            features_df = self._engineer_features()
            
            if self._is_cancelled:
                return
            
            # Step 3: XGBoost Forecast
            xgboost_forecast = None
            try:
                self.progress_update.emit("🚀 Running XGBoost model...", 60)
                xgboost_forecast = self._forecast_xgboost(features_df)
            except Exception as e:
                print(f"⚠️ XGBoost error: {e}")
                # Fallback to Prophet-only if XGBoost fails
            
            if self._is_cancelled:
                return
            
            # Step 4: Ensemble Predictions
            self.progress_update.emit("🎯 Combining predictions...", 85)
            final_forecast = self._ensemble_predictions(
                prophet_forecast, 
                xgboost_forecast
            )
            
            # Step 5: Calculate Metrics
            self.progress_update.emit("📈 Calculating metrics...", 95)
            metrics = self._calculate_metrics(final_forecast, xgboost_forecast)
            
            self.progress_update.emit("✅ Forecast complete!", 100)
            
            if not self._is_cancelled:
                self.forecast_ready.emit(final_forecast, metrics)
                
        except Exception as e:
            if not self._is_cancelled:
                self.error_occurred.emit(f"Forecast error: {str(e)}")
    
    def _forecast_prophet(self):
        """Prophet baseline forecast with volume regressor"""
        prophet_df = self.df.reset_index()[['Date', 'Close']].rename(
            columns={'Date': 'ds', 'Close': 'y'}
        )
        
        model = Prophet(
            daily_seasonality=True,
            yearly_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )
        
        # Add volume as regressor if available
        if 'Volume' in self.df.columns:
            prophet_df['volume'] = self.df['Volume'].values
            model.add_regressor('volume')
        
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=self.periods)
        
        # Fill future volume with rolling average
        if 'volume' in prophet_df.columns:
            avg_volume = self.df['Volume'].tail(30).mean()
            future['volume'] = avg_volume
        
        forecast = model.predict(future)
        
        forecast_df = forecast.set_index('ds')[
            ['yhat', 'yhat_lower', 'yhat_upper']
        ].rename(columns={
            'yhat': 'Prophet',
            'yhat_lower': 'Prophet_Lower',
            'yhat_upper': 'Prophet_Upper',
        })
        
        return forecast_df
    
    def _engineer_features(self):
        """Create technical indicator features for XGBoost"""
        df = self.df.copy()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14, min_periods=1).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)  # Avoid division by zero
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        bb_mid = df['Close'].rolling(window=20, min_periods=1).mean()
        bb_std = df['Close'].rolling(window=20, min_periods=1).std()
        df['BB_Upper'] = bb_mid + (2 * bb_std)
        df['BB_Lower'] = bb_mid - (2 * bb_std)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        
        # Volatility
        df['Volatility'] = df['Close'].pct_change().rolling(window=20, min_periods=1).std()
        
        # Volume features
        if 'Volume' in df.columns:
            df['Volume_MA'] = df['Volume'].rolling(window=20, min_periods=1).mean()
            df['Volume_Ratio'] = df['Volume'] / (df['Volume_MA'] + 1)
        
        # Price momentum
        df['Returns'] = df['Close'].pct_change()
        df['Momentum_5'] = (df['Close'] / df['Close'].shift(5)) - 1
        df['Momentum_10'] = (df['Close'] / df['Close'].shift(10)) - 1
        
        # Lag features
        for i in [1, 2, 3, 5, 10]:
            df[f'Close_Lag_{i}'] = df['Close'].shift(i)
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def _forecast_xgboost(self, features_df):
        """XGBoost-based forecast using technical indicators"""
        try:
            import xgboost as xgb
        except ImportError:
            print("⚠️ XGBoost not installed, using Prophet-only mode")
            return None
        
       
        # Select feature columns (exclude OHLCV)
        feature_cols = [col for col in features_df.columns 
                       if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
        
        X = features_df[feature_cols].values
        y = features_df['Close'].values
        
        # Use 80% for training
        split_idx = int(len(X) * 0.8)
        X_train, y_train = X[:split_idx], y[:split_idx]
        
        # Train XGBoost model (optimized params for speed)
        model = xgb.XGBRegressor(
            n_estimators=50,      # Reduced from 100 for speed
            max_depth=4,          # Reduced from 5 for speed
            learning_rate=0.05,   # Increased from 0.01 for faster convergence
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=2              # Use 2 CPU cores
        )
        model.fit(X_train, y_train, verbose=False)
        
        # Generate future predictions iteratively
        predictions = []
        last_features = X[-1].copy()
        
        for _ in range(self.periods):
            pred = model.predict([last_features])[0]
            predictions.append(pred)
            
            # Simple feature rolling update
            last_features = np.roll(last_features, -1)
            last_features[-1] = pred
        
        # Create forecast dataframe
        last_date = self.df.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1), 
            periods=self.periods
        )
        
        xgb_forecast = pd.DataFrame({
            'XGBoost': predictions
        }, index=future_dates)
        
        return xgb_forecast
    
    def _ensemble_predictions(self, prophet_fc, xgb_fc):
        """Combine Prophet and XGBoost predictions"""
        # Start with Prophet predictions
        ensemble = prophet_fc[['Prophet', 'Prophet_Lower', 'Prophet_Upper']].copy()
        ensemble.rename(columns={
            'Prophet': 'Forecast',
            'Prophet_Lower': 'Lower_Bound',
            'Prophet_Upper': 'Upper_Bound'
        }, inplace=True)
        
        # Get future dates only
        last_historical_date = self.df.index[-1]
        future_mask = ensemble.index > last_historical_date
        
        # If XGBoost available, blend predictions
        if xgb_fc is not None and len(xgb_fc) > 0:
            prophet_weight = 0.6
            xgb_weight = 0.4

            # FIX: Align by index to avoid broadcast error
            future_dates = xgb_fc.index
            prophet_future = prophet_fc.loc[future_dates, 'Prophet']

            combined = (
                prophet_future.values * prophet_weight
                + xgb_fc['XGBoost'].values * xgb_weight
            )

            ensemble.loc[future_dates, 'Forecast'] = combined

            volatility = self.df['Close'].pct_change().std()

            ensemble.loc[future_dates, 'Lower_Bound'] = combined * (1 - 2 * volatility)
            ensemble.loc[future_dates, 'Upper_Bound'] = combined * (1 + 2 * volatility)

        
        return ensemble
    
    def _calculate_metrics(self, forecast_df, xgb_fc):
        """Calculate forecast accuracy metrics"""
        # Get historical predictions
        historical_mask = forecast_df.index <= self.df.index[-1]
        historical_fc = forecast_df.loc[historical_mask, 'Forecast']
        
        # Align with actual data
        actual = self.df.loc[historical_fc.index, 'Close']
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((actual - historical_fc) / actual)) * 100
        
        # Calculate RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean((actual - historical_fc) ** 2))
        
        # Calculate directional accuracy
        actual_direction = (actual.diff() > 0).astype(int)
        pred_direction = (historical_fc.diff() > 0).astype(int)
        directional_accuracy = (actual_direction == pred_direction).mean() * 100
        
        # Determine which models were used
        models_used = ['Prophet']
        if xgb_fc is not None:
            models_used.append('XGBoost')
        
        metrics = {
            'MAPE': round(mape, 2),
            'RMSE': round(rmse, 2),
            'Directional Accuracy': round(directional_accuracy, 2),
            'Models Used': models_used
        }
        
        return metrics