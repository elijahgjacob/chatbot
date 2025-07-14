# app/agents/agent_handler.py
"""
Agent handler for orchestrating the chatbot workflow and tools.
"""
import logging
from app.tools.product_search import product_search_tool
from app.tools.response_filter import response_filter_tool
from app.tools.query_refinement import query_refinement_tool

AVAILABLE_TOOLS = [product_search_tool, response_filter_tool, query_refinement_tool]

logger = logging.getLogger(__name__)

# Example: You can add agent orchestration logic here, or import and use in main agent class 