# Duplicate Code Analysis and Fixes

## Summary
The codebase contains several instances of duplicate code that should be refactored to improve maintainability, reduce bugs, and follow DRY (Don't Repeat Yourself) principles.

## Identified Duplicates

### 1. Product Search Tools (CRITICAL)
**Files affected:**
- `app/tools/product_search.py` - Standard product search tool
- `app/tools/enhanced_search.py` - Enhanced product search tool  
- `app/tools/tools.py` - Another product search implementation

**Issues:**
- Three different implementations of product search functionality
- `tools.py` contains a `ProductSearchTool` class that duplicates `product_search_tool` from `product_search.py`
- `enhanced_search.py` has `enhanced_product_search_tool` that overlaps with basic product search
- All three use `get_product_prices_from_search` from `app.core.scraping`

**Impact:** Maintenance overhead, inconsistent behavior, confusion about which tool to use

### 2. Agent Helper Methods (HIGH)
**Files affected:**
- `app/agents/doctor_agent.py`
- `app/agents/sales_agent.py`

**Duplicate methods:**
- `_build_context_prompt()` - Nearly identical implementations
- `_update_user_context()` - Similar pattern but different context extraction logic

**Issues:**
- Both agents have almost identical `_build_context_prompt` methods
- Both follow the same pattern for context updates but with different domain-specific logic

### 3. Product Deduplication Logic
**Files affected:**
- `app/agents/doctor_agent.py` (lines 125-135)

**Issues:**
- Product deduplication logic using `seen_names` set could be extracted to a utility function
- This pattern might be needed in other agents too

### 4. Response Building Patterns
**Files affected:**
- `app/agents/doctor_agent.py`
- `app/agents/sales_agent.py`

**Issues:**
- Both agents follow similar patterns for building responses
- Similar error handling and success response structures
- Conversation memory management is duplicated

## Recommended Fixes

### 1. Consolidate Product Search Tools
**Action:** Remove duplicate tools and create a unified search interface

**Changes:**
- Remove `ProductSearchTool` class from `app/tools/tools.py`
- Keep `product_search_tool` as the primary search tool
- Keep `enhanced_product_search_tool` for advanced scenarios
- Update imports to use consistent tools

### 2. Create Base Agent Class
**Action:** Extract common functionality into a base agent class

**New file:** `app/agents/base_agent.py`
- Abstract base class with common methods
- `_build_context_prompt()` - unified implementation
- `_handle_conversation_memory()` - unified memory management
- `_build_response()` - unified response structure
- `_deduplicate_products()` - utility method

### 3. Create Agent Utilities Module
**Action:** Extract shared utility functions

**New file:** `app/agents/utils.py`
- Product deduplication utilities
- Context extraction utilities
- Response formatting utilities

### 4. Update Agent Implementations
**Action:** Refactor existing agents to inherit from base class

**Changes:**
- Make `DoctorAgent` and `SalesAgent` inherit from `BaseAgent`
- Override only domain-specific methods
- Remove duplicate code

## Implementation Status

### ✅ COMPLETED FIXES

1. **✅ High Priority:** Removed `tools.py` duplicates 
   - Removed duplicate `ProductSearchTool` class from `app/tools/tools.py`
   - Updated test imports to use `product_search_tool` from `app.tools.product_search`

2. **✅ Medium Priority:** Created base agent class
   - Created `app/agents/base_agent.py` with common functionality
   - Refactored `DoctorAgent` and `SalesAgent` to inherit from `BaseAgent`
   - Removed duplicate methods: `_build_context_prompt`, conversation memory handling, response building
   - Added shared utilities: `_deduplicate_products`, `_get_conversation_context`, `_handle_conversation_memory`, `_build_response`

3. **✅ Code Organization:** Implemented inheritance pattern
   - Both agents now use consistent response structures
   - Centralized conversation memory management
   - Unified context building logic

### 🔧 FIXES IMPLEMENTED

#### 1. Removed Product Search Tool Duplicates
- **File:** `app/tools/tools.py`
- **Action:** Removed `ProductSearchTool` class completely
- **Impact:** Eliminates confusion about which search tool to use

#### 2. Created Base Agent Class  
- **File:** `app/agents/base_agent.py` (NEW)
- **Provides:** Abstract base class with common agent functionality
- **Methods:** 
  - `_build_context_prompt()` - Unified context building
  - `_handle_conversation_memory()` - Memory management
  - `_build_response()` - Standardized responses
  - `_deduplicate_products()` - Product deduplication utility
  - `_get_conversation_context()` - Context retrieval

#### 3. Refactored Doctor Agent
- **File:** `app/agents/doctor_agent.py` 
- **Changes:**
  - Now inherits from `BaseAgent`
  - Added `handle_chat()` method for consistency
  - Removed duplicate `_build_context_prompt()` method
  - Updated conversation memory handling
  - Uses base class utilities for deduplication and response building

#### 4. Refactored Sales Agent
- **File:** `app/agents/sales_agent.py`
- **Changes:**
  - Now inherits from `BaseAgent` 
  - Added `handle_chat()` method for consistency
  - Removed duplicate `_build_context_prompt()` method
  - Updated conversation memory handling
  - Uses shared response building pattern

#### 5. Updated Tests
- **File:** `tests/test_agent.py`
- **Changes:** Updated imports to use correct product search tool

## Benefits of Fixes

- **Reduced maintenance:** Single source of truth for common functionality
- **Consistency:** All agents behave consistently
- **Easier testing:** Fewer places to mock and test
- **Better extensibility:** New agents can inherit common functionality
- **Reduced bugs:** Less duplicate code means fewer places for bugs to hide