"""
Scanner - Main Orchestrator
Integrates all engines to perform complete scan
"""

import logging
from datetime import datetime
from typing import List

from app.config import TRADING_PAIRS
from app.models import UserSelection, ScanResult, Signal
from app.yahoo_data_provider import YahooDataProvider
from app.signal_engine import SignalEngine
from app.confirm_engine import ConfirmEngine
from app.entry_engine import EntryEngine
from app.ranking_engine import RankingEngine
from app.risk_engine import RiskEngine
from app.plotly_chart_generator import PlotlyChartGenerator

logger = logging.getLogger(__name__)


class Scanner:
    """Main scanner orchestrator"""
    
    def __init__(self):
        # Initialize all engines
        self.data_provider = YahooDataProvider()
        self.signal_engine = SignalEngine()
        self.confirm_engine = ConfirmEngine(self.data_provider)
        self.entry_engine = EntryEngine()
        self.ranking_engine = RankingEngine()
        self.risk_engine = RiskEngine()
        self.chart_generator = PlotlyChartGenerator()
        
        logger.info("✅ Scanner initialized with all engines")
    
    async def scan(self, selection: UserSelection) -> ScanResult:
        """
        Perform complete scan
        
        Args:
            selection: User's selection (mode, expiry, timeframe)
        
        Returns:
            ScanResult with Top 3 signals
        """
        logger.info("=" * 60)
        logger.info(f"🔍 Starting scan: mode={selection.mode}, expiry={selection.expiry}m, tf={selection.timeframe}")
        logger.info("=" * 60)
        
        # Phase 1: Fetch data
        logger.info("📊 Phase 1: Fetching market data...")
        pairs_data = await self.data_provider.fetch_multiple(
            pairs=TRADING_PAIRS,
            timeframe=selection.timeframe,
            n=120
        )
        
        if not pairs_data:
            logger.error("❌ No data fetched!")
            return ScanResult(
                mode=selection.mode,
                expiry=selection.expiry,
                timeframe=selection.timeframe,
                signals=[],
                scan_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                total_pairs=len(TRADING_PAIRS),
                filtered_count=0
            )
        
        logger.info(f"✅ Fetched data for {len(pairs_data)}/{len(TRADING_PAIRS)} pairs")
        
        # Phase 2: Generate signals
        logger.info("🎯 Phase 2: Generating signals...")
        signals = await self.signal_engine.scan_all_pairs(
            pairs_data=pairs_data,
            mode=selection.mode,
            timeframe=selection.timeframe
        )
        
        if not signals:
            logger.warning("⚠️ No signals generated!")
            return ScanResult(
                mode=selection.mode,
                expiry=selection.expiry,
                timeframe=selection.timeframe,
                signals=[],
                scan_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                total_pairs=len(pairs_data),
                filtered_count=0
            )
        
        logger.info(f"✅ Generated {len(signals)} signals")
        
        # Phase 3: Optional 5m confirmation (only for timeframes < 15m)
        if selection.timeframe in ["1min", "5min"]:
            logger.info("🔍 Phase 3: Confirming signals on 5m...")
            confirmed_signals = await self.confirm_engine.confirm_signals(signals)
            
            # Use confirmed signals if available, otherwise use all
            if confirmed_signals:
                signals = confirmed_signals
                logger.info(f"✅ {len(signals)} signals confirmed on 5m")
            else:
                logger.warning("⚠️ No signals confirmed on 5m, using all signals")
        else:
            logger.info("⏭️ Phase 3: Skipping 5m confirmation (timeframe >= 15m)")
        
        # Phase 4: Calculate entry plans
        logger.info("📍 Phase 4: Calculating entry plans...")
        signals = self.entry_engine.calculate_entry_plans(signals, selection.expiry)
        logger.info(f"✅ Entry plans calculated for {len(signals)} signals")
        
        # Phase 5: Rank signals
        logger.info("🏆 Phase 5: Ranking signals...")
        top_signals = self.ranking_engine.rank_signals(signals)
        logger.info(f"✅ Top {len(top_signals)} signals selected")
        
        # Phase 6: Add risk warnings
        logger.info("⚠️ Phase 6: Adding risk warnings...")
        top_signals = self.risk_engine.add_risk_warnings(top_signals)
        logger.info(f"✅ Risk warnings added to {len(top_signals)} signals")
        
        # Phase 7: Generate charts
        logger.info("📊 Phase 7: Generating charts...")
        for signal in top_signals:
            if signal.pair in pairs_data:
                chart_path = self.chart_generator.generate_chart(
                    signal=signal,
                    df=pairs_data[signal.pair],
                    mode=selection.mode
                )
                signal.chart_path = chart_path
        
        logger.info(f"✅ Charts generated for {len(top_signals)} signals")
        
        # Create result
        result = ScanResult(
            mode=selection.mode,
            expiry=selection.expiry,
            timeframe=selection.timeframe,
            signals=top_signals,
            scan_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_pairs=len(pairs_data),
            filtered_count=len(signals)
        )
        
        logger.info("=" * 60)
        logger.info(f"✅ Scan complete: {len(top_signals)} Top signals ready")
        logger.info("=" * 60)
        
        return result
