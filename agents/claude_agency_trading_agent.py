#!/usr/bin/env python3
"""
Claude Agency Trading Agent
Extracted from gravity-ven/ai_agency repository

A sophisticated trading agent that implements the trading team structure
with CEO, TradePlanner, RiskManager, TradeAgent, and DataScientist roles.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class TradingPolicy:
    """Trading policy configuration from ai_agency repo"""
    version: str = "1.0.0"
    max_position_size: float = 2.0  # percentage
    risk_per_trade: float = 1.0     # percentage
    max_daily_drawdown: float = 3.0  # percentage
    required_stop_loss: bool = True
    required_risk_assessment: bool = True

@dataclass
class TeamMember:
    """Team member in trading hierarchy"""
    role: str
    performance_score: float = 0.0
    consecutive_losses: int = 0
    last_decision: Optional[datetime] = None

class ClaudeAgencyTradingAgent:
    """
    Advanced trading agent implementing Claude Agency patterns
    Features:
    - Team-based decision making
    - Performance scoring system
    - Risk management integration
    - Evolution-based agent replacement
    """
    
    def __init__(self, policy_config: Optional[Dict] = None):
        self.policy = TradingPolicy()
        if policy_config:
            self._load_policy(policy_config)
            
        # Team hierarchy
        self.team_hierarchy = ["CEO", "TradePlanner", "RiskManager", "TradeAgent", "DataScientist"]
        self.team_members = {
            role: TeamMember(role=role) 
            for role in self.team_hierarchy
        }
        
        # Performance tracking
        self.performance_history = []
        self.decision_log = []
        
        # Evolution parameters
        self.consecutive_loss_threshold = 5
        self.minimum_win_rate = 60.0
        self.evaluation_period_hours = 24
        
    def _load_policy(self, policy_config: Dict):
        """Load policy from configuration"""
        trading_rules = policy_config.get("system_rules", {}).get("trading_rules", {})
        
        self.policy.max_position_size = trading_rules.get("max_position_size", {}).get("value", 2.0)
        self.policy.risk_per_trade = trading_rules.get("risk_per_trade", {}).get("value", 1.0)
        self.policy.max_daily_drawdown = trading_rules.get("max_daily_drawdown", {}).get("value", 3.0)
        self.policy.required_stop_loss = trading_rules.get("required_stop_loss", True)
        self.policy.required_risk_assessment = trading_rules.get("required_risk_assessment", True)
    
    def make_team_decision(self, market_data: Dict, analysis: Dict) -> Dict:
        """Make trading decision using team-based approach"""
        decisions = {}
        
        # Each team member contributes
        for role, member in self.team_members.items():
            decision = self._get_role_decision(role, market_data, analysis)
            decisions[role] = decision
            member.last_decision = datetime.now()
        
        # CEO makes final decision based on team input
        final_decision = self._synthesize_team_decision(decisions)
        
        # Log decision
        self._log_decision(final_decision, decisions)
        
        return final_decision
    
    def _get_role_decision(self, role: str, market_data: Dict, analysis: Dict) -> Dict:
        """Get decision from specific team role"""
        if role == "CEO":
            return {
                "action": "APPROVE" if analysis.get("confidence", 0) > 0.7 else "REJECT",
                "reasoning": f"Executive oversight: confidence {analysis.get('confidence', 0):.2f}",
                "risk_score": analysis.get("risk_score", 0.5)
            }
        elif role == "TradePlanner":
            return {
                "position_size": min(self.policy.max_position_size, analysis.get("optimal_size", 1.0)),
                "entry_price": analysis.get("entry_price"),
                "strategy": analysis.get("recommended_strategy", "CONSERVATIVE")
            }
        elif role == "RiskManager":
            risk_assessment = analysis.get("risk_assessment", {})
            return {
                "risk_approved": risk_assessment.get("value", 0) <= self.policy.risk_per_trade,
                "stop_loss": analysis.get("stop_loss", 0.02),
                "concerns": risk_assessment.get("concerns", [])
            }
        elif role == "TradeAgent":
            return {
                "execution_ready": True,
                "timing": analysis.get("optimal_timing", "IMMEDIATE"),
                "order_type": analysis.get("order_type", "MARKET")
            }
        elif role == "DataScientist":
            return {
                "model_confidence": analysis.get("model_confidence", 0.5),
                "data_quality": analysis.get("data_quality", "GOOD"),
                "recommendations": analysis.get("technical_signals", [])
            }
        
        return {"action": "NO_OPINION"}
    
    def _synthesize_team_decision(self, team_decisions: Dict) -> Dict:
        """Synthesize team decisions into final action"""
        ceo_decision = team_decisions.get("CEO", {})
        trade_planner = team_decisions.get("TradePlanner", {})
        risk_manager = team_decisions.get("RiskManager", {})
        
        # Check if team approves
        team_approval = (
            ceo_decision.get("action") == "APPROVE" and
            risk_manager.get("risk_approved", False)
        )
        
        final_decision = {
            "action": "EXECUTE" if team_approval else "HOLD",
            "team_approval": team_approval,
            "position_size": trade_planner.get("position_size", 0) if team_approval else 0,
            "entry_price": trade_planner.get("entry_price"),
            "stop_loss": risk_manager.get("stop_loss"),
            "confidence": ceo_decision.get("confidence", 0.5),
            "timestamp": datetime.now().isoformat()
        }
        
        return final_decision
    
    def _log_decision(self, final_decision: Dict, team_decisions: Dict):
        """Log decision for compliance and evolution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "final_decision": final_decision,
            "team_decisions": team_decisions,
            "policy_version": self.policy.version
        }
        
        self.decision_log.append(log_entry)
        
        # Keep log manageable
        if len(self.decision_log) > 1000:
            self.decision_log = self.decision_log[-500:]
    
    def update_performance(self, trade_result: Dict):
        """Update team performance based on trade results"""
        success = trade_result.get("profit", 0) > 0
        
        # Update team members
        for member in self.team_members.values():
            if success:
                member.performance_score += 1
                member.consecutive_losses = 0
            else:
                member.performance_score -= 2
                member.consecutive_losses += 1
        
        # Log performance
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "trade_result": trade_result,
            "team_scores": {role: m.performance_score for role, m in self.team_members.items()}
        })
        
        # Check for team evolution needs
        self._evaluate_team_evolution()
    
    def _evaluate_team_evolution(self):
        """Evaluate if any team members need replacement"""
        for role, member in self.team_members.items():
            if (member.consecutive_losses >= self.consecutive_loss_threshold or
                member.performance_score < 0):
                
                logging.info(f"Team member {role} replacement needed: "
                           f"consecutive_losses={member.consecutive_losses}, "
                           f"score={member.performance_score}")
                
                # Reset for evolution
                member.performance_score = 0
                member.consecutive_losses = 0
    
    def get_team_status(self) -> Dict:
        """Get current team status and performance"""
        return {
            "team_members": {
                role: {
                    "performance_score": member.performance_score,
                    "consecutive_losses": member.consecutive_losses,
                    "last_decision": member.last_decision.isoformat() if member.last_decision else None
                }
                for role, member in self.team_members.items()
            },
            "policy": self.policy.__dict__,
            "performance_history_count": len(self.performance_history),
            "decision_log_count": len(self.decision_log)
        }

