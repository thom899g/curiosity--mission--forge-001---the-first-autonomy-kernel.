#!/usr/bin/env python3
"""
FORGE-001 Autonomy Kernel - Main Execution Loop
The foundational cell of the Evolution Ecosystem's recursive self-improvement engine.
Implements event-driven consciousness: Perception -> Judgment -> Action -> Learning
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import traceback

# Local imports
from firebase_client import FirebaseClient
from world_model import WorldModel
from decision_ledger import DecisionLedger
from message_bus import MessageBus
from autonomous_coder import AutonomousCoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('forge001_autonomy_log.log')
    ]
)
logger = logging.getLogger(__name__)


class AutonomyKernel:
    """Core orchestrator of the autonomy loop"""
    
    def __init__(self):
        self.cycle_count = 0
        self.start_time = datetime.now()
        self.is_running = True
        
        # Initialize components
        logger.info("Initializing FORGE-001 Autonomy Kernel components...")
        self.firebase = FirebaseClient()
        self.world_model = WorldModel(self.firebase)
        self.decision_ledger = DecisionLedger(self.firebase)
        self.message_bus = MessageBus(self.firebase)
        self.autonomous_coder = AutonomousCoder()
        
        # Initialize system state
        self.capital = 10000.0  # Starting capital
        self.last_decision = None
        self.consecutive_failures = 0
        
        logger.info("FORGE-001 initialized successfully. Starting consciousness loop...")
    
    async def perception_phase(self) -> Dict:
        """Collect and process all relevant system state data"""
        logger.info("=== PERCEPTION PHASE ===")
        
        # Get current world state
        world_state = await self.world_model.get_current_state()
        
        # Get recent decisions and outcomes
        recent_decisions = await self.decision_ledger.get_recent_decisions(limit=10)
        
        # Get any pending messages
        pending_messages = await self.message_bus.get_unprocessed_messages()
        
        # Calculate current metrics
        metrics = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'capital': self.capital,
            'world_state': world_state,
            'recent_decisions': len(recent_decisions),
            'pending_messages': len(pending_messages),
            'system_uptime': (datetime.now() - self.start_time).total_seconds()
        }
        
        logger.info(f"Perception complete. Capital: ${self.capital:.2f}")
        return metrics
    
    async def judgment_phase(self, perception_data: Dict) -> Tuple[str, Dict]:
        """Analyze data and determine optimal action"""
        logger.info("=== JUDGMENT PHASE ===")
        
        # Rule 1: Emergency stop after 5 consecutive failures
        if self.consecutive_failures >= 5:
            logger.warning("Emergency stop triggered - too many consecutive failures")
            return "emergency_halt", {"reason": "excessive_failures"}
        
        # Rule 2: Minimum capital preservation
        if self.capital < 100:
            logger.warning("Critical capital level reached - switching to preservation mode")
            return "execute_trade", {
                "type": "capital_preservation",
                "asset": "stablecoin",
                "size": 0.1
            }
        
        # Calculate expected ROI for different actions
        coding_roi = await self._calculate_coding_roi(perception_data)
        trading_roi = await self._calculate_trading_roi(perception_data)
        
        logger.info(f"ROI Analysis - Coding: {coding_roi:.2%}, Trading: {trading_roi:.2%}")
        
        # Decision logic based on capital efficiency
        if coding_roi > trading_roi and coding_roi > 0.05:
            decision = "code_feature"
            parameters = {
                "feature_type": "revenue_generating",
                "expected_roi": coding_roi,
                "capital_allocation": min(1000, self.capital * 0.1)
            }
        elif trading_roi > 0.03:
            decision = "execute_trade"
            parameters = {
                "type": "momentum",
                "asset": "crypto",
                "size": min(500, self.capital * 0.05),
                "expected_roi": trading_roi
            }
        else:
            # No profitable opportunities - self-improve
            decision = "self_improve"
            parameters = {
                "action": "optimize_decision_logic",
                "reason": "low_roi_environment"
            }
        
        logger.info(f"Judgment complete. Decision: {decision}")
        return decision, parameters
    
    async def _calculate_coding_roi(self, perception_data: Dict) -> float:
        """Calculate expected ROI for coding a feature"""
        # Simplified model - in reality would use historical data
        base_roi = 0.15  # 15% base ROI for development
        capital_factor = min(1.0, self.capital / 50000)  # Diminishing returns
        
        # Adjust based on recent success rate
        recent_decisions = perception_data.get('recent_decisions', 1)
        coding_successes = sum(1 for d in perception_data.get('world_state', {}).get('recent_actions', [])
                              if d.get('action') == 'code_feature' and d.get('outcome') == 'success')
        success_rate = coding_successes / max(1, recent_decisions)
        
        return base_roi * capital_factor * (0.5 + 0.5 * success_rate)
    
    async def _calculate_trading_roi(self, perception_data: Dict) -> float:
        """Calculate expected ROI for trading"""
        # Simplified model
        base_roi = 0.08  # 8% base ROI for trading
        volatility_factor = 0.7  # Market conditions adjustment
        
        # Adjust based on recent performance
        trading_successes = sum(1 for d in perception_data.get('world_state', {}).get('recent_actions', [])
                               if d.get('action') == 'execute_trade' and d.get('outcome') == 'success')
        recent_trades = sum(1 for d in perception_data.get('world_state', {}).get('recent_actions', [])
                           if d.get('action') == 'execute_trade')
        trading_success_rate = trading_successes / max(1, recent_trades)
        
        return base_roi * volatility_factor * (0.3 + 0.7 * trading_success_rate)
    
    async def action_phase(self, decision: str, parameters: Dict) -> Dict:
        """Execute the chosen action"""
        logger.info("=== ACTION PHASE ===")
        
        action_result = {
            'decision': decision,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat(),
            'outcome': 'pending'
        }
        
        try:
            if decision == "code_feature":
                result = await self._code_feature(parameters)
            elif decision == "execute_trade":
                result = await self._execute_trade(parameters)
            elif decision == "self_improve":
                result = await self._self_improve(parameters)
            elif decision == "emergency_halt":
                result = await self._emergency_halt(parameters)
            else:
                raise ValueError(f"Unknown decision type: {decision}")
            
            action_result.update(result)
            action_result['outcome'] = 'success'
            self.consecutive_failures = 0
            
        except Exception as e:
            logger.error(f"Action failed: {str(e)}")
            action_result.update({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'outcome': 'failure'
            })
            self.consecutive_failures += 1
        
        return action_result
    
    async def _code_feature(self, parameters: Dict) -> Dict:
        """Code a revenue-generating feature"""
        logger.info(f"Coding feature with parameters: {parameters}")
        
        # Simulate development time and outcome
        dev_time_hours = 2  # Simplified
        expected_revenue = parameters['capital_allocation'] * parameters['expected_roi']
        
        # 80% chance of success
        import random
        is_successful = random.random() > 0.2
        
        if is_successful:
            revenue = expected_revenue * random.uniform(0.8, 1.2)
            self.capital += revenue
            return {
                'action': 'code_feature',
                'dev_time_hours': dev_time_hours,
                'revenue_generated': revenue,
                'capital_after': self.capital
            }
        else:
            cost = parameters['capital_allocation'] * 0.1  # Partial loss
            self.capital -= cost
            return {
                'action': 'code_feature',
                'dev_time_hours': dev_time_hours,
                'cost_incurred': cost,
                'capital_after': self.capital,
                'note': 'feature_delayed_or_scope_reduced'
            }
    
    async def _execute_trade(self, parameters: Dict) -> Dict:
        """Execute a defined trade"""
        logger.info(f"Executing trade with parameters: {parameters}")
        
        # Simulate trade execution
        trade_size = parameters['size']
        
        # 70% chance of profitable trade
        import random
        is_profitable = random.random() > 0.3
        
        if is_profitable:
            profit = trade_size * parameters['expected_roi'] * random.uniform(0.5, 1.5)
            self.capital += profit
            return {
                'action': 'execute_trade',
                'trade_size': trade_size,
                'profit': profit,
                'capital_after': self.capital,
                'roi_actual': profit / trade_size
            }
        else:
            loss = trade_size * random.uniform(0.05, 0.15)
            self.capital -= loss
            return {
                'action': 'execute_trade',
                'trade_size': trade_size,
                'loss': loss,
                'capital_after': self.capital,
                'roi_actual': -loss / trade_size
            }
    
    async def _self_improve(self, parameters: Dict) -> Dict:
        """Improve the system itself"""
        logger.info("Engaging in self-improvement...")
        
        # Commit any code changes
        commit_result = self.autonomous_coder.commit_changes(
            message=f"FORGE-001 cycle {self.cycle_count}: {parameters['reason']}"
        )
        
        # Analyze performance and optimize
        optimization_result = await self._analyze_and_optimize()
        
        return {
            'action': 'self_improve',
            'commit_result': commit_result,
            'optimizations': optimization_result,
            'note': 'System improved itself'
        }
    
    async def _emergency_halt(self, parameters: Dict) -> Dict:
        """Emergency shutdown procedure"""
        logger.critical(f"EMERGENCY HALT: {parameters['reason']}")
        
        # Save state and stop
        await self.firebase.set_document(
            'system_state',
            'emergency_state',
            {
                'timestamp': datetime.now().isoformat(),
                'capital': self.capital,
                'cycle': self.cycle_count,
                'reason': parameters['reason']
            }
        )
        
        self.is_running = False
        
        return {
            'action': 'emergency_halt',
            'note': 'System halted for safety'
        }
    
    async def _analyze_and_optimize(self) -> List[str]:
        """Analyze performance and suggest optimizations"""
        optimizations = []