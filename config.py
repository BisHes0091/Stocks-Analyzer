# config.py
TRADING_CONFIG = {
    "default_timeframe": "1 Month",
    "default_symbol": "GC=F",
    "refresh_interval": 60,
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2,
    "sma_periods": [20, 50, 200],
    "risk_free_rate": 0.02,
    "max_position_size": 100000,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.15
}

API_KEYS = {
    "alpha_vantage": "ur alpha_vantage here",
    "fmp": "ur fmp api here",
    "news_api": "ur news api here"
}

COLOR_SCHEME = {
    "bg_primary": "#131722",
    "bg_secondary": "#1e222d",
    "accent": "#2962ff",
    "buy": "#00c853",
    "sell": "#ff5252",
    "neutral": "#ffd700",
    "text": "#d1d4dc"
}