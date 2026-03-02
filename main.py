# main.py
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import yfinance as yf
import talib
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Ui Area
class BisStocks(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stocks_data = {}
        self.current_symbol = "GC=F"
        self.initUI()
        self.setup_theme()

    def initUI(self):
        self.setWindowTitle("BisStocks — Advanced Trading Analyzer")
        self.setGeometry(80, 60, 1500, 950)
        self.setMinimumSize(1200, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 3)
        main_layout.addWidget(right_panel, 2)

        self.statusBar().showMessage("  Ready — Select a market and click Analyze")
        self.statusBar().setStyleSheet(
            "QStatusBar { background-color: #0d1117; color: #6e7681; font-size: 11px; border-top: 1px solid #2a2e39; }"
        )

    def setup_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QWidget {
                background-color: #161b22;
                color: #c9d1d9;
                font-family: 'Segoe UI', 'Inter', Arial;
                font-size: 12px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2962ff, stop:1 #1a47cc);
                color: white;
                border: none;
                padding: 9px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d6fff, stop:1 #2952e8);
            }
            QPushButton:pressed {
                background: #1a3ab8;
            }
            QPushButton#sell {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5252, stop:1 #cc2929);
            }
            QPushButton#sell:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:1 #e03030);
            }
            QPushButton#buy {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c853, stop:1 #009624);
            }
            QPushButton#buy:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1adb68, stop:1 #00aa2a);
            }
            QPushButton#hold {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f0a500, stop:1 #c47f00);
                color: #0d1117;
            }
            QPushButton#hold:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffb300, stop:1 #d48c00);
            }
            QGroupBox {
                border: 1px solid #21262d;
                border-radius: 10px;
                margin-top: 18px;
                font-weight: 700;
                font-size: 12px;
                padding-top: 14px;
                background-color: #0d1117;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #58a6ff;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QComboBox {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 7px 10px;
                color: #c9d1d9;
                font-size: 12px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #58a6ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #21262d;
                border: 1px solid #30363d;
                color: #c9d1d9;
                selection-background-color: #2962ff;
            }
            QLabel#signal {
                font-size: 22px;
                font-weight: 800;
                padding: 12px 20px;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QLabel#price {
                font-size: 30px;
                font-weight: 800;
                color: #3fb950;
                letter-spacing: -0.5px;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
                background-color: #21262d;
                height: 20px;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2962ff, stop:1 #58a6ff);
            }
            QTableWidget {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 6px;
                gridline-color: #21262d;
                outline: 0;
            }
            QTableWidget::item {
                padding: 7px 10px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #1f2b3e;
            }
            QHeaderView::section {
                background-color: #161b22;
                color: #8b949e;
                padding: 7px 10px;
                border: none;
                border-bottom: 1px solid #21262d;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QScrollBar:vertical {
                background-color: #0d1117;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #30363d;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #58a6ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
                color: #c9d1d9;
                line-height: 1.5;
            }
            QCheckBox {
                spacing: 8px;
                color: #8b949e;
                font-size: 12px;
                padding: 3px 0;
            }
            QCheckBox:hover {
                color: #c9d1d9;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid #30363d;
                background-color: #21262d;
            }
            QCheckBox::indicator:checked {
                background-color: #2962ff;
                border-color: #2962ff;
            }
            QFrame#divider {
                background-color: #21262d;
                max-height: 1px;
            }
        """)

    # Market haru
    # u can add more if u want
    def create_left_panel(self):
        panel = QWidget()
        panel.setMaximumWidth(260)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        logo_group = QGroupBox()
        logo_group.setTitle("")
        logo_group.setStyleSheet(
            "QGroupBox { border: 1px solid #21262d; border-radius: 10px; background-color: #0d1117; margin-top: 0; padding: 12px; }"
        )
        logo_layout = QVBoxLayout(logo_group)
        logo_layout.setContentsMargins(10, 10, 10, 10)

        logo_label = QLabel("📈 BIS-STOCKS")
        logo_label.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #58a6ff; padding: 4px 0; background: transparent; letter-spacing: 1px;"
        )
        logo_label.setAlignment(Qt.AlignCenter)

        sub_label = QLabel("Advanced Trading Analyzer")
        sub_label.setStyleSheet(
            "font-size: 11px; color: #484f58; background: transparent; font-weight: 400;"
        )
        sub_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(sub_label)
        layout.addWidget(logo_group)

        stock_group = QGroupBox("Market Selection")
        stock_layout = QVBoxLayout()
        stock_layout.setSpacing(8)

        self.stock_combo = QComboBox()
        stocks = [
            ("Gold / USD", "GC=F"),
            ("Silver / USD", "SI=F"),
            ("S&P 500 ETF", "SPY"),
            ("Bitcoin / USD", "BTC-USD"),
            ("Ethereum / USD", "ETH-USD"),
            ("Apple (AAPL)", "AAPL"),
            ("Tesla (TSLA)", "TSLA"),
            ("Amazon (AMZN)", "AMZN"),
            ("Google (GOOGL)", "GOOGL"),
            ("Microsoft (MSFT)", "MSFT"),
            ("Oil WTI", "CL=F"),
            ("Natural Gas", "NG=F"),
            ("Euro / USD", "EURUSD=X"),
            ("Yen / USD", "JPY=X"),
        ]

        for name, symbol in stocks:
            self.stock_combo.addItem(name, symbol)

        stock_layout.addWidget(self.stock_combo)

        self.analyze_btn = QPushButton("🔍  ANALYZE NOW")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.analyze_stock)
        stock_layout.addWidget(self.analyze_btn)

        stock_group.setLayout(stock_layout)
        layout.addWidget(stock_group)

        timeframe_group = QGroupBox("Timeframe")
        timeframe_layout = QVBoxLayout()
        timeframe_layout.setSpacing(8)

        self.timeframe_combo = QComboBox()
        timeframes = ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"]
        for tf in timeframes:
            self.timeframe_combo.addItem(tf)
        self.timeframe_combo.setCurrentIndex(1)

        timeframe_layout.addWidget(self.timeframe_combo)

        self.refresh_btn = QPushButton("⟳  Refresh Data")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_data)
        timeframe_layout.addWidget(self.refresh_btn)

        timeframe_group.setLayout(timeframe_layout)
        layout.addWidget(timeframe_group)

        indicators_group = QGroupBox("Indicators")
        indicators_layout = QVBoxLayout()
        indicators_layout.setSpacing(4)

        self.rsi_check = QCheckBox("RSI (14)")
        self.rsi_check.setChecked(True)
        self.macd_check = QCheckBox("MACD")
        self.macd_check.setChecked(True)
        self.bollinger_check = QCheckBox("Bollinger Bands")
        self.bollinger_check.setChecked(True)
        self.sma_check = QCheckBox("SMA (20 / 50 / 200)")
        self.sma_check.setChecked(True)
        self.volume_check = QCheckBox("Volume Analysis")
        self.volume_check.setChecked(True)

        indicators_layout.addWidget(self.rsi_check)
        indicators_layout.addWidget(self.macd_check)
        indicators_layout.addWidget(self.bollinger_check)
        indicators_layout.addWidget(self.sma_check)
        indicators_layout.addWidget(self.volume_check)

        indicators_group.setLayout(indicators_layout)
        layout.addWidget(indicators_group)

        layout.addStretch()

        dev_label = QLabel("Dev: Bishesh")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet("color: #30363d; font-size: 10px; background: transparent;")
        layout.addWidget(dev_label)

        return panel

    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        price_group = QGroupBox("Live Price & Signal")
        price_layout = QHBoxLayout()
        price_layout.setContentsMargins(16, 12, 16, 12)

        price_left = QVBoxLayout()
        self.price_label = QLabel("Developed By Bis")
        self.price_label.setObjectName("price")
        self.change_label = QLabel("Awaiting data...")
        self.change_label.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent; margin-top: 2px;")
        price_left.addWidget(self.price_label)
        price_left.addWidget(self.change_label)

        self.signal_label = QLabel("  NEUTRAL  ")
        self.signal_label.setObjectName("signal")
        self.signal_label.setAlignment(Qt.AlignCenter)
        self.signal_label.setStyleSheet(
            "background-color: #21262d; color: #f0a500; border-radius: 8px; border: 1px solid #30363d;"
        )
        self.signal_label.setMinimumWidth(160)

        price_layout.addLayout(price_left)
        price_layout.addStretch()
        price_layout.addWidget(self.signal_label)
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        chart_group = QGroupBox("Chart View  (Last 20 Periods)")
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(10, 8, 10, 8)

        self.chart_widget = QTextEdit()
        self.chart_widget.setMaximumHeight(230)
        self.chart_widget.setMinimumHeight(180)
        self.chart_widget.setReadOnly(True)
        self.chart_widget.setPlaceholderText("Chart will appear after analysis...")
        chart_layout.addWidget(self.chart_widget)

        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)

        signals_group = QGroupBox("Technical Signal Dashboard")
        signals_layout = QGridLayout()
        signals_layout.setSpacing(8)
        signals_layout.setContentsMargins(10, 10, 10, 10)

        self.rsi_signal = self.create_signal_widget("RSI", "— —", "#484f58")
        self.macd_signal = self.create_signal_widget("MACD", "— —", "#484f58")
        self.bollinger_signal = self.create_signal_widget("BOLLINGER", "— —", "#484f58")
        self.trend_signal = self.create_signal_widget("TREND", "— —", "#484f58")
        self.volume_signal = self.create_signal_widget("VOLUME", "— —", "#484f58")
        self.ml_signal = self.create_signal_widget("ML PREDICT", "— —", "#484f58")

        signals_layout.addWidget(self.rsi_signal, 0, 0)
        signals_layout.addWidget(self.macd_signal, 0, 1)
        signals_layout.addWidget(self.bollinger_signal, 0, 2)
        signals_layout.addWidget(self.trend_signal, 1, 0)
        signals_layout.addWidget(self.volume_signal, 1, 1)
        signals_layout.addWidget(self.ml_signal, 1, 2)

        signals_group.setLayout(signals_layout)
        layout.addWidget(signals_group)

        action_group = QGroupBox("Recommended Action")
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(12, 10, 12, 10)
        action_layout.setSpacing(10)

        self.buy_btn = QPushButton("▲  BUY")
        self.buy_btn.setObjectName("buy")
        self.buy_btn.setCursor(Qt.PointingHandCursor)

        self.sell_btn = QPushButton("▼  SELL")
        self.sell_btn.setObjectName("sell")
        self.sell_btn.setCursor(Qt.PointingHandCursor)

        self.hold_btn = QPushButton("⏸  HOLD")
        self.hold_btn.setObjectName("hold")
        self.hold_btn.setCursor(Qt.PointingHandCursor)

        action_layout.addWidget(self.buy_btn)
        action_layout.addWidget(self.sell_btn)
        action_layout.addWidget(self.hold_btn)

        action_group.setLayout(action_layout)
        layout.addWidget(action_group)

        return panel

    def create_right_panel(self):
        panel = QWidget()
        panel.setMaximumWidth(380)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        analysis_group = QGroupBox("Deep Analysis Report")
        analysis_layout = QVBoxLayout()
        analysis_layout.setContentsMargins(8, 8, 8, 8)

        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setPlaceholderText("Select a market and click Analyze to generate a report...")
        analysis_layout.addWidget(self.analysis_text)

        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        levels_group = QGroupBox("Key Price Levels")
        levels_layout = QGridLayout()
        levels_layout.setContentsMargins(12, 10, 12, 10)
        levels_layout.setSpacing(6)

        def make_level_label(text, color="#c9d1d9"):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"color: {color}; background-color: #21262d; border-radius: 5px; padding: 5px 8px; font-weight: 600; font-size: 11px;"
            )
            return lbl

        self.resistance2 = make_level_label("R2: —", "#ff7b72")
        self.resistance1 = make_level_label("R1: —", "#ffa198")
        self.pivot = make_level_label("Pivot: —", "#e3b341")
        self.support1 = make_level_label("S1: —", "#7ee787")
        self.support2 = make_level_label("S2: —", "#56d364")

        levels_layout.addWidget(self.resistance2, 0, 0)
        levels_layout.addWidget(self.resistance1, 0, 1)
        levels_layout.addWidget(self.pivot, 1, 0, 1, 2)
        levels_layout.addWidget(self.support1, 2, 0)
        levels_layout.addWidget(self.support2, 2, 1)

        levels_group.setLayout(levels_layout)
        layout.addWidget(levels_group)

        portfolio_group = QGroupBox("Portfolio Summary")
        portfolio_layout = QVBoxLayout()
        portfolio_layout.setContentsMargins(8, 8, 8, 8)

        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(3)
        self.portfolio_table.setHorizontalHeaderLabels(["Symbol", "Position", "Signal"])
        self.portfolio_table.horizontalHeader().setStretchLastSection(True)
        self.portfolio_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.portfolio_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.portfolio_table.verticalHeader().setVisible(False)
        self.portfolio_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.portfolio_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.portfolio_table.setAlternatingRowColors(True)
        self.portfolio_table.setStyleSheet(
            self.portfolio_table.styleSheet() + "QTableWidget { alternate-background-color: #0d1117; }"
        )
        portfolio_layout.addWidget(self.portfolio_table)

        portfolio_group.setLayout(portfolio_layout)
        layout.addWidget(portfolio_group)

        return panel

    def create_signal_widget(self, name, value, color):
        widget = QWidget()
        widget.setStyleSheet(
            "QWidget { background-color: #0d1117; border-radius: 8px; border: 1px solid #21262d; }"
        )
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-weight: 700; color: #484f58; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;"
        )

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(
            f"font-size: 15px; font-weight: 800; color: {color}; background: transparent; border: none;"
        )

        layout.addWidget(label)
        layout.addWidget(value_label)

        return widget

    def analyze_stock(self):
        symbol = self.stock_combo.currentData()
        self.current_symbol = symbol
        timeframe = self.timeframe_combo.currentText()

        self.statusBar().showMessage(f"  Fetching data for {symbol} ...")
        self.analysis_text.setText("  Downloading market data, please wait...")
        QApplication.processEvents()

        data = self.fetch_stock_data(symbol, timeframe)

        if data is not None and len(data) >= 5:
            analysis = self.perform_analysis(data)
            if analysis:
                self.display_results(analysis, data)
                self.statusBar().showMessage(
                    f"  Last updated: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}   |   Symbol: {symbol}"
                )
        else:
            self.analysis_text.setText(
                "  Could not retrieve sufficient data for this symbol.\n\n"
                "  Try a different timeframe or check your internet connection."
            )
            self.statusBar().showMessage("  Data fetch failed — try a different timeframe")

    def fetch_stock_data(self, symbol, timeframe):
        try:
            period_map = {
                "1 Week": "5d",
                "1 Month": "1mo",
                "3 Months": "3mo",
                "6 Months": "6mo",
                "1 Year": "1y",
                "5 Years": "5y",
            }

            period = period_map.get(timeframe, "1mo")

            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval="1d")

            if data is None or data.empty:
                data = stock.history(period="3mo", interval="1d")

            if data is None or len(data) < 5:
                return None

            return data

        except Exception as e:
            self.analysis_text.setText(f"  Error fetching data: {str(e)}")
            return None

    def _safe_arr(self, series):
        return np.array(series, dtype=float).flatten()

    def perform_analysis(self, data):
        try:
            analysis = {}

            close_prices = self._safe_arr(data['Close'])
            high_prices  = self._safe_arr(data['High'])
            low_prices   = self._safe_arr(data['Low'])
            volumes      = self._safe_arr(data['Volume'])

            if len(close_prices) < 5:
                return None

            analysis['current_price']  = float(close_prices[-1])
            analysis['previous_close'] = float(close_prices[-2]) if len(close_prices) > 1 else float(close_prices[-1])

            rsi_period = min(14, len(close_prices) - 1)
            rsi_values = talib.RSI(close_prices, timeperiod=rsi_period)
            analysis['rsi'] = float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else 50.0

            macd_arr, macd_sig_arr, macd_hist_arr = talib.MACD(close_prices)
            analysis['macd']        = float(macd_arr[-1])      if not np.isnan(macd_arr[-1])      else 0.0
            analysis['macd_signal'] = float(macd_sig_arr[-1]) if not np.isnan(macd_sig_arr[-1]) else 0.0
            analysis['macd_hist']   = float(macd_hist_arr[-1]) if not np.isnan(macd_hist_arr[-1]) else 0.0

            bb_period = min(20, len(close_prices) - 1)
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=bb_period)
            analysis['bb_upper']  = float(upper[-1])  if not np.isnan(upper[-1])  else float(close_prices[-1])
            analysis['bb_middle'] = float(middle[-1]) if not np.isnan(middle[-1]) else float(close_prices[-1])
            analysis['bb_lower']  = float(lower[-1])  if not np.isnan(lower[-1])  else float(close_prices[-1])

            sma20_p  = min(20,  len(close_prices) - 1)
            sma50_p  = min(50,  len(close_prices) - 1)
            sma200_p = min(200, len(close_prices) - 1)

            sma20  = talib.SMA(close_prices, timeperiod=sma20_p)
            sma50  = talib.SMA(close_prices, timeperiod=sma50_p)
            sma200 = talib.SMA(close_prices, timeperiod=sma200_p)

            analysis['sma_20']  = float(sma20[-1])  if not np.isnan(sma20[-1])  else float(close_prices[-1])
            analysis['sma_50']  = float(sma50[-1])  if not np.isnan(sma50[-1])  else float(close_prices[-1])
            analysis['sma_200'] = float(sma200[-1]) if not np.isnan(sma200[-1]) else float(close_prices[-1])

            vol_window = min(20, len(volumes))
            analysis['volume_avg']     = float(np.mean(volumes[-vol_window:]))
            analysis['volume_current'] = float(volumes[-1])

            analysis['pivot']        = float((high_prices[-1] + low_prices[-1] + close_prices[-1]) / 3)
            analysis['resistance_1'] = float(2 * analysis['pivot'] - low_prices[-1])
            analysis['resistance_2'] = float(analysis['pivot'] + (high_prices[-1] - low_prices[-1]))
            analysis['support_1']    = float(2 * analysis['pivot'] - high_prices[-1])
            analysis['support_2']    = float(analysis['pivot'] - (high_prices[-1] - low_prices[-1]))

            price_window = min(20, len(close_prices))
            analysis['volatility'] = float(
                np.std(close_prices[-price_window:]) / np.mean(close_prices[-price_window:])
            ) if price_window > 1 else 0.0

            ml_window = min(30, len(close_prices))
            if ml_window >= 5:
                X = np.arange(ml_window).reshape(-1, 1)
                y = close_prices[-ml_window:]
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                analysis['ml_prediction'] = float(model.predict([[ml_window]])[0])
            else:
                analysis['ml_prediction'] = float(close_prices[-1])

            return analysis

        except Exception as e:
            self.analysis_text.setText(f"  Analysis error: {str(e)}")
            return None

    def display_results(self, analysis, data):
        price_change     = analysis['current_price'] - analysis['previous_close']
        price_change_pct = (price_change / analysis['previous_close']) * 100 if analysis['previous_close'] != 0 else 0

        self.price_label.setText(f"${analysis['current_price']:,.2f}")

        arrow = "▲" if price_change >= 0 else "▼"
        color = "#3fb950" if price_change >= 0 else "#f85149"
        self.change_label.setText(f"{arrow} {abs(price_change):,.2f}  ({price_change_pct:+.2f}%)")
        self.change_label.setStyleSheet(f"font-size: 13px; color: {color}; background: transparent; margin-top: 2px;")

        signals = self.generate_signals(analysis)

        self.update_signal_widget(self.rsi_signal,       "RSI",        signals['rsi_signal'],    signals['rsi_color'])
        self.update_signal_widget(self.macd_signal,      "MACD",       signals['macd_signal'],   signals['macd_color'])
        self.update_signal_widget(self.bollinger_signal, "BOLLINGER",  signals['bb_signal'],     signals['bb_color'])
        self.update_signal_widget(self.trend_signal,     "TREND",      signals['trend_signal'],  signals['trend_color'])
        self.update_signal_widget(self.volume_signal,    "VOLUME",     signals['volume_signal'], signals['volume_color'])
        self.update_signal_widget(self.ml_signal,        "ML PREDICT", signals['ml_signal'],     signals['ml_color'])

        self.signal_label.setText(f"  {signals['overall_signal']}  ")
        self.signal_label.setStyleSheet(
            f"background-color: {signals['overall_color']}; color: white;"
            f"font-size: 22px; font-weight: 800; border-radius: 8px; padding: 12px 20px; letter-spacing: 1px;"
        )

        self.update_key_levels(analysis)
        self.generate_chart_ascii(data, analysis)
        self.generate_analysis_text(analysis, signals)
        self.update_portfolio()

    def update_signal_widget(self, widget, name, value, color):
        layout = widget.layout()
        value_label = layout.itemAt(1).widget()
        value_label.setText(value)
        value_label.setStyleSheet(
            f"font-size: 15px; font-weight: 800; color: {color}; background: transparent; border: none;"
        )

    def generate_signals(self, analysis):
        signals = {}

        if analysis['rsi'] < 30:
            signals['rsi_signal'] = "BUY"
            signals['rsi_color']  = "#3fb950"
        elif analysis['rsi'] > 70:
            signals['rsi_signal'] = "SELL"
            signals['rsi_color']  = "#f85149"
        else:
            signals['rsi_signal'] = "NEUTRAL"
            signals['rsi_color']  = "#e3b341"

        if analysis['macd'] > analysis['macd_signal']:
            signals['macd_signal'] = "BUY"
            signals['macd_color']  = "#3fb950"
        else:
            signals['macd_signal'] = "SELL"
            signals['macd_color']  = "#f85149"

        if analysis['current_price'] < analysis['bb_lower']:
            signals['bb_signal'] = "BUY"
            signals['bb_color']  = "#3fb950"
        elif analysis['current_price'] > analysis['bb_upper']:
            signals['bb_signal'] = "SELL"
            signals['bb_color']  = "#f85149"
        else:
            signals['bb_signal'] = "NEUTRAL"
            signals['bb_color']  = "#e3b341"

        if analysis['current_price'] > analysis['sma_50'] > analysis['sma_200']:
            signals['trend_signal'] = "STRONG BUY"
            signals['trend_color']  = "#3fb950"
        elif analysis['current_price'] > analysis['sma_50']:
            signals['trend_signal'] = "BUY"
            signals['trend_color']  = "#3fb950"
        elif analysis['current_price'] < analysis['sma_50'] < analysis['sma_200']:
            signals['trend_signal'] = "STRONG SELL"
            signals['trend_color']  = "#f85149"
        elif analysis['current_price'] < analysis['sma_50']:
            signals['trend_signal'] = "SELL"
            signals['trend_color']  = "#f85149"
        else:
            signals['trend_signal'] = "NEUTRAL"
            signals['trend_color']  = "#e3b341"

        vol_ratio = analysis['volume_current'] / analysis['volume_avg'] if analysis['volume_avg'] > 0 else 1
        if vol_ratio > 1.5:
            signals['volume_signal'] = "HIGH"
            signals['volume_color']  = "#58a6ff"
        elif vol_ratio < 0.5:
            signals['volume_signal'] = "LOW"
            signals['volume_color']  = "#e3b341"
        else:
            signals['volume_signal'] = "NORMAL"
            signals['volume_color']  = "#8b949e"

        if analysis['ml_prediction'] > analysis['current_price'] * 1.02:
            signals['ml_signal'] = "BULLISH"
            signals['ml_color']  = "#3fb950"
        elif analysis['ml_prediction'] < analysis['current_price'] * 0.98:
            signals['ml_signal'] = "BEARISH"
            signals['ml_color']  = "#f85149"
        else:
            signals['ml_signal'] = "NEUTRAL"
            signals['ml_color']  = "#e3b341"

        buy_signals  = sum(1 for k in ['rsi_signal','macd_signal','bb_signal','trend_signal','ml_signal']
                          if 'BUY' in signals.get(k, '') or 'BULLISH' in signals.get(k, ''))
        sell_signals = sum(1 for k in ['rsi_signal','macd_signal','bb_signal','trend_signal','ml_signal']
                          if 'SELL' in signals.get(k, '') or 'BEARISH' in signals.get(k, ''))

        if buy_signals >= sell_signals + 3:
            signals['overall_signal'] = "STRONG BUY"
            signals['overall_color']  = "#238636"
        elif buy_signals > sell_signals:
            signals['overall_signal'] = "BUY"
            signals['overall_color']  = "#2ea043"
        elif sell_signals >= buy_signals + 3:
            signals['overall_signal'] = "STRONG SELL"
            signals['overall_color']  = "#b62324"
        elif sell_signals > buy_signals:
            signals['overall_signal'] = "SELL"
            signals['overall_color']  = "#da3633"
        else:
            signals['overall_signal'] = "NEUTRAL"
            signals['overall_color']  = "#9e6a03"

        return signals

    def update_key_levels(self, analysis):
        self.resistance2.setText(f"R2: ${analysis['resistance_2']:,.2f}")
        self.resistance1.setText(f"R1: ${analysis['resistance_1']:,.2f}")
        self.support1.setText(   f"S1: ${analysis['support_1']:,.2f}")
        self.support2.setText(   f"S2: ${analysis['support_2']:,.2f}")
        self.pivot.setText(      f"Pivot: ${analysis['pivot']:,.2f}")

    def generate_chart_ascii(self, data, analysis):
        close_prices = self._safe_arr(data['Close'])[-20:]
        n = len(close_prices)

        if n < 2:
            self.chart_widget.setText("  Not enough data for chart.")
            return

        min_p = float(np.min(close_prices))
        max_p = float(np.max(close_prices))
        price_range = max_p - min_p if max_p != min_p else 1.0

        rows = 10
        cols = n

        chart_lines = []
        chart_lines.append(f" {'Price':>10}  {'─' * cols}")

        for i in range(rows, -1, -1):
            level = min_p + (price_range * i / rows)
            bar   = ""
            for price in close_prices:
                if price >= level:
                    bar += "█"
                else:
                    bar += " "
            chart_lines.append(f" ${level:>9,.2f}  {bar}")

        chart_lines.append(f" {'':>10}  {'─' * cols}")
        chart_lines.append(f" {'':>10}  ← {n} periods")

        self.chart_widget.setText("\n".join(chart_lines))

    def generate_analysis_text(self, analysis, signals):
        p  = analysis['current_price']
        rsi = analysis['rsi']

        lines = []
        lines.append("══ MARKET STATUS ══════════════════════════════")
        lines.append(f"  Price      :  ${p:>12,.2f}")
        lines.append(f"  RSI (14)   :  {rsi:.1f}   →  {signals['rsi_signal']}")
        lines.append(f"  MACD       :  {'Bullish ▲' if analysis['macd'] > analysis['macd_signal'] else 'Bearish ▼'}")
        lines.append(f"  Volatility :  {analysis['volatility']*100:.2f}%")
        lines.append("")
        lines.append("══ KEY LEVELS ═════════════════════════════════")
        lines.append(f"  Resistance 2:  ${analysis['resistance_2']:>10,.2f}")
        lines.append(f"  Resistance 1:  ${analysis['resistance_1']:>10,.2f}")
        lines.append(f"  Pivot Point :  ${analysis['pivot']:>10,.2f}")
        lines.append(f"  Support 1   :  ${analysis['support_1']:>10,.2f}")
        lines.append(f"  Support 2   :  ${analysis['support_2']:>10,.2f}")
        lines.append("")
        lines.append("══ MOVING AVERAGES ════════════════════════════")
        lines.append(f"  SMA  20 :  ${analysis['sma_20']:>10,.2f}")
        lines.append(f"  SMA  50 :  ${analysis['sma_50']:>10,.2f}")
        lines.append(f"  SMA 200 :  ${analysis['sma_200']:>10,.2f}")
        trend_str = "Uptrend ▲" if analysis['current_price'] > analysis['sma_50'] else "Downtrend ▼"
        lines.append(f"  Trend   :  {trend_str}")
        lines.append("")
        lines.append("══ AI / ML FORECAST ═══════════════════════════")
        pct = ((analysis['ml_prediction'] / p) - 1) * 100
        lines.append(f"  Next Period : ${analysis['ml_prediction']:>10,.2f}")
        lines.append(f"  Expected Δ  : {pct:+.2f}%")
        lines.append("")
        lines.append("══ RISK ASSESSMENT ════════════════════════════")
        if analysis['volatility'] > 0.02:
            lines.append("  ⚠  HIGH VOLATILITY — size positions carefully")
        elif analysis['volatility'] > 0.01:
            lines.append("  ●  MODERATE VOLATILITY — normal conditions")
        else:
            lines.append("  ●  LOW VOLATILITY — range-bound market")

        vol_status = "Above Avg ▲" if analysis['volume_current'] > analysis['volume_avg'] else "Below Avg ▼"
        lines.append(f"  Volume : {vol_status}")
        lines.append("")
        lines.append("══ RECOMMENDATION ═════════════════════════════")
        lines.append(f"  Overall Signal :  {signals['overall_signal']}")

        if "BUY" in signals['overall_signal']:
            lines.append(f"  Entry Zone  :  ${analysis['support_1']:,.2f} – ${p:,.2f}")
            lines.append(f"  Target 1    :  ${analysis['resistance_1']:,.2f}")
            lines.append(f"  Target 2    :  ${analysis['resistance_2']:,.2f}")
            lines.append(f"  Stop Loss   :  ${analysis['support_2']:,.2f}")
        elif "SELL" in signals['overall_signal']:
            lines.append(f"  Entry Zone  :  ${p:,.2f} – ${analysis['resistance_1']:,.2f}")
            lines.append(f"  Target 1    :  ${analysis['support_1']:,.2f}")
            lines.append(f"  Target 2    :  ${analysis['support_2']:,.2f}")
            lines.append(f"  Stop Loss   :  ${analysis['resistance_2']:,.2f}")

        lines.append("═══════════════════════════════════════════════")

        self.analysis_text.setText("\n".join(lines))

    def update_portfolio(self):
        sample_data = [
            ("GOLD",   "2.5 oz",  "BUY"),
            ("SILVER", "50 oz",   "HOLD"),
            ("BTC",    "0.15",    "SELL"),
            ("SPY",    "10 sh",   "BUY"),
        ]

        self.portfolio_table.setRowCount(len(sample_data))

        for i, (symbol, position, signal) in enumerate(sample_data):
            sym_item = QTableWidgetItem(symbol)
            sym_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.portfolio_table.setItem(i, 0, sym_item)
            self.portfolio_table.setItem(i, 1, QTableWidgetItem(position))

            signal_item = QTableWidgetItem(signal)
            signal_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            if signal == "BUY":
                signal_item.setForeground(QColor("#3fb950"))
            elif signal == "SELL":
                signal_item.setForeground(QColor("#f85149"))
            else:
                signal_item.setForeground(QColor("#e3b341"))

            self.portfolio_table.setItem(i, 2, signal_item)

        self.portfolio_table.resizeRowsToContents()

    def refresh_data(self):
        self.analyze_stock()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = BisStocks()
    window.show()

    QTimer.singleShot(500, window.analyze_stock)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()