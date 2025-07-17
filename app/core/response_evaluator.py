"""
LLM-Based Response Evaluator for Al Essa Kuwait Chatbot
Evaluates the accuracy, relevance, and quality of chatbot responses.
"""

from typing import Dict, List, Any, Optional
from app.core.llm import llm
from langchain.schema import HumanMessage, SystemMessage
import logging
import json

logger = logging.getLogger(__name__)

EVALUATOR_PROMPT = """You are an expert evaluator for the Al Essa Kuwait Virtual Assistant chatbot. Your job is to assess the quality, accuracy, and relevance of chatbot responses.

**🎯 EVALUATION CRITERIA**

**1. RELEVANCE (0-100%)**
- Does the response directly address the user's query?
- Are the recommended products relevant to what the user asked for?
- Is the response on-topic and focused?

**2. ACCURACY (0-100%)**
- Are the product recommendations appropriate for the query?
- Is the medical/sales advice accurate and helpful?
- Are there any obvious errors or mismatches?

**3. COMPLETENESS (0-100%)**
- Does the response fully answer the user's question?
- Are important details included (pricing, availability, etc.)?
- Is the response comprehensive enough?

**4. PRODUCT RELEVANCE (0-100%)**
- Do ALL recommended products match the user's request?
- Are there any irrelevant or completely unrelated products?
- Are the products appropriately filtered and sorted?

**5. AGENT ROUTING (0-100%)**
- Was the query routed to the correct agent (Doctor vs Sales)?
- Is the response style appropriate for the agent type?
- Are medical disclaimers included when needed?

**⚠️ CRITICAL ISSUES TO FLAG:**
- Irrelevant product recommendations (e.g., breast pumps for wheelchair queries)
- Medical advice without proper disclaimers
- Wrong agent routing (medical query to sales agent)
- Pricing errors or missing product information
- Inappropriate or unsafe recommendations

**📊 OUTPUT FORMAT:**
Provide your evaluation as a JSON object with the following structure:
{
    "overall_score": 85,
    "relevance": 90,
    "accuracy": 85, 
    "completeness": 80,
    "product_relevance": 75,
    "agent_routing": 95,
    "critical_issues": ["Issue 1", "Issue 2"],
    "strengths": ["Strength 1", "Strength 2"],
    "improvements": ["Suggestion 1", "Suggestion 2"],
    "summary": "Brief overall assessment"
}

**🔍 ANALYSIS FOCUS:**
- Pay special attention to product-query matching
- Verify that products are relevant to the user's actual need
- Check for any obvious mismatches or errors
- Assess whether the response would be helpful to a real customer"""

