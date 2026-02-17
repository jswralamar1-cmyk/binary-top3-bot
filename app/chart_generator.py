"""
Chart Generator - Phase J
Generates smart charts for signals
Different charts for Sniper vs Momentum modes
"""

import logging
import os
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import mplfinance as mpf

from app.config import (
    CHART_CANDLES_SNIPER,
    CHART_CANDLES_MOMENTUM,
    MODE_SNIPER,
    MODE_MOMENTUM,
    WATERMARK_TEXT
)
from app.models import Signal
from app.indicators import calculate_all_indicators

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Smart chart generator"""
    
    def __init__(self, charts_dir: str = "/tmp/charts"):
        self.charts_dir = charts_dir
        os.makedirs(charts_dir, exist_ok=True)
        logger.info(f"✅ ChartGenerator initialized (dir: {charts_dir})")
    
    def generate_chart(
        self,
        signal: Signal,
        df: pd.DataFrame,
        mode: str
    ) -> Optional[str]:
        """
        Generate chart for signal
        
        Args:
            signal: Signal object
            df: DataFrame with OHLCV data
            mode: "sniper" or "momentum"
        
        Returns:
            Path to chart image or None if error
        """
        try:
            # Determine number of candles
            if mode == MODE_SNIPER:
                n_candles = CHART_CANDLES_SNIPER
            else:
                n_candles = CHART_CANDLES_MOMENTUM
            
            # Take last N candles
            df = df.iloc[-n_candles:].copy()
            
            # Calculate indicators
            df = calculate_all_indicators(df)
            
            # Set datetime as index
            df.set_index("datetime", inplace=True)
            
            # Prepare chart
            if mode == MODE_SNIPER:
                chart_path = self._generate_sniper_chart(signal, df)
            else:
                chart_path = self._generate_momentum_chart(signal, df)
            
            logger.debug(f"✅ Chart generated for {signal.pair}: {chart_path}")
            return chart_path
        
        except Exception as e:
            logger.error(f"❌ Error generating chart for {signal.pair}: {e}")
            return None
    
    def _generate_sniper_chart(self, signal: Signal, df: pd.DataFrame) -> str:
        """
        Generate chart for Sniper mode
        - 50 candles
        - EMA9, EMA21
        - RSI
        - Entry trigger line
        - Breakout zone
        """
        # Create figure
        fig = plt.figure(figsize=(12, 8), facecolor='#1a1a1a')
        
        # Define grid
        gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 0.1], hspace=0.05)
        ax_main = fig.add_subplot(gs[0])
        ax_rsi = fig.add_subplot(gs[1], sharex=ax_main)
        
        # Style
        style = mpf.make_mpf_style(
            base_mpf_style='charles',
            marketcolors=mpf.make_marketcolors(
                up='#00ff88',
                down='#ff4444',
                edge='inherit',
                wick='inherit',
                volume='inherit'
            ),
            facecolor='#1a1a1a',
            edgecolor='#333333',
            figcolor='#1a1a1a',
            gridcolor='#333333',
            gridstyle='--',
            y_on_right=False
        )
        
        # Plot candlesticks
        mpf.plot(
            df,
            type='candle',
            style=style,
            ax=ax_main,
            volume=False,
            show_nontrading=False
        )
        
        # Plot EMAs
        ax_main.plot(df.index, df['ema9'], color='#00aaff', linewidth=1.5, label='EMA9', alpha=0.8)
        ax_main.plot(df.index, df['ema21'], color='#ffaa00', linewidth=1.5, label='EMA21', alpha=0.8)
        
        # Plot entry trigger line
        trigger_price = signal.trigger_price
        current_price = signal.current_price
        
        if signal.direction == "CALL":
            trigger_color = '#00ff00'
            trigger_label = f'🎯 دخول: {trigger_price:.5f}'
        else:
            trigger_color = '#ff0000'
            trigger_label = f'🎯 دخول: {trigger_price:.5f}'
        
        ax_main.axhline(y=trigger_price, color=trigger_color, linestyle='--', linewidth=2, label=trigger_label, alpha=0.8)
        ax_main.axhline(y=current_price, color='#ffffff', linestyle=':', linewidth=1, label=f'💵 الحالي: {current_price:.5f}', alpha=0.6)
        
        # Breakout zone (shaded area)
        if signal.direction == "CALL":
            ax_main.axhspan(trigger_price, trigger_price * 1.001, alpha=0.1, color='green')
        else:
            ax_main.axhspan(trigger_price * 0.999, trigger_price, alpha=0.1, color='red')
        
        # Title and labels
        ax_main.set_title(
            f"{signal.pair} - ⚡ Sniper Setup - {signal.direction} - ⭐ {signal.score:.0f}/100",
            color='white',
            fontsize=14,
            fontweight='bold',
            pad=10
        )
        ax_main.set_ylabel('السعر', color='white', fontsize=10)
        ax_main.legend(loc='upper left', fontsize=8, facecolor='#1a1a1a', edgecolor='#333333', labelcolor='white')
        ax_main.tick_params(colors='white')
        ax_main.spines['bottom'].set_color('#333333')
        ax_main.spines['top'].set_color('#333333')
        ax_main.spines['left'].set_color('#333333')
        ax_main.spines['right'].set_color('#333333')
        
        # Plot RSI
        ax_rsi.plot(df.index, df['rsi'], color='#00aaff', linewidth=1.5)
        ax_rsi.axhline(y=70, color='#ff4444', linestyle='--', linewidth=1, alpha=0.5)
        ax_rsi.axhline(y=30, color='#00ff88', linestyle='--', linewidth=1, alpha=0.5)
        ax_rsi.axhline(y=50, color='#888888', linestyle=':', linewidth=1, alpha=0.3)
        ax_rsi.fill_between(df.index, 30, 70, alpha=0.05, color='gray')
        ax_rsi.set_ylabel('RSI', color='white', fontsize=10)
        ax_rsi.set_ylim(0, 100)
        ax_rsi.tick_params(colors='white')
        ax_rsi.spines['bottom'].set_color('#333333')
        ax_rsi.spines['top'].set_color('#333333')
        ax_rsi.spines['left'].set_color('#333333')
        ax_rsi.spines['right'].set_color('#333333')
        ax_rsi.set_facecolor('#1a1a1a')
        
        # Watermark
        fig.text(0.5, 0.01, WATERMARK_TEXT, ha='center', fontsize=10, color='white', alpha=0.3)
        
        # Save
        chart_path = os.path.join(self.charts_dir, f"{signal.pair.replace('/', '_')}_{signal.tf}_sniper.png")
        plt.savefig(chart_path, facecolor='#1a1a1a', edgecolor='none', dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _generate_momentum_chart(self, signal: Signal, df: pd.DataFrame) -> str:
        """
        Generate chart for Momentum mode
        - 100 candles
        - EMA9, EMA21, EMA50
        - RSI + MACD
        - Entry trigger line
        - Support/Resistance zones
        """
        # Create figure
        fig = plt.figure(figsize=(14, 10), facecolor='#1a1a1a')
        
        # Define grid
        gs = fig.add_gridspec(4, 1, height_ratios=[4, 1, 1, 0.1], hspace=0.05)
        ax_main = fig.add_subplot(gs[0])
        ax_rsi = fig.add_subplot(gs[1], sharex=ax_main)
        ax_macd = fig.add_subplot(gs[2], sharex=ax_main)
        
        # Style
        style = mpf.make_mpf_style(
            base_mpf_style='charles',
            marketcolors=mpf.make_marketcolors(
                up='#00ff88',
                down='#ff4444',
                edge='inherit',
                wick='inherit',
                volume='inherit'
            ),
            facecolor='#1a1a1a',
            edgecolor='#333333',
            figcolor='#1a1a1a',
            gridcolor='#333333',
            gridstyle='--',
            y_on_right=False
        )
        
        # Plot candlesticks
        mpf.plot(
            df,
            type='candle',
            style=style,
            ax=ax_main,
            volume=False,
            show_nontrading=False
        )
        
        # Plot EMAs
        ax_main.plot(df.index, df['ema9'], color='#00aaff', linewidth=1.5, label='EMA9', alpha=0.8)
        ax_main.plot(df.index, df['ema21'], color='#ffaa00', linewidth=1.5, label='EMA21', alpha=0.8)
        ax_main.plot(df.index, df['ema50'], color='#888888', linewidth=1.5, label='EMA50', alpha=0.6)
        
        # Plot entry trigger line
        trigger_price = signal.trigger_price
        current_price = signal.current_price
        
        if signal.direction == "CALL":
            trigger_color = '#00ff00'
            trigger_label = f'🎯 دخول: {trigger_price:.5f}'
        else:
            trigger_color = '#ff0000'
            trigger_label = f'🎯 دخول: {trigger_price:.5f}'
        
        ax_main.axhline(y=trigger_price, color=trigger_color, linestyle='--', linewidth=2, label=trigger_label, alpha=0.8)
        ax_main.axhline(y=current_price, color='#ffffff', linestyle=':', linewidth=1, label=f'💵 الحالي: {current_price:.5f}', alpha=0.6)
        
        # Support/Resistance zones (last 20 candles high/low)
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].min()
        ax_main.axhline(y=recent_high, color='#ff4444', linestyle=':', linewidth=1, alpha=0.3)
        ax_main.axhline(y=recent_low, color='#00ff88', linestyle=':', linewidth=1, alpha=0.3)
        
        # Title and labels
        ax_main.set_title(
            f"{signal.pair} - 🔥 Momentum Setup - {signal.direction} - ⭐ {signal.score:.0f}/100",
            color='white',
            fontsize=14,
            fontweight='bold',
            pad=10
        )
        ax_main.set_ylabel('السعر', color='white', fontsize=10)
        ax_main.legend(loc='upper left', fontsize=8, facecolor='#1a1a1a', edgecolor='#333333', labelcolor='white')
        ax_main.tick_params(colors='white')
        ax_main.spines['bottom'].set_color('#333333')
        ax_main.spines['top'].set_color('#333333')
        ax_main.spines['left'].set_color('#333333')
        ax_main.spines['right'].set_color('#333333')
        
        # Plot RSI
        ax_rsi.plot(df.index, df['rsi'], color='#00aaff', linewidth=1.5)
        ax_rsi.axhline(y=70, color='#ff4444', linestyle='--', linewidth=1, alpha=0.5)
        ax_rsi.axhline(y=30, color='#00ff88', linestyle='--', linewidth=1, alpha=0.5)
        ax_rsi.axhline(y=50, color='#888888', linestyle=':', linewidth=1, alpha=0.3)
        ax_rsi.fill_between(df.index, 30, 70, alpha=0.05, color='gray')
        ax_rsi.set_ylabel('RSI', color='white', fontsize=10)
        ax_rsi.set_ylim(0, 100)
        ax_rsi.tick_params(colors='white')
        ax_rsi.spines['bottom'].set_color('#333333')
        ax_rsi.spines['top'].set_color('#333333')
        ax_rsi.spines['left'].set_color('#333333')
        ax_rsi.spines['right'].set_color('#333333')
        ax_rsi.set_facecolor('#1a1a1a')
        
        # Plot MACD
        ax_macd.plot(df.index, df['macd'], color='#00aaff', linewidth=1.5, label='MACD')
        ax_macd.plot(df.index, df['macd_signal'], color='#ffaa00', linewidth=1.5, label='Signal')
        ax_macd.bar(df.index, df['macd_hist'], color='#888888', alpha=0.5, label='Histogram')
        ax_macd.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)
        ax_macd.set_ylabel('MACD', color='white', fontsize=10)
        ax_macd.legend(loc='upper left', fontsize=7, facecolor='#1a1a1a', edgecolor='#333333', labelcolor='white')
        ax_macd.tick_params(colors='white')
        ax_macd.spines['bottom'].set_color('#333333')
        ax_macd.spines['top'].set_color('#333333')
        ax_macd.spines['left'].set_color('#333333')
        ax_macd.spines['right'].set_color('#333333')
        ax_macd.set_facecolor('#1a1a1a')
        
        # Watermark
        fig.text(0.5, 0.01, WATERMARK_TEXT, ha='center', fontsize=10, color='white', alpha=0.3)
        
        # Save
        chart_path = os.path.join(self.charts_dir, f"{signal.pair.replace('/', '_')}_{signal.tf}_momentum.png")
        plt.savefig(chart_path, facecolor='#1a1a1a', edgecolor='none', dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
