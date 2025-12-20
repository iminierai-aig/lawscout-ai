"""
Gemini API Usage Tracker
Tracks token usage and costs in real-time with daily limits
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class GeminiUsageTracker:
    """
    Track Gemini API usage and costs in real-time
    
    Pricing (as of 2024):
    - Input tokens: $0.075 per 1M tokens (gemini-2.0-flash-exp)
    - Output tokens: $0.30 per 1M tokens (gemini-2.0-flash-exp)
    """
    
    # Gemini 2.0 Flash pricing (per 1M tokens)
    INPUT_COST_PER_MILLION = 0.075
    OUTPUT_COST_PER_MILLION = 0.30
    
    def __init__(self, max_daily_cost: Optional[float] = None):
        """
        Initialize usage tracker
        
        Args:
            max_daily_cost: Maximum daily cost in USD (default from env or $5.00)
        """
        self.max_daily_cost = max_daily_cost or float(
            os.getenv("MAX_DAILY_GEMINI_COST", "5.00")
        )
        
        # Daily tracking (resets at midnight)
        self.daily_input_tokens = 0
        self.daily_output_tokens = 0
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()
        
        # Lifetime tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        
        # Per-user tracking (optional)
        self.user_usage = defaultdict(lambda: {
            'input_tokens': 0,
            'output_tokens': 0,
            'requests': 0
        })
        
        logger.info(f"📊 Gemini Usage Tracker initialized (max daily cost: ${self.max_daily_cost:.2f})")
    
    def _check_reset_daily(self):
        """Reset daily counters if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            logger.info(
                f"📅 Daily reset: Previous day cost: ${self.get_daily_cost():.4f}, "
                f"Requests: {self.daily_requests}"
            )
            self.daily_input_tokens = 0
            self.daily_output_tokens = 0
            self.daily_requests = 0
            self.last_reset_date = today
    
    def track_usage(
        self, 
        input_tokens: int, 
        output_tokens: int,
        user_id: Optional[int] = None
    ):
        """
        Track API usage
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            user_id: Optional user ID for per-user tracking
        """
        self._check_reset_daily()
        
        # Update daily counters
        self.daily_input_tokens += input_tokens
        self.daily_output_tokens += output_tokens
        self.daily_requests += 1
        
        # Update lifetime counters
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_requests += 1
        
        # Update per-user tracking if provided
        if user_id:
            self.user_usage[user_id]['input_tokens'] += input_tokens
            self.user_usage[user_id]['output_tokens'] += output_tokens
            self.user_usage[user_id]['requests'] += 1
        
        # Log usage
        daily_cost = self.get_daily_cost()
        logger.debug(
            f"📊 Usage tracked: {input_tokens} input, {output_tokens} output tokens. "
            f"Daily cost: ${daily_cost:.4f}"
        )
    
    def get_daily_cost(self) -> float:
        """Calculate daily cost in USD"""
        input_cost = (self.daily_input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (self.daily_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        return input_cost + output_cost
    
    def get_total_cost(self) -> float:
        """Calculate total lifetime cost in USD"""
        input_cost = (self.total_input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (self.total_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        return input_cost + output_cost
    
    def check_cost_limit(self) -> tuple[bool, str]:
        """
        Check if daily cost limit is exceeded
        
        Returns:
            (is_allowed, message): Whether API calls are allowed and reason
        """
        self._check_reset_daily()
        
        daily_cost = self.get_daily_cost()
        
        if daily_cost >= self.max_daily_cost:
            message = (
                f"⚠️ Daily Gemini API cost limit exceeded: ${daily_cost:.4f} >= ${self.max_daily_cost:.2f}. "
                f"AI features temporarily disabled. Resets at midnight."
            )
            logger.warning(message)
            return False, message
        
        # Warn at 80% of limit
        if daily_cost >= self.max_daily_cost * 0.8:
            message = (
                f"⚠️ Approaching daily cost limit: ${daily_cost:.4f} / ${self.max_daily_cost:.2f} "
                f"({daily_cost / self.max_daily_cost * 100:.1f}%)"
            )
            logger.warning(message)
            return True, message
        
        return True, ""
    
    def get_stats(self) -> dict:
        """Get current usage statistics"""
        self._check_reset_daily()
        
        daily_cost = self.get_daily_cost()
        total_cost = self.get_total_cost()
        
        return {
            'daily': {
                'input_tokens': self.daily_input_tokens,
                'output_tokens': self.daily_output_tokens,
                'requests': self.daily_requests,
                'cost': daily_cost,
                'cost_limit': self.max_daily_cost,
                'cost_percentage': (daily_cost / self.max_daily_cost * 100) if self.max_daily_cost > 0 else 0
            },
            'lifetime': {
                'input_tokens': self.total_input_tokens,
                'output_tokens': self.total_output_tokens,
                'requests': self.total_requests,
                'cost': total_cost
            }
        }
    
    def log_stats(self):
        """Log current usage statistics"""
        stats = self.get_stats()
        daily = stats['daily']
        lifetime = stats['lifetime']
        
        logger.info(
            f"📊 Gemini Usage Stats:\n"
            f"   Daily: {daily['requests']} requests, "
            f"{daily['input_tokens']:,} input + {daily['output_tokens']:,} output tokens, "
            f"${daily['cost']:.4f} cost ({daily['cost_percentage']:.1f}% of limit)\n"
            f"   Lifetime: {lifetime['requests']} requests, "
            f"{lifetime['input_tokens']:,} input + {lifetime['output_tokens']:,} output tokens, "
            f"${lifetime['cost']:.4f} total cost"
        )


# Global tracker instance
_global_tracker: Optional[GeminiUsageTracker] = None

def get_usage_tracker() -> GeminiUsageTracker:
    """Get or create global usage tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = GeminiUsageTracker()
    return _global_tracker