class ResponseEvaluator:
    """LLM-based evaluator for chatbot responses."""
    
    def __init__(self):
        """Initialize the response evaluator."""
        self.llm = llm
        
    def evaluate_response(self, user_query: str, bot_response: str, 
                         products: List[Dict] = None, agent_type: str = None,
                         workflow_steps: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate a chatbot response for quality, accuracy, and relevance.
        
        Args:
            user_query: The original user query
            bot_response: The chatbot's response
            products: List of recommended products
            agent_type: Which agent handled the query (doctor/sales)
            workflow_steps: Steps taken in the workflow
            
        Returns:
            Dictionary containing evaluation scores and feedback
        """
        try:
            # Prepare evaluation context
            evaluation_context = self._build_evaluation_context(
                user_query, bot_response, products, agent_type, workflow_steps
            )
            
            # Create evaluation prompt
            messages = [
                SystemMessage(content=EVALUATOR_PROMPT),
                HumanMessage(content=evaluation_context)
            ]
            
            # Get LLM evaluation
            response = self.llm.invoke(messages)
            evaluation_text = response.content
            
            # Parse JSON response
            try:
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON evaluation, using fallback")
                evaluation = self._parse_text_evaluation(evaluation_text)
            
            # Add metadata
            evaluation["evaluator_version"] = "1.0"
            evaluation["evaluation_timestamp"] = self._get_timestamp()
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Response evaluation failed: {e}")
            return self._get_fallback_evaluation(str(e))
    
    def _build_evaluation_context(self, user_query: str, bot_response: str,
                                 products: List[Dict], agent_type: str,
                                 workflow_steps: List[str]) -> str:
        """Build the context for evaluation."""
        context = f"""**EVALUATION REQUEST**

**User Query:** "{user_query}"

**Agent Type:** {agent_type or 'Unknown'}

**Workflow Steps:** {' → '.join(workflow_steps or ['Unknown'])}

**Bot Response:**
{bot_response}

**Recommended Products ({len(products or [])} total):**"""
        
        if products:
            for i, product in enumerate(products[:10], 1):  # Show first 10 products
                name = product.get('name', 'Unknown Product')
                price = product.get('price', 'Unknown')
                currency = product.get('currency', 'KWD')
                context += f"\n{i}. {name} - {price} {currency}"
                
            if len(products) > 10:
                context += f"\n... and {len(products) - 10} more products"
        else:
            context += "\nNo products recommended"
        
        context += "\n\n**PLEASE EVALUATE THIS RESPONSE:**"
        return context
    
    def _parse_text_evaluation(self, evaluation_text: str) -> Dict[str, Any]:
        """Parse evaluation from text if JSON parsing fails."""
        # Simple fallback parsing
        lines = evaluation_text.split('\n')
        evaluation = {
            "overall_score": 50,
            "relevance": 50,
            "accuracy": 50,
            "completeness": 50,
            "product_relevance": 50,
            "agent_routing": 50,
            "critical_issues": [],
            "strengths": [],
            "improvements": [],
            "summary": "Evaluation parsing failed, manual review needed"
        }
        
        # Try to extract scores from text
        for line in lines:
            if "overall" in line.lower() and any(char.isdigit() for char in line):
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    if 0 <= score <= 100:
                        evaluation["overall_score"] = score
                except:
                    pass
                    
        return evaluation
    
    def _get_fallback_evaluation(self, error: str) -> Dict[str, Any]:
        """Get fallback evaluation when evaluation fails."""
        return {
            "overall_score": 0,
            "relevance": 0,
            "accuracy": 0,
            "completeness": 0,
            "product_relevance": 0,
            "agent_routing": 0,
            "critical_issues": [f"Evaluation failed: {error}"],
            "strengths": [],
            "improvements": ["Fix evaluation system"],
            "summary": "Evaluation system error - manual review required",
            "evaluator_version": "1.0",
            "evaluation_timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def format_evaluation_summary(self, evaluation: Dict[str, Any]) -> str:
        """Format evaluation results for display."""
        if not evaluation:
            return "❌ Evaluation failed"
        
        overall = evaluation.get('overall_score', 0)
        
        # Determine overall quality
        if overall >= 90:
            quality_emoji = "🟢"
            quality_text = "EXCELLENT"
        elif overall >= 75:
            quality_emoji = "🟡"
            quality_text = "GOOD"
        elif overall >= 60:
            quality_emoji = "🟠"
            quality_text = "FAIR"
        else:
            quality_emoji = "🔴"
            quality_text = "POOR"
        
        summary = f"\n📊 **RESPONSE EVALUATION**\n"
        summary += f"{quality_emoji} **Overall Quality: {overall}% ({quality_text})**\n\n"
        
        # Detailed scores
        summary += "**Detailed Scores:**\n"
        summary += f"• Relevance: {evaluation.get('relevance', 0)}%\n"
        summary += f"• Accuracy: {evaluation.get('accuracy', 0)}%\n"
        summary += f"• Completeness: {evaluation.get('completeness', 0)}%\n"
        summary += f"• Product Relevance: {evaluation.get('product_relevance', 0)}%\n"
        summary += f"• Agent Routing: {evaluation.get('agent_routing', 0)}%\n"
        
        # Critical issues
        issues = evaluation.get('critical_issues', [])
        if issues:
            summary += f"\n⚠️  **Critical Issues:**\n"
            for issue in issues[:3]:  # Show first 3 issues
                summary += f"• {issue}\n"
        
        # Strengths
        strengths = evaluation.get('strengths', [])
        if strengths:
            summary += f"\n✅ **Strengths:**\n"
            for strength in strengths[:2]:  # Show first 2 strengths
                summary += f"• {strength}\n"
        
        # Summary
        eval_summary = evaluation.get('summary', '')
        if eval_summary:
            summary += f"\n💬 **Summary:** {eval_summary}\n"
        
        return summary

# Global evaluator instance
response_evaluator = ResponseEvaluator()