#!/usr/bin/env python3
"""
OpenClaw Cost Calculator
Analyzes your usage and projects monthly costs based on model routing

Usage:
    python3 cost-calculator.py [--tasks N] [--heartbeat-interval M]

Examples:
    python3 cost-calculator.py --tasks 100 --heartbeat-interval 30
    python3 cost-calculator.py  # Uses defaults
"""

import argparse
import json

# Model costs (per call, approximate)
MODEL_COSTS = {
    'nano': 0.0001,          # groq-fast, groq-llama
    'haiku': 0.0025,         # claude-haiku-4
    'mistral-large': 0.004,  # mistral-large-2512
    'sonnet': 0.015,         # claude-sonnet-4-5
    'opus': 0.075,           # claude-opus-4-6
}

# Default task distribution (based on real production analysis)
DEFAULT_DISTRIBUTION = {
    'heartbeat': 0.40,           # 40% of calls
    'simple_data': 0.10,         # 10%
    'chat': 0.20,                # 20%
    'community': 0.15,           # 15%
    'editorial': 0.10,           # 10%
    'strategic': 0.05,           # 5%
}

# Model routing (optimized strategy)
OPTIMIZED_ROUTING = {
    'heartbeat': 'nano',
    'simple_data': 'haiku',
    'chat': 'mistral-large',
    'community': 'sonnet',
    'editorial': 'sonnet',
    'strategic': 'opus',
}

# Blanket downgrade (for comparison)
HAIKU_EVERYWHERE = {
    'heartbeat': 'haiku',
    'simple_data': 'haiku',
    'chat': 'haiku',
    'community': 'haiku',
    'editorial': 'haiku',
    'strategic': 'haiku',
}

# All Sonnet (baseline)
SONNET_EVERYWHERE = {
    'heartbeat': 'sonnet',
    'simple_data': 'sonnet',
    'chat': 'sonnet',
    'community': 'sonnet',
    'editorial': 'sonnet',
    'strategic': 'sonnet',
}


def calculate_monthly_cost(total_tasks, distribution, routing):
    """Calculate monthly cost given task distribution and model routing"""
    cost = 0
    breakdown = {}
    
    for task_type, percentage in distribution.items():
        task_count = total_tasks * percentage
        model = routing[task_type]
        cost_per_task = MODEL_COSTS[model]
        task_cost = task_count * cost_per_task
        
        breakdown[task_type] = {
            'count': task_count,
            'model': model,
            'cost_per_task': cost_per_task,
            'total_cost': task_cost,
        }
        
        cost += task_cost
    
    return cost, breakdown


def calculate_heartbeat_cost(interval_minutes, model='nano'):
    """Calculate monthly heartbeat cost"""
    # Calls per day = 1440 minutes / interval
    calls_per_day = 1440 / interval_minutes
    calls_per_month = calls_per_day * 30
    cost_per_call = MODEL_COSTS[model]
    return calls_per_month * cost_per_call, calls_per_month


