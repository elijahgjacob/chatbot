"""
Tests for the scraping functionality.
"""

import pytest
from app.core.scraping import get_product_prices_from_search, ProductScraper

def test_scraper_initialization():
    """Test that the scraper initializes correctly."""
    scraper = ProductScraper()
    assert scraper.base_url == "https://www.alessaonline.com"
    assert scraper.timeout == 10

def test_search_url_building():
    """Test that search URLs are built correctly."""
    scraper = ProductScraper()
    url = scraper.build_search_url("wheelchair")
    expected = "https://www.alessaonline.com/default/catalogsearch/result/?q=wheelchair"
    assert url == expected
    
    url_with_spaces = scraper.build_search_url("sunrise wheelchair")
    expected_with_spaces = "https://www.alessaonline.com/default/catalogsearch/result/?q=sunrise+wheelchair"
    assert url_with_spaces == expected_with_spaces

def test_price_parsing():
    """Test that price parsing works correctly."""
    scraper = ProductScraper()
    
    # Test various price formats
    assert scraper.parse_price("150.0 KWD") == 150.0
    assert scraper.parse_price("75 KWD") == 75.0
    assert scraper.parse_price("$200") == 200.0
    assert scraper.parse_price("1,500") == 1500.0
    assert scraper.parse_price("") is None
    assert scraper.parse_price("N/A") is None

def test_real_wheelchair_search():
    """Test that wheelchair search returns real products."""
    result = get_product_prices_from_search("wheelchair")
    
    assert "products" in result
    assert len(result["products"]) > 0
    
    # Check that products have real data
    for product in result["products"][:3]:  # Check first 3 products
        assert "name" in product
        assert "price" in product
        assert "url" in product
        assert product["name"] != ""
        assert product["price"] > 0
        assert "alessaonline.com" in product["url"]
        
        # Ensure no fake product names
        fake_names = ["Basic Manual Wheelchair", "Deluxe Manual Wheelchair", "Portable Travel Wheelchair"]
        assert product["name"] not in fake_names

def test_sunrise_brand_search():
    """Test that Sunrise brand search returns real products."""
    result = get_product_prices_from_search("sunrise wheelchair")
    
    assert "products" in result
    assert len(result["products"]) > 0
    
    # Check that we get Sunrise products
    sunrise_products = [p for p in result["products"] if "sunrise" in p["name"].lower()]
    assert len(sunrise_products) > 0
    
    # Check that products have real data
    for product in sunrise_products[:3]:
        assert "name" in product
        assert "price" in product
        assert "url" in product
        assert "sunrise" in product["name"].lower()
        assert product["price"] > 0

def test_cheapest_search():
    """Test that cheapest search works correctly."""
    result = get_product_prices_from_search("wheelchair")
    
    assert "products" in result
    assert len(result["products"]) > 0
    
    # Find the cheapest product
    products = result["products"]
    cheapest = min(products, key=lambda x: x["price"])
    
    # Verify it's actually the cheapest
    for product in products:
        assert product["price"] >= cheapest["price"]

def test_no_fake_data():
    """Test that no fake/mock data is returned."""
    result = get_product_prices_from_search("wheelchair")
    
    products = result["products"]
    
    # Check for fake product names
    fake_names = [
        "Basic Manual Wheelchair",
        "Deluxe Manual Wheelchair", 
        "Portable Travel Wheelchair",
        "Lightweight Electric Wheelchair",
        "Affordable Power Wheelchair"
    ]
    
    for product in products:
        assert product["name"] not in fake_names
    
    # Check for fake prices (should be in KWD, not USD)
    for product in products:
        assert product["currency"] == "KWD"
        # Prices should be reasonable for Kuwait market
        assert 1 <= product["price"] <= 10000

def test_product_search_tool():
    """Test the product search tool integration."""
    from app.tools.product_search import product_search_tool
    
    result = product_search_tool.invoke({"query": "wheelchair"})
    
    assert result["success"] is True
    assert "products" in result
    assert len(result["products"]) > 0
    
    # Check that it returns real data
    for product in result["products"][:3]:
        assert "name" in product
        assert "price" in product
        assert "url" in product
        assert product["name"] != ""
        assert product["price"] > 0