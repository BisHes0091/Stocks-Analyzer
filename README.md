Stock Trading Strategy Automation using Python

This repository contains a Python-based solution for automating stock trading strategies. It integrates with various APIs to gather stock market data and applies multiple technical indicators to analyze trading opportunities. The system is customizable and built with flexibility in mind, allowing you to configure multiple trading parameters.

Key Features:

Trading Configuration: A config.py file allows you to easily customize trading parameters, including:

Default timeframe (e.g., 1 Month)

Symbol (e.g., "GC=F" for gold futures)

Risk management parameters like stop loss and take profit percentages

Common technical indicators like RSI, MACD, and Bollinger Bands

Technical Indicators:

RSI (Relative Strength Index): A momentum oscillator to determine overbought or oversold conditions.

MACD (Moving Average Convergence Divergence): A trend-following indicator used to identify moving averages that indicate a new trend.

Bollinger Bands: Used to measure volatility and overbought/oversold conditions.

SMA (Simple Moving Averages): Helps track the average value of stock prices over a specified number of periods.

Risk Management:

Configurable stop_loss_pct and take_profit_pct to automate position exits based on percentage thresholds.

Maximum position size (max_position_size) and a risk-free rate for calculating expected returns.

API Integrations:

Alpha Vantage API: For real-time market data (you’ll need your own API key).

FMP API (Financial Modeling Prep): For fetching financial data and company fundamentals.

News API: To gather the latest financial news, assisting in sentiment analysis.

Customizable Color Scheme: The script allows you to customize the look and feel of visualizations with a color scheme tailored for dark mode.

Usage:

Set up your API keys in the config.py file.

Adjust trading parameters such as risk tolerance, technical indicator settings, and stock symbols.

Run the trading strategy script and begin analyzing stock data with automated trading rules.

This repository is a perfect starting point for those looking to build, test, or refine their algorithmic trading strategies with Python.
