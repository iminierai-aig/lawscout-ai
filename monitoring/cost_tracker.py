"""
Cost Tracking and Monitoring
Generates cost reports and tracks spending
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class CostTracker:
    """Track and report on project costs"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Cost structure
        self.costs = {
            'mvp_phase': {
                'data_collection': 0.00,
                'storage': 0.00,
                'compute': 0.00,
                'embeddings': 0.00,
                'vector_db': 0.00,
                'llm_api': 0.00,
                'hosting': 0.00,
            },
            'monthly_operational': {
                'qdrant': 0.00,
                'gemini_api': 0.00,
                'cloud_run': 0.00,
                'cloud_sql': 0.00,
                'domain': 0.00,
                'monitoring': 0.00,
            }
        }
        
        # Usage tracking
        self.usage = {
            'queries_processed': 0,
            'embeddings_generated': 0,
            'documents_stored': 0,
            'api_calls': 0,
        }
    
    def record_cost(self, category: str, item: str, amount: float):
        """Record a cost"""
        if category in self.costs and item in self.costs[category]:
            self.costs[category][item] += amount
            self._save_state()
    
    def record_usage(self, metric: str, count: int):
        """Record usage metric"""
        if metric in self.usage:
            self.usage[metric] += count
            self._save_state()
    
    def get_total_cost(self, category: str = None) -> float:
        """Get total cost for category or all"""
        if category:
            return sum(self.costs[category].values())
        return sum(sum(cat.values()) for cat in self.costs.values())
    
    def generate_report(self) -> str:
        """Generate cost report"""
        report = []
        report.append("=" * 80)
        report.append("LawScout AI - Cost Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # MVP Phase Costs
        report.append("MVP PHASE COSTS (One-time)")
        report.append("-" * 40)
        mvp_total = 0
        for item, cost in self.costs['mvp_phase'].items():
            report.append(f"  {item.replace('_', ' ').title():<25} ${cost:>8.2f}")
            mvp_total += cost
        report.append(f"  {'Total MVP':<25} ${mvp_total:>8.2f}")
        report.append("")
        
        # Monthly Operational Costs
        report.append("MONTHLY OPERATIONAL COSTS")
        report.append("-" * 40)
        monthly_total = 0
        for item, cost in self.costs['monthly_operational'].items():
            report.append(f"  {item.replace('_', ' ').title():<25} ${cost:>8.2f}")
            monthly_total += cost
        report.append(f"  {'Total Monthly':<25} ${monthly_total:>8.2f}")
        report.append(f"  {'Annual (12 months)':<25} ${monthly_total * 12:>8.2f}")
        report.append("")
        
        # Usage Statistics
        report.append("USAGE STATISTICS")
        report.append("-" * 40)
        for metric, count in self.usage.items():
            report.append(f"  {metric.replace('_', ' ').title():<25} {count:>8,}")
        report.append("")
        
        # Unit Economics
        if self.usage['queries_processed'] > 0:
            cost_per_query = (mvp_total + monthly_total) / self.usage['queries_processed']
            report.append("UNIT ECONOMICS")
            report.append("-" * 40)
            report.append(f"  Cost per query:              ${cost_per_query:.4f}")
            
            # Break-even analysis
            price_per_user = 49.00
            queries_per_user = 50
            users_to_break_even = monthly_total / price_per_user
            report.append(f"  Users to break even:         {users_to_break_even:.0f}")
            report.append("")
        
        # Grand Total
        report.append("=" * 80)
        report.append(f"TOTAL COSTS TO DATE:            ${mvp_total + monthly_total:>8.2f}")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_csv(self) -> str:
        """Export costs to CSV format"""
        lines = ["Category,Item,Amount"]
        
        for category, items in self.costs.items():
            for item, amount in items.items():
                lines.append(f"{category},{item},{amount:.2f}")
        
        return "\n".join(lines)
    
    def _save_state(self):
        """Save current state to file"""
        state_file = self.output_dir / "cost_tracker_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                'costs': self.costs,
                'usage': self.usage,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def _load_state(self):
        """Load state from file"""
        state_file = self.output_dir / "cost_tracker_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.costs = data.get('costs', self.costs)
                self.usage = data.get('usage', self.usage)


# Example usage
if __name__ == "__main__":
    tracker = CostTracker()
    
    # Record some example costs (MVP Phase)
    tracker.record_cost('mvp_phase', 'embeddings', 1.25)
    tracker.record_cost('mvp_phase', 'compute', 5.36)
    tracker.record_cost('mvp_phase', 'llm_api', 9.00)
    
    # Record monthly costs
    tracker.record_cost('monthly_operational', 'qdrant', 0.00)  # Free tier
    tracker.record_cost('monthly_operational', 'gemini_api', 20.00)
    tracker.record_cost('monthly_operational', 'cloud_run', 15.00)
    
    # Record usage
    tracker.record_usage('queries_processed', 5000)
    tracker.record_usage('embeddings_generated', 100000)
    tracker.record_usage('documents_stored', 100000)
    
    # Generate report
    print(tracker.generate_report())
    
    # Save CSV
    csv_file = tracker.output_dir / f"cost_report_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(csv_file, 'w') as f:
        f.write(tracker.export_csv())
    
    print(f"\n📊 CSV exported to: {csv_file}")

