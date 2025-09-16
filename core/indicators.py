# indicators.py
def calculate_sma(df, window=20):
    df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()
    return df


def calculate_ema(df, span=20):
    df[f"EMA_{span}"] = df["Close"].ewm(span=span, adjust=False).mean()
    return df