def print_breakdown(label, cost, breakdown):
    """Pretty print cost breakdown"""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    
    for task_type, details in breakdown.items():
        print(f"\n{task_type.upper()}")
        print(f"  Count: {details['count']:.0f} tasks")
        print(f"  Model: {details['model']}")
        print(f"  Cost per task: ${details['cost_per_task']:.4f}")
        print(f"  Total: ${details['total_cost']:.2f}")
    
    print(f"\n{'─'*60}")
    print(f"TOTAL MONTHLY COST: ${cost:.2f}")
    print(f"TOTAL ANNUAL COST: ${cost * 12:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description='Calculate OpenClaw monthly costs based on usage patterns'
    )
    parser.add_argument(
        '--tasks',
        type=int,
        default=100,
        help='Total tasks per month (excluding heartbeats). Default: 100'
    )
    parser.add_argument(
        '--heartbeat-interval',
        type=int,
        default=30,
        help='Heartbeat polling interval in minutes. Default: 30'
    )
    parser.add_argument(
        '--custom-distribution',
        type=str,
        help='Custom task distribution as JSON. Example: \'{"chat": 0.5, "editorial": 0.5}\''
    )
    
    args = parser.parse_args()
    
    # Parse custom distribution if provided
    distribution = DEFAULT_DISTRIBUTION
    if args.custom_distribution:
        try:
            distribution = json.loads(args.custom_distribution)
            # Validate it sums to 1.0
            total = sum(distribution.values())
            if abs(total - 1.0) > 0.01:
                print(f"⚠️  Warning: Distribution sums to {total}, not 1.0. Normalizing...")
                distribution = {k: v/total for k, v in distribution.items()}
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON for custom distribution")
            return
    
    print("\n🧮 OpenClaw Cost Calculator")
    print(f"\nAssumptions:")
    print(f"  - Tasks per month: {args.tasks}")
    print(f"  - Heartbeat interval: {args.heartbeat_interval} minutes")
    print(f"  - Distribution: {distribution}")
    
    # Calculate costs for each strategy
    optimized_cost, optimized_breakdown = calculate_monthly_cost(
        args.tasks, distribution, OPTIMIZED_ROUTING
    )
    
    haiku_cost, haiku_breakdown = calculate_monthly_cost(
        args.tasks, distribution, HAIKU_EVERYWHERE
    )
    
    sonnet_cost, sonnet_breakdown = calculate_monthly_cost(
        args.tasks, distribution, SONNET_EVERYWHERE
    )
    
    # Add heartbeat costs
    heartbeat_nano_cost, heartbeat_calls = calculate_heartbeat_cost(
        args.heartbeat_interval, 'nano'
    )
    heartbeat_sonnet_cost, _ = calculate_heartbeat_cost(
        args.heartbeat_interval, 'sonnet'
    )
    
    optimized_total = optimized_cost + heartbeat_nano_cost
    haiku_total = haiku_cost + heartbeat_nano_cost  # Assume they optimize heartbeats too
    sonnet_total = sonnet_cost + heartbeat_sonnet_cost
    
    # Print breakdowns
    print_breakdown("STRATEGY 1: OPTIMIZED ROUTING (Recommended)", optimized_cost, optimized_breakdown)
    print(f"\n  + Heartbeat cost (Nano, {args.heartbeat_interval}min intervals): ${heartbeat_nano_cost:.2f}")
    print(f"  = TOTAL WITH HEARTBEATS: ${optimized_total:.2f}/month (${optimized_total*12:.2f}/year)")
    
    print_breakdown("STRATEGY 2: HAIKU EVERYWHERE (Blanket Downgrade)", haiku_cost, haiku_breakdown)
    print(f"\n  + Heartbeat cost (Nano, {args.heartbeat_interval}min intervals): ${heartbeat_nano_cost:.2f}")
    print(f"  = TOTAL WITH HEARTBEATS: ${haiku_total:.2f}/month (${haiku_total*12:.2f}/year)")
    print(f"\n  ⚠️  WARNING: This assumes Haiku quality is acceptable for all tasks.")
    print(f"      Real-world testing showed 67-75% quality degradation (see Case 5).")
    
    print_breakdown("STRATEGY 3: SONNET EVERYWHERE (Baseline)", sonnet_cost, sonnet_breakdown)
    print(f"\n  + Heartbeat cost (Sonnet, {args.heartbeat_interval}min intervals): ${heartbeat_sonnet_cost:.2f}")
    print(f"  = TOTAL WITH HEARTBEATS: ${sonnet_total:.2f}/month (${sonnet_total*12:.2f}/year)")
    
    # Comparison
    print(f"\n{'='*60}")
    print("SAVINGS COMPARISON")
    print(f"{'='*60}")
    
    savings_optimized = sonnet_total - optimized_total
    savings_haiku = sonnet_total - haiku_total
    
    print(f"\nOptimized Routing vs All Sonnet:")
    print(f"  Monthly: ${savings_optimized:.2f} ({savings_optimized/sonnet_total*100:.1f}%)")
    print(f"  Annual: ${savings_optimized*12:.2f}")
    
    print(f"\nHaiku Everywhere vs All Sonnet:")
    print(f"  Monthly: ${savings_haiku:.2f} ({savings_haiku/sonnet_total*100:.1f}%)")
    print(f"  Annual: ${savings_haiku*12:.2f}")
    print(f"  ⚠️  But with 67-75% quality loss on complex tasks")
    
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    print("\n1. Start with OPTIMIZED ROUTING")
    print("   - Saves money without sacrificing quality")
    print("   - Tested on 99 real production tasks")
    print(f"   - Annual savings: ${savings_optimized*12:.0f} ({savings_optimized/sonnet_total*100:.0f}%)")
    
    print("\n2. Optimize heartbeats FIRST")
    heartbeat_savings = heartbeat_sonnet_cost - heartbeat_nano_cost
    print(f"   - Switch heartbeats to Nano: ${heartbeat_savings:.2f}/mo savings")
    print(f"   - That's ${heartbeat_savings*12:.0f}/year for 5 minutes of work")
    print(f"   - ROI: ${heartbeat_savings*12/0.083:.0f}/hour")
    
    print("\n3. Audit your task types")
    print("   - Use scripts/analyze-task-complexity.py")
    print("   - Don't assume 80% can use Haiku (real number: 25-33%)")
    
    print("\n4. Monitor quality, not just cost")
    print("   - Track rejection rate (how often you edit/reject AI output)")
    print("   - If >30% rejection rate → upgrade model for that task type")
    
    print(f"\n{'='*60}")
    print("\nNext steps:")
    print("  1. Run: bash scripts/enable-optimized-embeddings.sh")
    print("  2. Configure heartbeats to use Nano model")
    print("  3. Implement model routing rules (see configs/model-routing-rules.json)")
    print("  4. Monitor costs for 2 weeks")
    print("  5. Adjust routing based on quality + cost data")
    print("")


if __name__ == '__main__':
    main()