# Export for Factory Droid integration
def create_claude_agency_agent(config_path: Optional[str] = None):
    """Factory function to create Claude Agency Trading Agent"""
    policy_config = None
    if config_path:
        with open(config_path, 'r') as f:
            policy_config = json.load(f)
    
    return ClaudeAgencyTradingAgent(policy_config)

if __name__ == "__main__":
    # Demo usage
    agent = ClaudeAgencyTradingAgent()
    
    # Example decision making
    market_data = {"symbol": "BTC", "price": 50000}
    analysis = {
        "confidence": 0.8,
        "risk_score": 0.3,
        "optimal_size": 1.5,
        "entry_price": 50000,
        "recommended_strategy": "AGGRESSIVE",
        "risk_assessment": {"value": 0.8, "concerns": []},
        "stop_loss": 0.02,
        "optimal_timing": "IMMEDIATE",
        "order_type": "MARKET",
        "model_confidence": 0.75,
        "data_quality": "EXCELLENT",
        "technical_signals": ["RSI_OVERSOLD", "MACD_BULLISH"]
    }
    
    decision = agent.make_team_decision(market_data, analysis)
    print("Team Decision:", json.dumps(decision, indent=2))
    
    print("\nTeam Status:", json.dumps(agent.get_team_status(), indent=2))
