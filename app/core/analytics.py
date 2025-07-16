"""
Analytics and Monitoring System for Al Essa Kuwait Chatbot
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os
from collections import defaultdict, Counter
import threading

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Metrics for individual queries."""
    query: str
    session_id: str
    agent_type: str
    response_time: float
    products_found: int
    cache_hit: bool
    success: bool
    error_message: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class SessionMetrics:
    """Metrics for user sessions."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_products_viewed: int = 0
    agent_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.agent_usage is None:
            self.agent_usage = defaultdict(int)

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    agent_usage: Dict[str, int] = None
    error_counts: Dict[str, int] = None
    peak_concurrent_users: int = 0
    current_concurrent_users: int = 0
    
    def __post_init__(self):
        if self.agent_usage is None:
            self.agent_usage = defaultdict(int)
        if self.error_counts is None:
            self.error_counts = defaultdict(int)

class AnalyticsManager:
    """Manages analytics and monitoring for the chatbot system."""
    
    def __init__(self, data_dir: str = "analytics"):
        """Initialize analytics manager."""
        self.data_dir = data_dir
        self.metrics_file = os.path.join(data_dir, "metrics.json")
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.queries_file = os.path.join(data_dir, "queries.json")
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.system_metrics = self._load_system_metrics()
        self.active_sessions = {}
        self.query_history = []
        
        # Threading for concurrent access
        self.lock = threading.Lock()
        
        # Load existing data
        self._load_existing_data()
        
    def _load_system_metrics(self) -> SystemMetrics:
        """Load system metrics from file."""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    return SystemMetrics(**data)
        except Exception as e:
            logger.warning(f"Failed to load system metrics: {e}")
        return SystemMetrics()
    
    def _save_system_metrics(self) -> None:
        """Save system metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(asdict(self.system_metrics), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save system metrics: {e}")
    
    def _load_existing_data(self) -> None:
        """Load existing analytics data."""
        # Load sessions
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    for session_data in sessions_data:
                        session = SessionMetrics(**session_data)
                        if session.end_time is None:  # Active session
                            self.active_sessions[session.session_id] = session
        except Exception as e:
            logger.warning(f"Failed to load sessions: {e}")
        
        # Load recent queries (last 1000)
        try:
            if os.path.exists(self.queries_file):
                with open(self.queries_file, 'r') as f:
                    queries_data = json.load(f)
                    self.query_history = [QueryMetrics(**q) for q in queries_data[-1000:]]
        except Exception as e:
            logger.warning(f"Failed to load queries: {e}")
    
    def _save_sessions(self) -> None:
        """Save sessions to file."""
        try:
            all_sessions = list(self.active_sessions.values())
            with open(self.sessions_file, 'w') as f:
                json.dump([asdict(session) for session in all_sessions], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def _save_queries(self) -> None:
        """Save recent queries to file."""
        try:
            with open(self.queries_file, 'w') as f:
                json.dump([asdict(query) for query in self.query_history[-1000:]], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queries: {e}")
    
    def start_session(self, session_id: str) -> None:
        """Start tracking a new session."""
        with self.lock:
            if session_id not in self.active_sessions:
                session = SessionMetrics(
                    session_id=session_id,
                    start_time=time.time()
                )
                self.active_sessions[session_id] = session
                self.system_metrics.current_concurrent_users = len(self.active_sessions)
                self.system_metrics.peak_concurrent_users = max(
                    self.system_metrics.peak_concurrent_users,
                    self.system_metrics.current_concurrent_users
                )
                self._save_sessions()
    
    def end_session(self, session_id: str) -> None:
        """End tracking a session."""
        with self.lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.end_time = time.time()
                self.system_metrics.current_concurrent_users = len(self.active_sessions) - 1
                del self.active_sessions[session_id]
                self._save_sessions()
    
    def record_query(self, metrics: QueryMetrics) -> None:
        """Record metrics for a query."""
        with self.lock:
            # Update system metrics
            self.system_metrics.total_queries += 1
            if metrics.success:
                self.system_metrics.successful_queries += 1
            else:
                self.system_metrics.failed_queries += 1
                if metrics.error_message:
                    self.system_metrics.error_counts[metrics.error_message] += 1
            
            # Update agent usage
            self.system_metrics.agent_usage[metrics.agent_type] += 1
            
            # Update cache hit rate
            total_queries = self.system_metrics.total_queries
            cache_hits = sum(1 for q in self.query_history if q.cache_hit)
            self.system_metrics.cache_hit_rate = cache_hits / total_queries if total_queries > 0 else 0.0
            
            # Update average response time
            total_time = sum(q.response_time for q in self.query_history) + metrics.response_time
            self.system_metrics.average_response_time = total_time / (len(self.query_history) + 1)
            
            # Update session metrics
            if metrics.session_id in self.active_sessions:
                session = self.active_sessions[metrics.session_id]
                session.total_queries += 1
                if metrics.success:
                    session.successful_queries += 1
                else:
                    session.failed_queries += 1
                session.total_products_viewed += metrics.products_found
                session.agent_usage[metrics.agent_type] += 1
            
            # Add to query history
            self.query_history.append(metrics)
            if len(self.query_history) > 1000:
                self.query_history = self.query_history[-1000:]
            
            # Save data
            self._save_system_metrics()
            self._save_queries()
            self._save_sessions()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        with self.lock:
            # Calculate success rate
            success_rate = (
                self.system_metrics.successful_queries / self.system_metrics.total_queries
                if self.system_metrics.total_queries > 0 else 0.0
            )
            
            # Get recent performance (last hour)
            one_hour_ago = time.time() - 3600
            recent_queries = [
                q for q in self.query_history
                if q.timestamp > one_hour_ago
            ]
            
            recent_success_rate = (
                sum(1 for q in recent_queries if q.success) / len(recent_queries)
                if recent_queries else 0.0
            )
            
            recent_avg_response_time = (
                sum(q.response_time for q in recent_queries) / len(recent_queries)
                if recent_queries else 0.0
            )
            
            return {
                "overall_success_rate": success_rate,
                "recent_success_rate": recent_success_rate,
                "average_response_time": self.system_metrics.average_response_time,
                "recent_average_response_time": recent_avg_response_time,
                "cache_hit_rate": self.system_metrics.cache_hit_rate,
                "current_concurrent_users": self.system_metrics.current_concurrent_users,
                "peak_concurrent_users": self.system_metrics.peak_concurrent_users,
                "total_queries": self.system_metrics.total_queries,
                "agent_usage": dict(self.system_metrics.agent_usage),
                "top_errors": dict(Counter(self.system_metrics.error_counts).most_common(5)),
                "recent_queries_count": len(recent_queries)
            }
    
    def get_user_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific user session."""
        with self.lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session_queries = [
                    q for q in self.query_history
                    if q.session_id == session_id
                ]
                
                return {
                    "session_id": session_id,
                    "start_time": session.start_time,
                    "total_queries": session.total_queries,
                    "successful_queries": session.successful_queries,
                    "failed_queries": session.failed_queries,
                    "total_products_viewed": session.total_products_viewed,
                    "agent_usage": dict(session.agent_usage),
                    "average_response_time": (
                        sum(q.response_time for q in session_queries) / len(session_queries)
                        if session_queries else 0.0
                    ),
                    "cache_hit_rate": (
                        sum(1 for q in session_queries if q.cache_hit) / len(session_queries)
                        if session_queries else 0.0
                    )
                }
            return None
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular queries."""
        with self.lock:
            query_counts = Counter(q.query for q in self.query_history)
            return [
                {"query": query, "count": count}
                for query, count in query_counts.most_common(limit)
            ]
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """Get performance trends over time."""
        with self.lock:
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Group queries by hour
            hourly_data = defaultdict(list)
            for query in self.query_history:
                if start_time <= query.timestamp <= end_time:
                    hour = int(query.timestamp // 3600) * 3600
                    hourly_data[hour].append(query)
            
            # Calculate metrics for each hour
            hours_list = []
            success_rates = []
            response_times = []
            query_counts = []
            
            for hour in sorted(hourly_data.keys()):
                queries = hourly_data[hour]
                hours_list.append(datetime.fromtimestamp(hour).strftime("%H:%M"))
                success_rates.append(
                    sum(1 for q in queries if q.success) / len(queries)
                    if queries else 0.0
                )
                response_times.append(
                    sum(q.response_time for q in queries) / len(queries)
                    if queries else 0.0
                )
                query_counts.append(len(queries))
            
            return {
                "hours": hours_list,
                "success_rates": success_rates,
                "response_times": response_times,
                "query_counts": query_counts
            }

# Initialize global analytics manager
analytics_manager = AnalyticsManager()