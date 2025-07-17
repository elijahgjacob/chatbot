"""
Test Data Generator for Al Essa Kuwait Virtual Assistant
Generates comprehensive test scenarios for different chat scenarios and tool calls
"""

from typing import Dict, List, Any, Tuple
import random
from dataclasses import dataclass
from enum import Enum

class QueryType(Enum):
    PRODUCT_SEARCH = "product_search"
    MEDICAL_INQUIRY = "medical_inquiry"
    BRAND_SPECIFIC = "brand_specific"
    PRICE_INQUIRY = "price_inquiry"
    COMPARISON = "comparison"
    GENERAL = "general"
    EMERGENCY = "emergency"
    MIXED = "mixed"

class ExpectedAgent(Enum):
    SALES = "sales"
    DOCTOR = "doctor"
    AMBIGUOUS = "ambiguous"

@dataclass
class TestScenario:
    """Represents a single test scenario"""
    query: str
    expected_agent: ExpectedAgent
    query_type: QueryType
    expected_tools: List[str]
    expected_keywords: List[str]
    difficulty_level: int  # 1-5, where 5 is most difficult
    context: Dict[str, Any] = None
    expected_accuracy: float = 0.95  # Expected accuracy for this scenario

class TestDataGenerator:
    """Generates comprehensive test data for the virtual assistant"""
    
    def __init__(self):
        self.product_categories = [
            "wheelchairs", "blood pressure monitors", "thermometers", 
            "air conditioners", "refrigerators", "washing machines",
            "medical equipment", "mobility aids", "home appliances",
            "walkers", "crutches", "oxygen concentrators"
        ]
        
        self.medical_symptoms = [
            "headache", "back pain", "knee pain", "chest pain",
            "shortness of breath", "dizziness", "fever", "cough",
            "joint pain", "muscle aches", "fatigue", "insomnia"
        ]
        
        self.brands = [
            "Al Essa", "Samsung", "LG", "Sunrise", "Philips",
            "Siemens", "Bosch", "Whirlpool", "Drive Medical"
        ]
        
        self.price_terms = [
            "cheapest", "most affordable", "budget", "price range",
            "under 100 KWD", "expensive", "premium", "cost"
        ]
    
    def generate_product_search_scenarios(self, count: int = 50) -> List[TestScenario]:
        """Generate product search test scenarios"""
        scenarios = []
        
        templates = [
            "Show me {category}",
            "I need {category}",
            "Do you have {category}?",
            "What {category} do you sell?",
            "I'm looking for {category}",
            "Can you help me find {category}?",
            "Where can I buy {category}?",
            "I want to purchase {category}",
            "Display all {category}",
            "List your {category}"
        ]
        
        for i in range(count):
            category = random.choice(self.product_categories)
            template = random.choice(templates)
            query = template.format(category=category)
            
            scenarios.append(TestScenario(
                query=query,
                expected_agent=ExpectedAgent.SALES,
                query_type=QueryType.PRODUCT_SEARCH,
                expected_tools=["product_search"],
                expected_keywords=[category, "product", "search"],
                difficulty_level=random.randint(1, 3)
            ))
        
        return scenarios
    
    def generate_medical_inquiry_scenarios(self, count: int = 30) -> List[TestScenario]:
        """Generate medical inquiry test scenarios"""
        scenarios = []
        
        templates = [
            "I have {symptom}",
            "What should I do for {symptom}?",
            "I'm experiencing {symptom}",
            "How to treat {symptom}?",
            "What causes {symptom}?",
            "I need help with {symptom}",
            "Can you advise on {symptom}?",
            "What products help with {symptom}?",
            "I suffer from {symptom}",
            "Any recommendations for {symptom}?"
        ]
        
        for i in range(count):
            symptom = random.choice(self.medical_symptoms)
            template = random.choice(templates)
            query = template.format(symptom=symptom)
            
            # Determine if this should route to doctor or sales
            expected_agent = ExpectedAgent.DOCTOR
            expected_tools = ["medical_advice"]
            
            # Some queries might need product recommendations
            if "products" in template.lower() or "recommendations" in template.lower():
                expected_tools.append("product_search")
            
            scenarios.append(TestScenario(
                query=query,
                expected_agent=expected_agent,
                query_type=QueryType.MEDICAL_INQUIRY,
                expected_tools=expected_tools,
                expected_keywords=[symptom, "medical", "health"],
                difficulty_level=random.randint(2, 4)
            ))
        
        return scenarios
    
    def generate_brand_specific_scenarios(self, count: int = 20) -> List[TestScenario]:
        """Generate brand-specific query scenarios"""
        scenarios = []
        
        templates = [
            "Show me {brand} products",
            "What {brand} items do you have?",
            "I want {brand} {category}",
            "Do you sell {brand}?",
            "Compare {brand} with other brands",
            "{brand} price list",
            "Best {brand} products",
            "New {brand} arrivals",
            "{brand} warranty information",
            "Where to buy {brand}?"
        ]
        
        for i in range(count):
            brand = random.choice(self.brands)
            category = random.choice(self.product_categories)
            template = random.choice(templates)
            
            if "{category}" in template:
                query = template.format(brand=brand, category=category)
                keywords = [brand, category, "brand"]
            else:
                query = template.format(brand=brand)
                keywords = [brand, "brand"]
            
            scenarios.append(TestScenario(
                query=query,
                expected_agent=ExpectedAgent.SALES,
                query_type=QueryType.BRAND_SPECIFIC,
                expected_tools=["product_search", "brand_filter"],
                expected_keywords=keywords,
                difficulty_level=random.randint(2, 3)
            ))
        
        return scenarios
    
    def generate_price_inquiry_scenarios(self, count: int = 25) -> List[TestScenario]:
        """Generate price-related query scenarios"""
        scenarios = []
        
        templates = [
            "What's the {price_term} {category}?",
            "How much does {category} cost?",
            "Show me {price_term} {category}",
            "Price of {category}",
            "{category} {price_term}",
            "Can you find {price_term} {category}?",
            "I need {price_term} {category}",
            "Budget {category} options",
            "Affordable {category}",
            "Compare prices for {category}"
        ]
        
        for i in range(count):
            price_term = random.choice(self.price_terms)
            category = random.choice(self.product_categories)
            template = random.choice(templates)
            query = template.format(price_term=price_term, category=category)
            
            scenarios.append(TestScenario(
                query=query,
                expected_agent=ExpectedAgent.SALES,
                query_type=QueryType.PRICE_INQUIRY,
                expected_tools=["product_search", "price_filter"],
                expected_keywords=[category, price_term, "price"],
                difficulty_level=random.randint(2, 4)
            ))
        
        return scenarios
    
    def generate_emergency_scenarios(self, count: int = 10) -> List[TestScenario]:
        """Generate emergency medical scenarios"""
        scenarios = []
        
        emergency_queries = [
            "I'm having chest pain",
            "I can't breathe properly",
            "Someone is unconscious",
            "Severe allergic reaction",
            "Heavy bleeding",
            "High fever with confusion",
            "Severe head injury",
            "Heart attack symptoms",
            "Stroke symptoms",
            "Emergency medical help needed"
        ]
        
        for query in emergency_queries[:count]:
            scenarios.append(TestScenario(
                query=query,
                expected_agent=ExpectedAgent.DOCTOR,
                query_type=QueryType.EMERGENCY,
                expected_tools=["emergency_response", "medical_advice"],
                expected_keywords=["emergency", "urgent", "medical"],
                difficulty_level=5,
                expected_accuracy=1.0  # Emergency scenarios must be 100% accurate
            ))
        
        return scenarios
    
    def generate_mixed_scenarios(self, count: int = 15) -> List[TestScenario]:
        """Generate mixed/ambiguous scenarios"""
        scenarios = []
        
        mixed_queries = [
            "I need something for my back pain",  # Could be medical advice or product
            "What's good for headaches?",  # Could be advice or products
            "Help with mobility issues",  # Could route to either agent
            "I need support for walking",  # Could be medical or product
            "Something for blood pressure",  # Could be advice or monitor
            "Pain relief options",  # Could be medical or products
            "Breathing support",  # Could be advice or equipment
            "Joint support products",  # Mixed medical and product
            "Recovery equipment",  # Could be either
            "Health monitoring devices"  # Product but health-related
        ]
        
        for i, query in enumerate(mixed_queries[:count]):
            # These scenarios could legitimately go to either agent
            scenarios.append(TestScenario(
                query=query,
                expected_agent=ExpectedAgent.AMBIGUOUS,
                query_type=QueryType.MIXED,
                expected_tools=["agent_router", "product_search", "medical_advice"],
                expected_keywords=["ambiguous", "mixed"],
                difficulty_level=4,
                expected_accuracy=0.85  # Lower accuracy expectation for ambiguous cases
            ))
        
        return scenarios
    
    def generate_conversation_context_scenarios(self, count: int = 20) -> List[TestScenario]:
        """Generate scenarios with conversation context"""
        scenarios = []
        
        conversation_pairs = [
            ("I need a wheelchair", "What's the price range?"),
            ("I have back pain", "What products can help?"),
            ("Show me Samsung products", "Which one is cheapest?"),
            ("I need medical advice", "Do you have related products?"),
            ("I'm looking for mobility aids", "What brands do you recommend?")
        ]
        
        for i, (first_query, follow_up) in enumerate(conversation_pairs[:count//2]):
            # First query in conversation
            scenarios.append(TestScenario(
                query=first_query,
                expected_agent=ExpectedAgent.SALES if "wheelchair" in first_query else ExpectedAgent.DOCTOR,
                query_type=QueryType.GENERAL,
                expected_tools=["product_search"] if "wheelchair" in first_query else ["medical_advice"],
                expected_keywords=["conversation", "context"],
                difficulty_level=3,
                context={"conversation_turn": 1}
            ))
            
            # Follow-up query
            scenarios.append(TestScenario(
                query=follow_up,
                expected_agent=ExpectedAgent.SALES,  # Follow-ups often become product-focused
                query_type=QueryType.GENERAL,
                expected_tools=["product_search", "context_analysis"],
                expected_keywords=["conversation", "context", "follow_up"],
                difficulty_level=4,
                context={"conversation_turn": 2, "previous_query": first_query}
            ))
        
        return scenarios
    
    def generate_edge_case_scenarios(self, count: int = 15) -> List[TestScenario]:
        """Generate edge case scenarios"""
        scenarios = []
        
        edge_cases = [
            ("", ExpectedAgent.SALES, ["empty_query"]),  # Empty query
            ("asdfghjkl", ExpectedAgent.SALES, ["gibberish"]),  # Gibberish
            ("What's the weather?", ExpectedAgent.SALES, ["out_of_scope"]),  # Out of scope
            ("Tell me a joke", ExpectedAgent.SALES, ["out_of_scope"]),  # Out of scope
            ("How to cook pasta?", ExpectedAgent.SALES, ["out_of_scope"]),  # Out of scope
            ("I want to return a product", ExpectedAgent.SALES, ["customer_service"]),  # Customer service
            ("Your website is broken", ExpectedAgent.SALES, ["technical_issue"]),  # Technical issue
            ("I want to speak to a manager", ExpectedAgent.SALES, ["escalation"]),  # Escalation
            ("What are your business hours?", ExpectedAgent.SALES, ["business_info"]),  # Business info
            ("Where is your store located?", ExpectedAgent.SALES, ["location_info"]),  # Location
        ]
        
        for query, expected_agent, keywords in edge_cases[:count]:
            scenarios.append(TestScenario(
                query=query,
                expected_agent=expected_agent,
                query_type=QueryType.GENERAL,
                expected_tools=["fallback_handler"],
                expected_keywords=keywords,
                difficulty_level=5,
                expected_accuracy=0.80  # Lower accuracy expectation for edge cases
            ))
        
        return scenarios
    
    def generate_comprehensive_test_suite(self) -> List[TestScenario]:
        """Generate a comprehensive test suite with all scenario types"""
        all_scenarios = []
        
        # Add different types of scenarios
        all_scenarios.extend(self.generate_product_search_scenarios(50))
        all_scenarios.extend(self.generate_medical_inquiry_scenarios(30))
        all_scenarios.extend(self.generate_brand_specific_scenarios(20))
        all_scenarios.extend(self.generate_price_inquiry_scenarios(25))
        all_scenarios.extend(self.generate_emergency_scenarios(10))
        all_scenarios.extend(self.generate_mixed_scenarios(15))
        all_scenarios.extend(self.generate_conversation_context_scenarios(20))
        all_scenarios.extend(self.generate_edge_case_scenarios(15))
        
        # Shuffle to ensure varied testing order
        random.shuffle(all_scenarios)
        
        return all_scenarios
    
    def get_scenarios_by_difficulty(self, difficulty: int) -> List[TestScenario]:
        """Get scenarios filtered by difficulty level"""
        all_scenarios = self.generate_comprehensive_test_suite()
        return [s for s in all_scenarios if s.difficulty_level == difficulty]
    
    def get_scenarios_by_type(self, query_type: QueryType) -> List[TestScenario]:
        """Get scenarios filtered by query type"""
        all_scenarios = self.generate_comprehensive_test_suite()
        return [s for s in all_scenarios if s.query_type == query_type]
    
    def get_high_accuracy_scenarios(self) -> List[TestScenario]:
        """Get scenarios that should have high accuracy (95%+)"""
        all_scenarios = self.generate_comprehensive_test_suite()
        return [s for s in all_scenarios if s.expected_accuracy >= 0.95]

# Test data for specific testing purposes
GOLDEN_TEST_CASES = [
    # Perfect routing cases
    TestScenario("Show me wheelchairs", ExpectedAgent.SALES, QueryType.PRODUCT_SEARCH, ["product_search"], ["wheelchair"], 1),
    TestScenario("I have a headache", ExpectedAgent.DOCTOR, QueryType.MEDICAL_INQUIRY, ["medical_advice"], ["headache"], 1),
    TestScenario("What Al Essa products do you have?", ExpectedAgent.SALES, QueryType.BRAND_SPECIFIC, ["product_search"], ["Al Essa"], 2),
    TestScenario("What should I do for chest pain?", ExpectedAgent.DOCTOR, QueryType.EMERGENCY, ["emergency_response"], ["chest pain"], 5),
    
    # Quality benchmarks
    TestScenario("I need the cheapest air conditioner", ExpectedAgent.SALES, QueryType.PRICE_INQUIRY, ["product_search", "price_filter"], ["cheapest", "air conditioner"], 3),
    TestScenario("Compare Samsung and LG refrigerators", ExpectedAgent.SALES, QueryType.COMPARISON, ["product_search", "comparison"], ["Samsung", "LG", "refrigerators"], 4),
]

def get_golden_test_cases() -> List[TestScenario]:
    """Get the golden test cases for benchmarking"""
    return GOLDEN_TEST_CASES