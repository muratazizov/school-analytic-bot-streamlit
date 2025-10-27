# Dynamic Interface Implementation

## Overview
The app interface (title, description, and welcome message) is now fully dynamic and adapts automatically based on the actual database schema.

## Changes Made

### 1. Table Name Tracking
Modified `get_database_schema()` to collect and store table names:
- Added `table_names = []` list to track all tables during schema retrieval
- Store table names in `st.session_state.table_names` for access by other functions
- Fallback to empty list if schema retrieval fails

### 2. New Helper Functions

#### `get_dynamic_app_title()`
- Generates title based on actual database name from config
- Format: `🏫 {DB_NAME} Chatbot (Azure OpenAI)`
- Example: `🏫 SchoolDB Chatbot (Azure OpenAI)`

#### `get_dynamic_app_description()`
- Generates description based on actual table names from database
- Converts table names to friendly format (e.g., `LibraryCheckouts` → `library checkouts`)
- Intelligently formats list:
  - 1 table: "Ask me questions about {table}."
  - 2 tables: "Ask me questions about {table1} and {table2}."
  - 3+ tables: "Ask me questions about {table1}, {table2}, or {table3}."
- Example for SchoolDB: "Ask me questions about students, teachers, classes, classenrollments, scores, attendance, books, or librarycheckouts."

#### `get_dynamic_welcome_message()`
- Generates initial assistant message based on actual table names
- Same friendly formatting as description
- Uses "and" for last item (instead of "or")
- Fallback message if no database connection: "Hello! I'm your database assistant. Please configure your database connection in the sidebar."

### 3. Updated main() Function
- Replaced hardcoded `st.title("🏫 School Database Chatbot (Azure OpenAI)")` with `dynamic_title = get_dynamic_app_title(); st.title(dynamic_title)`
- Replaced hardcoded description with `dynamic_description = get_dynamic_app_description(); st.write(dynamic_description)`
- Replaced hardcoded welcome message with `dynamic_welcome = get_dynamic_welcome_message()`

## Benefits

1. **Automatic Adaptation**: If you change databases (e.g., from SchoolDB to InventoryDB), the interface automatically updates
2. **Schema-Aware**: The app shows only what's actually in your database
3. **No Manual Updates**: No need to edit hardcoded strings when database changes
4. **User-Friendly**: Table names are converted to lowercase with spaces for better readability
5. **Professional**: Interface always matches the actual database structure

## Example Outputs

### With SchoolDB (9 tables)
- **Title**: 🏫 SchoolDB Chatbot (Azure OpenAI)
- **Description**: Ask me questions about students, teachers, subjects, classes, classenrollments, scores, attendance, books, or librarycheckouts.
- **Welcome**: Hello! I'm your database assistant. Ask me about students, teachers, subjects, classes, classenrollments, scores, attendance, books, and librarycheckouts.

### With Different Database (e.g., InventoryDB with 3 tables: Products, Orders, Customers)
- **Title**: 🏫 InventoryDB Chatbot (Azure OpenAI)
- **Description**: Ask me questions about products, orders, or customers.
- **Welcome**: Hello! I'm your database assistant. Ask me about products, orders, and customers.

### With No Connection
- **Title**: 🏫 Database Chatbot (Azure OpenAI)
- **Description**: Configure your database connection to start querying.
- **Welcome**: Hello! I'm your database assistant. Please configure your database connection in the sidebar.

## How It Works

1. When the app loads, `get_database_schema()` retrieves the schema and populates `st.session_state.table_names`
2. The main function calls the helper functions to generate dynamic text
3. The generated text is displayed in the UI
4. When configuration changes or schema is refreshed, the cache clears and text regenerates on next load
