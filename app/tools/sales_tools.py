"""
Specialized Sales Tools for Al Essa Kuwait Sales Agent
"""
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json

from app.core.scraping import get_product_prices_from_search
from app.core.llm import get_llm_response

logger = logging.getLogger(__name__)


class PriceComparisonInput(BaseModel):
    products: List[str] = Field(description="List of product names to compare prices for")
    budget: Optional[float] = Field(default=None, description="Customer's budget in KWD")


class PriceComparisonTool(BaseTool):
    name: str = "price_comparison"
    description: str = "Compare prices of multiple products and provide best value recommendations within customer budget. Use when customer wants to compare different products or find the most cost-effective option."
    args_schema: type = PriceComparisonInput

    def _run(self, products: List[str], budget: Optional[float] = None) -> Dict[str, Any]:
        """Compare prices across multiple products"""
        logger.info(f"PriceComparisonTool: Comparing prices for {products}")
        
        try:
            comparison_results = []
            all_products = []
            
            # Get products for each search term
            for product_query in products:
                result = get_product_prices_from_search(product_query)
                product_list = result.get('products', [])
                
                if product_list:
                    # Get best product for this category
                    best_product = min(product_list, key=lambda x: x.get('price', float('inf')))
                    comparison_results.append({
                        'category': product_query,
                        'best_option': best_product,
                        'total_found': len(product_list)
                    })
                    all_products.extend(product_list)
            
            # Filter by budget if provided
            if budget:
                affordable_products = [p for p in all_products if p.get('price', float('inf')) <= budget]
            else:
                affordable_products = all_products
            
            # Create comparison summary
            comparison_summary = self._create_comparison_summary(comparison_results, budget, affordable_products)
            
            return {
                "success": True,
                "comparison_results": comparison_results,
                "affordable_products": affordable_products,
                "budget": budget,
                "summary": comparison_summary,
                "total_products_compared": len(all_products)
            }
            
        except Exception as e:
            logger.error(f"Error in price comparison: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Unable to compare prices at the moment. Let me help you find individual product information."
            }
    
    def _create_comparison_summary(self, results: List[Dict], budget: Optional[float], affordable: List[Dict]) -> str:
        """Create a sales-focused comparison summary"""
        if not results:
            return "I couldn't find products to compare. Let me search for specific items for you."
        
        summary = "🔍 **Price Comparison Results**\n\n"
        
        for result in results:
            best = result['best_option']
            summary += f"**{result['category'].title()}:**\n"
            summary += f"• Best Value: {best['name']} - {best['price']} KWD\n"
            summary += f"• Total Options: {result['total_found']} products available\n\n"
        
        if budget:
            summary += f"💰 **Within Your {budget} KWD Budget:**\n"
            summary += f"• {len(affordable)} products match your budget\n"
            summary += f"• Savings opportunity: Up to {budget - min([p['price'] for p in affordable], default=budget):.1f} KWD under budget\n\n"
        
        summary += "✅ **My Recommendation:** Based on value for money and customer reviews, I recommend starting with the products highlighted above. Would you like detailed specifications for any of these options?"
        
        return summary


class ProductRecommendationInput(BaseModel):
    customer_needs: str = Field(description="Description of customer needs and requirements")
    budget: Optional[float] = Field(default=None, description="Customer's budget in KWD")
    category: Optional[str] = Field(default=None, description="Product category (medical, appliances, technology)")


