"""
Plotly Chart Generator - Professional charts with indicators
"""

import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class PlotlyChartGenerator:
    """Generate professional trading charts with Plotly"""
    
    def __init__(self):
        self.charts_dir = "charts_output"
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)
        logger.info("✅ PlotlyChartGenerator initialized")
    
    def generate_chart(
        self,
        signal,
        df: pd.DataFrame,
        mode: str
    ) -> str:
        """
        Generate professional chart with indicators
        
        Args:
            signal: Signal object
            df: DataFrame with OHLC data
            mode: Trading mode (Sniper/Momentum)
        
        Returns:
            Path to saved chart image
        """
        try:
            # Extract signal data
            pair = signal.pair
            signal_type = signal.direction
            entry_price = signal.trigger_price or signal.current_price
            score = signal.score
            expiry = signal.expiry_minutes
            
            if df is None or len(df) < 10:
                logger.error("❌ Insufficient data for chart")
                return None
            
            # Calculate indicators if not present
            from app.indicators import calculate_all_indicators
            df = calculate_all_indicators(df)
            
            # Extract indicator series
            ema9 = df.get('ema9')
            ema21 = df.get('ema21')
            ema50 = df.get('ema50')
            rsi = df.get('rsi')
            
            # Create subplots: Main chart + RSI
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f"{pair} - {mode} Mode", "RSI")
            )
            
            # === Main Chart: Candlesticks ===
            fig.add_trace(
                go.Candlestick(
                    x=df['datetime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
            
            # === EMA Lines ===
            if ema9 is not None:
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=ema9,
                        name='EMA 9',
                        line=dict(color='#2196F3', width=1.5)
                    ),
                    row=1, col=1
                )
            
            if ema21 is not None:
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=ema21,
                        name='EMA 21',
                        line=dict(color='#FF9800', width=1.5)
                    ),
                    row=1, col=1
                )
            
            if ema50 is not None:
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=ema50,
                        name='EMA 50',
                        line=dict(color='#9C27B0', width=1.5)
                    ),
                    row=1, col=1
                )
            
            # === Entry Price Line ===
            entry_color = '#00C853' if signal_type == 'CALL' else '#D32F2F'
            fig.add_hline(
                y=entry_price,
                line=dict(color=entry_color, width=2, dash='dash'),
                annotation_text=f"Entry: {entry_price:.5f}",
                annotation_position="right",
                row=1, col=1
            )
            
            # === RSI Subplot ===
            if rsi is not None:
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=rsi,
                        name='RSI',
                        line=dict(color='#FF6F00', width=2)
                    ),
                    row=2, col=1
                )
                
                # RSI levels
                fig.add_hline(y=70, line=dict(color='red', width=1, dash='dot'), row=2, col=1)
                fig.add_hline(y=30, line=dict(color='green', width=1, dash='dot'), row=2, col=1)
                fig.add_hline(y=50, line=dict(color='gray', width=1, dash='dot'), row=2, col=1)
            
            # === Layout Styling ===
            signal_emoji = "📈" if signal_type == "CALL" else "📉"
            title_text = f"{signal_emoji} {pair} | {signal_type} | Score: {score}/100 | {expiry}"
            
            fig.update_layout(
                title=dict(
                    text=title_text,
                    font=dict(size=18, color='white', family='Arial Black')
                ),
                xaxis_title="Time",
                yaxis_title="Price",
                template='plotly_dark',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=800,
                margin=dict(l=50, r=50, t=100, b=50),
                paper_bgcolor='#1e1e1e',
                plot_bgcolor='#2d2d2d',
                font=dict(color='white')
            )
            
            # Update axes
            fig.update_xaxes(
                gridcolor='#3d3d3d',
                showgrid=True,
                rangeslider_visible=False
            )
            fig.update_yaxes(
                gridcolor='#3d3d3d',
                showgrid=True
            )
            
            # Add watermark
            fig.add_annotation(
                text="MJ Trading",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=60, color='rgba(255,255,255,0.1)'),
                textangle=-30
            )
            
            # Save chart
            filename = f"{self.charts_dir}/{pair.replace('/', '_')}_{mode}_{signal_type}_{int(datetime.now().timestamp())}.png"
            fig.write_image(filename, width=1400, height=800, scale=2)
            
            logger.info(f"✅ Chart saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generating chart: {e}")
            return None
