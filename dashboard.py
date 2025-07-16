#!/usr/bin/env python3
"""
Al Essa Kuwait Chatbot Dashboard
Simple dashboard to view system analytics and performance metrics.
"""

import requests
import json
import time
from datetime import datetime
import os

DASHBOARD_CONFIG = {
    "api_base_url": "http://localhost:8000",
    "refresh_interval": 30,  # seconds
    "max_queries_display": 10
}

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Print dashboard header."""
    print("=" * 80)
    print("🌟 Al Essa Kuwait Virtual Assistant - System Dashboard")
    print("=" * 80)
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def get_api_data(endpoint):
    """Get data from API endpoint."""
    try:
        response = requests.get(f"{DASHBOARD_CONFIG['api_base_url']}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error fetching data from {endpoint}: {e}")
        return None

def display_system_health():
    """Display system health metrics."""
    print("\n📊 SYSTEM HEALTH")
    print("-" * 40)
    
    health_data = get_api_data("/analytics/health")
    if health_data:
        print(f"Overall Success Rate: {health_data.get('overall_success_rate', 0):.2%}")
        print(f"Recent Success Rate: {health_data.get('recent_success_rate', 0):.2%}")
        print(f"Average Response Time: {health_data.get('average_response_time', 0):.2f}s")
        print(f"Recent Avg Response Time: {health_data.get('recent_average_response_time', 0):.2f}s")
        print(f"Cache Hit Rate: {health_data.get('cache_hit_rate', 0):.2%}")
        print(f"Current Users: {health_data.get('current_concurrent_users', 0)}")
        print(f"Peak Users: {health_data.get('peak_concurrent_users', 0)}")
        print(f"Total Queries: {health_data.get('total_queries', 0)}")
        print(f"Recent Queries: {health_data.get('recent_queries_count', 0)}")
    else:
        print("❌ Unable to fetch system health data")

def display_agent_usage():
    """Display agent usage statistics."""
    print("\n🤖 AGENT USAGE")
    print("-" * 40)
    
    health_data = get_api_data("/analytics/health")
    if health_data and 'agent_usage' in health_data:
        agent_usage = health_data['agent_usage']
        if agent_usage:
            for agent, count in agent_usage.items():
                print(f"{agent.title()}: {count}")
        else:
            print("No agent usage data available")
    else:
        print("❌ Unable to fetch agent usage data")

def display_popular_queries():
    """Display popular queries."""
    print("\n🔥 POPULAR QUERIES")
    print("-" * 40)
    
    queries_data = get_api_data(f"/analytics/popular-queries?limit={DASHBOARD_CONFIG['max_queries_display']}")
    if queries_data:
        for i, query_data in enumerate(queries_data, 1):
            query = query_data.get('query', 'Unknown')
            count = query_data.get('count', 0)
            print(f"{i:2d}. {query[:50]}{'...' if len(query) > 50 else ''} ({count})")
    else:
        print("❌ Unable to fetch popular queries data")

def display_cache_stats():
    """Display cache statistics."""
    print("\n💾 CACHE STATISTICS")
    print("-" * 40)
    
    cache_data = get_api_data("/cache/stats")
    if cache_data:
        print(f"Product Cache Size: {cache_data.get('product_cache_size', 0)}")
        print(f"LLM Cache Size: {cache_data.get('llm_cache_size', 0)}")
        print(f"Session Cache Size: {cache_data.get('session_cache_size', 0)}")
        print(f"Total Cache Size: {cache_data.get('total_cache_size', 0)}")
    else:
        print("❌ Unable to fetch cache statistics")

def display_performance_trends():
    """Display performance trends."""
    print("\n📈 PERFORMANCE TRENDS (Last 24 Hours)")
    print("-" * 40)
    
    trends_data = get_api_data("/analytics/trends?hours=24")
    if trends_data and 'hours' in trends_data:
        hours = trends_data['hours']
        success_rates = trends_data.get('success_rates', [])
        response_times = trends_data.get('response_times', [])
        query_counts = trends_data.get('query_counts', [])
        
        if hours:
            print("Hour    | Success Rate | Avg Response | Queries")
            print("-" * 50)
            for i, hour in enumerate(hours):
                success_rate = success_rates[i] if i < len(success_rates) else 0
                response_time = response_times[i] if i < len(response_times) else 0
                query_count = query_counts[i] if i < len(query_counts) else 0
                print(f"{hour:7s} | {success_rate:11.1%} | {response_time:11.2f}s | {query_count:7d}")
    else:
        print("❌ Unable to fetch performance trends data")

def display_error_summary():
    """Display error summary."""
    print("\n⚠️  ERROR SUMMARY")
    print("-" * 40)
    
    health_data = get_api_data("/analytics/health")
    if health_data and 'top_errors' in health_data:
        top_errors = health_data['top_errors']
        if top_errors:
            for error, count in top_errors.items():
                print(f"{error[:60]}{'...' if len(error) > 60 else ''} ({count})")
        else:
            print("✅ No errors recorded")
    else:
        print("❌ Unable to fetch error summary data")

def main():
    """Main dashboard loop."""
    print("Starting Al Essa Kuwait Chatbot Dashboard...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            clear_screen()
            print_header()
            
            display_system_health()
            display_agent_usage()
            display_popular_queries()
            display_cache_stats()
            display_performance_trends()
            display_error_summary()
            
            print(f"\n🔄 Refreshing in {DASHBOARD_CONFIG['refresh_interval']} seconds...")
            time.sleep(DASHBOARD_CONFIG['refresh_interval'])
            
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")

if __name__ == "__main__":
    main()