class ProductRecommendationTool(BaseTool):
    name: str = "product_recommendation"
    description: str = "Generate personalized product recommendations based on customer needs, budget, and preferences. Use when customer is looking for suggestions or doesn't know exactly what they want."
    args_schema: type = ProductRecommendationInput

    def _run(self, customer_needs: str, budget: Optional[float] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Generate personalized product recommendations"""
        logger.info(f"ProductRecommendationTool: Generating recommendations for '{customer_needs}'")
        
        try:
            # Extract key terms from customer needs
            search_terms = self._extract_search_terms(customer_needs, category)
            
            recommendations = []
            for term in search_terms:
                result = get_product_prices_from_search(term)
                products = result.get('products', [])
                
                # Filter by budget if provided
                if budget:
                    products = [p for p in products if p.get('price', float('inf')) <= budget]
                
                if products:
                    # Sort by price (ascending) and take top 3
                    products.sort(key=lambda x: x.get('price', 0))
                    recommendations.extend(products[:3])
            
            # Remove duplicates and limit to top 6 recommendations
            unique_recommendations = []
            seen_names = set()
            for product in recommendations:
                if product['name'] not in seen_names:
                    unique_recommendations.append(product)
                    seen_names.add(product['name'])
                if len(unique_recommendations) >= 6:
                    break
            
            # Generate sales-focused recommendation text
            recommendation_text = self._create_recommendation_text(unique_recommendations, customer_needs, budget)
            
            return {
                "success": True,
                "recommendations": unique_recommendations,
                "customer_needs": customer_needs,
                "budget": budget,
                "recommendation_text": recommendation_text,
                "total_options": len(unique_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in product recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Let me help you find products by searching our catalog directly."
            }
    
    def _extract_search_terms(self, needs: str, category: Optional[str]) -> List[str]:
        """Extract relevant search terms from customer needs"""
        needs_lower = needs.lower()
        search_terms = []
        
        # Medical equipment terms
        if any(word in needs_lower for word in ['mobility', 'walk', 'move', 'wheelchair', 'crutch']):
            search_terms.extend(['wheelchair', 'mobility aids'])
        
        # Appliance terms
        if any(word in needs_lower for word in ['cold', 'food', 'kitchen', 'refrigerat']):
            search_terms.append('refrigerator')
        if any(word in needs_lower for word in ['cool', 'hot', 'temperature', 'air']):
            search_terms.append('air conditioner')
        if any(word in needs_lower for word in ['clean', 'vacuum', 'dust']):
            search_terms.append('vacuum cleaner')
        if any(word in needs_lower for word in ['wash', 'clothes', 'laundry']):
            search_terms.append('washing machine')
        
        # If category is specified, add category-specific terms
        if category:
            if category == 'medical':
                search_terms.extend(['medical equipment', 'healthcare'])
            elif category == 'appliances':
                search_terms.extend(['home appliances', 'kitchen appliances'])
        
        # Default search if no specific terms found
        if not search_terms:
            search_terms = [needs.split()[0] if needs.split() else 'products']
        
        return search_terms[:3]  # Limit to 3 search terms
    
    def _create_recommendation_text(self, products: List[Dict], needs: str, budget: Optional[float]) -> str:
        """Create sales-focused recommendation text"""
        if not products:
            return "I'd love to help you find the perfect solution! Let me search our catalog for products that match your specific needs."
        
        text = f"🎯 **Perfect Recommendations for You!**\n\n"
        text += f"Based on your needs: '{needs}'\n\n"
        
        for i, product in enumerate(products[:3], 1):
            text += f"**{i}. {product['name']}** - {product['price']} KWD\n"
            text += f"   ✅ Excellent choice for your requirements\n"
            if product.get('vendor'):
                text += f"   🏷️ Brand: {product['vendor']}\n"
            text += f"   🔗 [View Details]({product.get('url', '#')})\n\n"
        
        if budget:
            affordable_count = len([p for p in products if p.get('price', 0) <= budget])
            text += f"💰 **Budget-Friendly:** {affordable_count} options within your {budget} KWD budget\n\n"
        
        text += "🚀 **Why Choose Al Essa Kuwait:**\n"
        text += "• Trusted quality and authentic products\n"
        text += "• Professional installation and support\n"
        text += "• Competitive pricing with warranty\n\n"
        text += "📞 Ready to order? I can help you complete your purchase today!"
        
        return text


class CustomerQualificationInput(BaseModel):
    conversation_history: str = Field(description="Recent conversation with the customer")


class CustomerQualificationTool(BaseTool):
    name: str = "customer_qualification"
    description: str = "Analyze customer conversation to identify their needs, budget, timeline, and buying readiness. Use to better understand and qualify the customer."
    args_schema: type = CustomerQualificationInput

    def _run(self, conversation_history: str) -> Dict[str, Any]:
        """Analyze customer conversation for qualification"""
        logger.info("CustomerQualificationTool: Analyzing customer qualification")
        
        try:
            qualification = self._analyze_customer_signals(conversation_history)
            qualification_summary = self._create_qualification_summary(qualification)
            
            return {
                "success": True,
                "qualification": qualification,
                "summary": qualification_summary,
                "next_steps": self._suggest_next_steps(qualification)
            }
            
        except Exception as e:
            logger.error(f"Error in customer qualification: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Let me ask you a few questions to better understand your needs."
            }
    
    def _analyze_customer_signals(self, conversation: str) -> Dict[str, Any]:
        """Analyze conversation for buying signals and qualification criteria"""
        conv_lower = conversation.lower()
        
        # Budget indicators
        budget_mentioned = any(word in conv_lower for word in ['budget', 'afford', 'cost', 'price', 'expensive', 'cheap', 'kwd'])
        
        # Urgency indicators
        urgency_level = 'low'
        if any(word in conv_lower for word in ['urgent', 'asap', 'immediately', 'today']):
            urgency_level = 'high'
        elif any(word in conv_lower for word in ['soon', 'this week', 'quickly']):
            urgency_level = 'medium'
        
        # Buying intent
        buying_intent = 'low'
        if any(word in conv_lower for word in ['buy', 'purchase', 'order', 'get one']):
            buying_intent = 'high'
        elif any(word in conv_lower for word in ['interested', 'need', 'want', 'looking for']):
            buying_intent = 'medium'
        
        # Decision maker
        decision_maker = any(word in conv_lower for word in ['i need', 'i want', 'i am', 'my decision'])
        
        # Pain points
        pain_points = []
        if any(word in conv_lower for word in ['problem', 'issue', 'broken', 'not working']):
            pain_points.append('current_product_issues')
        if any(word in conv_lower for word in ['upgrade', 'replace', 'old']):
            pain_points.append('replacement_needed')
        
        return {
            'budget_mentioned': budget_mentioned,
            'urgency_level': urgency_level,
            'buying_intent': buying_intent,
            'decision_maker': decision_maker,
            'pain_points': pain_points
        }
    
    def _create_qualification_summary(self, qualification: Dict[str, Any]) -> str:
        """Create qualification summary for sales strategy"""
        summary = "📋 **Customer Qualification Summary**\n\n"
        
        intent = qualification['buying_intent']
        urgency = qualification['urgency_level']
        
        summary += f"🎯 **Buying Intent:** {intent.title()}\n"
        summary += f"⏰ **Urgency Level:** {urgency.title()}\n"
        summary += f"💰 **Budget Discussion:** {'Yes' if qualification['budget_mentioned'] else 'Not yet'}\n"
        summary += f"🎯 **Decision Maker:** {'Likely' if qualification['decision_maker'] else 'Unknown'}\n"
        
        if qualification['pain_points']:
            summary += f"⚠️ **Pain Points:** {', '.join(qualification['pain_points'])}\n"
        
        return summary
    
    def _suggest_next_steps(self, qualification: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on qualification"""
        steps = []
        
        if not qualification['budget_mentioned']:
            steps.append("Discuss budget and financing options")
        
        if qualification['buying_intent'] == 'high':
            steps.append("Present specific product options and pricing")
            steps.append("Discuss delivery and installation")
        elif qualification['buying_intent'] == 'medium':
            steps.append("Show product demonstrations or specifications")
            steps.append("Address potential concerns")
        else:
            steps.append("Build interest with benefits and value proposition")
            steps.append("Qualify specific needs and use cases")
        
        if qualification['urgency_level'] == 'high':
            steps.append("Check immediate inventory and delivery options")
        
        return steps


class UpsellingSuggestionInput(BaseModel):
    primary_product: str = Field(description="Main product the customer is interested in")
    customer_budget: Optional[float] = Field(default=None, description="Customer's budget in KWD")


class UpsellingSuggestionTool(BaseTool):
    name: str = "upselling_suggestion"
    description: str = "Suggest complementary products, accessories, or upgrade options to increase order value. Use when customer has shown interest in a specific product."
    args_schema: type = UpsellingSuggestionInput

    def _run(self, primary_product: str, customer_budget: Optional[float] = None) -> Dict[str, Any]:
        """Generate upselling and cross-selling suggestions"""
        logger.info(f"UpsellingSuggestionTool: Generating upsells for '{primary_product}'")
        
        try:
            # Get complementary product suggestions
            complementary_products = self._get_complementary_products(primary_product)
            
            # Get upgrade suggestions
            upgrade_suggestions = self._get_upgrade_suggestions(primary_product)
            
            # Create upselling presentation
            upselling_text = self._create_upselling_presentation(
                primary_product, 
                complementary_products, 
                upgrade_suggestions, 
                customer_budget
            )
            
            return {
                "success": True,
                "primary_product": primary_product,
                "complementary_products": complementary_products,
                "upgrade_suggestions": upgrade_suggestions,
                "upselling_text": upselling_text,
                "budget_considered": customer_budget
            }
            
        except Exception as e:
            logger.error(f"Error in upselling suggestions: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Let me also show you some related products that might interest you."
            }
    
    def _get_complementary_products(self, primary_product: str) -> List[str]:
        """Get complementary products based on primary product category"""
        primary_lower = primary_product.lower()
        complementary = []
        
        # Medical equipment complementary products
        if any(word in primary_lower for word in ['wheelchair', 'mobility']):
            complementary.extend(['wheelchair accessories', 'mobility aids', 'cushions'])
        
        # Appliance complementary products
        if any(word in primary_lower for word in ['refrigerator', 'fridge']):
            complementary.extend(['water filter', 'ice maker', 'food storage'])
        elif any(word in primary_lower for word in ['air conditioner', 'ac']):
            complementary.extend(['air purifier', 'humidifier', 'smart thermostat'])
        elif any(word in primary_lower for word in ['washing machine']):
            complementary.extend(['dryer', 'laundry accessories', 'detergent'])
        elif any(word in primary_lower for word in ['vacuum', 'cleaner']):
            complementary.extend(['vacuum bags', 'cleaning accessories', 'air purifier'])
        
        return complementary[:3]  # Limit to 3 suggestions
    
    def _get_upgrade_suggestions(self, primary_product: str) -> List[str]:
        """Get upgrade suggestions for the primary product"""
        upgrades = []
        primary_lower = primary_product.lower()
        
        if 'basic' in primary_lower or 'standard' in primary_lower:
            upgrades.append('Premium model with advanced features')
        if any(word in primary_lower for word in ['manual', 'non-inverter']):
            upgrades.append('Smart/Inverter version for energy efficiency')
        
        # General upgrade suggestions
        upgrades.extend([
            'Extended warranty package',
            'Professional installation service',
            'Maintenance package'
        ])
        
        return upgrades[:3]
    
    def _create_upselling_presentation(self, primary: str, complementary: List[str], 
                                     upgrades: List[str], budget: Optional[float]) -> str:
        """Create compelling upselling presentation"""
        text = f"🎯 **Complete Your {primary} Solution!**\n\n"
        
        if complementary:
            text += "🛍️ **Perfect Additions:**\n"
            for item in complementary:
                text += f"• {item.title()} - Enhances your experience\n"
            text += "\n"
        
        if upgrades:
            text += "⬆️ **Upgrade Options:**\n"
            for upgrade in upgrades:
                text += f"• {upgrade} - Added value and peace of mind\n"
            text += "\n"
        
        text += "💡 **Bundle Benefits:**\n"
        text += "• Save on combined shipping\n"
        text += "• Coordinated installation\n"
        text += "• Single warranty coverage\n"
        text += "• Better overall value\n\n"
        
        if budget:
            text += f"💰 **Budget-Friendly Options Available** - Starting from additional 10-20% of your {budget} KWD budget\n\n"
        
        text += "🤝 **Special Offer:** Bundle discount available for multiple items!"
        
        return text