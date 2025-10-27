import pyodbc
import json
import re
from decimal import Decimal
import datetime
import streamlit as st
import pandas as pd
from openai import AzureOpenAI
import config
import time

# Constants
MAX_DISPLAY_ROWS = 1000
MAX_SUMMARY_ROWS = 100
MAX_CHAT_MESSAGES = 50
MAX_RETRIES = 3
RETRY_DELAY = 1

# Validate configuration on startup
def validate_and_show_config_errors():
    """Check configuration and show errors in UI"""
    errors = config.validate_config()
    if errors:
        st.error("⚠️ Configuration Error - Please fix the following issues:")
        for error in errors:
            st.error(f"• {error}")
        st.info("💡 Set these values in your .env file or use the sidebar configuration.")
        return False
    return True

# Initialize Azure OpenAI client in session state
def get_openai_client():
    """Get or create OpenAI client from session state"""
    if 'openai_client' not in st.session_state:
        try:
            st.session_state.openai_client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {e}")
            return None
    return st.session_state.openai_client


@st.cache_data(ttl=3600)
def get_database_schema(_connection_string, db_server, db_name):
    """
    Dynamically retrieve the database schema from SQL Server.
    Cached per database to support multi-database scenarios.
    
    Args:
        _connection_string: Connection string (prefixed with _ to exclude from cache key)
        db_server: Database server name (used in cache key)
        db_name: Database name (used in cache key)
    
    Returns:
        str: Formatted database schema information
    """
    try:
        conn = pyodbc.connect(_connection_string, timeout=10)
        cursor = conn.cursor()
        
        # Query to get all tables and their columns with data types from ALL schemas
        schema_query = """
        SELECT 
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            c.IS_NULLABLE,
            CASE 
                WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PRIMARY KEY'
                WHEN fk.COLUMN_NAME IS NOT NULL THEN 'FOREIGN KEY'
                ELSE ''
            END AS KEY_TYPE,
            fk.REFERENCED_TABLE_SCHEMA,
            fk.REFERENCED_TABLE_NAME,
            fk.REFERENCED_COLUMN_NAME,
            c.COLUMN_DEFAULT
        FROM 
            INFORMATION_SCHEMA.TABLES t
        INNER JOIN 
            INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME
        LEFT JOIN (
            SELECT 
                ku.TABLE_SCHEMA,
                ku.TABLE_NAME,
                ku.COLUMN_NAME
            FROM 
                INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            INNER JOIN 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku 
                ON tc.CONSTRAINT_SCHEMA = ku.CONSTRAINT_SCHEMA 
                AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            WHERE 
                tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA AND c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
        LEFT JOIN (
            SELECT 
                ku.TABLE_SCHEMA,
                ku.TABLE_NAME,
                ku.COLUMN_NAME,
                ccu.TABLE_SCHEMA AS REFERENCED_TABLE_SCHEMA,
                ccu.TABLE_NAME AS REFERENCED_TABLE_NAME,
                ccu.COLUMN_NAME AS REFERENCED_COLUMN_NAME
            FROM 
                INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            INNER JOIN 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku 
                ON tc.CONSTRAINT_SCHEMA = ku.CONSTRAINT_SCHEMA 
                AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            INNER JOIN 
                INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu 
                ON tc.CONSTRAINT_SCHEMA = ccu.CONSTRAINT_SCHEMA 
                AND tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
            WHERE 
                tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
        ) fk ON c.TABLE_SCHEMA = fk.TABLE_SCHEMA AND c.TABLE_NAME = fk.TABLE_NAME AND c.COLUMN_NAME = fk.COLUMN_NAME
        WHERE 
            t.TABLE_TYPE = 'BASE TABLE'
            AND t.TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
        ORDER BY 
            t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        cursor.execute(schema_query)
        rows = cursor.fetchall()
        
        # Build schema string and collect table names
        schema_text = "DATABASE SCHEMA:\n\n"
        current_table = None
        current_schema = None
        table_names = []
        
        for row in rows:
            table_schema = row[0]
            table_name = row[1]
            column_name = row[2]
            data_type = row[3].upper()
            max_length = row[4]
            numeric_precision = row[5]
            numeric_scale = row[6]
            is_nullable = row[7]
            key_type = row[8]
            ref_schema = row[9]
            ref_table = row[10]
            ref_column = row[11]
            
            # Create full table identifier with schema
            full_table_name = f"{table_schema}.{table_name}"
            
            # Start new table section
            if current_schema != table_schema or current_table != table_name:
                if current_table is not None:
                    schema_text += "\n"
                schema_text += f"Table: {full_table_name}\n"
                current_schema = table_schema
                current_table = table_name
                if full_table_name not in table_names:
                    table_names.append(full_table_name)
            
            # Format data type with length/precision
            if max_length and data_type in ['NVARCHAR', 'VARCHAR', 'CHAR', 'NCHAR']:
                type_info = f"{data_type}({max_length})"
            elif numeric_precision and data_type in ['DECIMAL', 'NUMERIC']:
                type_info = f"{data_type}({numeric_precision},{numeric_scale})"
            else:
                type_info = data_type
            
            # Build column description
            column_desc = f"- {column_name} ({type_info}"
            
            if key_type == 'PRIMARY KEY':
                column_desc += ", PRIMARY KEY"
            elif key_type == 'FOREIGN KEY':
                if ref_schema:
                    column_desc += f", FOREIGN KEY -> {ref_schema}.{ref_table}.{ref_column}"
                else:
                    column_desc += f", FOREIGN KEY -> {ref_table}.{ref_column}"
            
            column_desc += ")"
            
            schema_text += column_desc + "\n"
        
        cursor.close()
        conn.close()
        
        # Store table names in session state for dynamic UI
        st.session_state.table_names = table_names
        
        return schema_text
    
    except pyodbc.Error as e:
        # Specific database errors
        error_msg = str(e)
        st.session_state.table_names = []
        
        if "Login failed" in error_msg or "authentication" in error_msg.lower():
            return "DATABASE SCHEMA:\n\n❌ Authentication failed. Please check your username and password in the sidebar."
        elif "Cannot open database" in error_msg:
            return f"DATABASE SCHEMA:\n\n❌ Database '{db_name}' not found. Please check the database name."
        elif "timeout" in error_msg.lower():
            return f"DATABASE SCHEMA:\n\n❌ Connection timeout. Please check if SQL Server is running on '{db_server}'."
        else:
            return f"DATABASE SCHEMA:\n\n❌ Database connection failed: {error_msg}"
    
    except Exception as e:
        # Other errors
        st.session_state.table_names = []
        return f"DATABASE SCHEMA:\n\n❌ Schema retrieval failed: {str(e)}"


def get_dynamic_app_title():
    """
    Generate a dynamic app title based on database name.
    
    Returns:
        str: Dynamic app title
    """
    db_name = config.DB_NAME or "Database"
    return f"{db_name} Database Chatbot"


def get_dynamic_app_description():
    """
    Generate a dynamic app description based on available database tables.
    
    Returns:
        str: Dynamic app description
    """
    table_names = st.session_state.get('table_names', [])
    
    if not table_names:
        return "Configure your database connection to start querying."
    
    # Convert table names to friendly descriptions (remove schema prefix, replace underscores)
    table_descriptions = []
    for name in table_names:
        # Remove schema prefix (e.g., "dbo.Students" -> "Students")
        simple_name = name.split('.')[-1] if '.' in name else name
        # Convert to lowercase and replace underscores
        friendly_name = simple_name.replace('_', ' ').lower()
        table_descriptions.append(friendly_name)
    
    # Build the description
    if len(table_descriptions) == 0:
        return "Ask me questions about your data."
    elif len(table_descriptions) == 1:
        return f"Ask me questions about {table_descriptions[0]}."
    elif len(table_descriptions) == 2:
        return f"Ask me questions about {table_descriptions[0]} and {table_descriptions[1]}."
    else:
        # Join all but last with commas, and last with 'or'
        all_but_last = ", ".join(table_descriptions[:-1])
        return f"Ask me questions about {all_but_last}, or {table_descriptions[-1]}."


def get_dynamic_welcome_message():
    """
    Generate a dynamic welcome message based on available database tables.
    
    Returns:
        str: Dynamic welcome message
    """
    table_names = st.session_state.get('table_names', [])
    
    if not table_names:
        return "Hello! I'm your database assistant. Please configure your database connection in the sidebar."
    
    # Convert table names to friendly descriptions (remove schema prefix, replace underscores)
    table_descriptions = []
    for name in table_names:
        # Remove schema prefix (e.g., "dbo.Students" -> "Students")
        simple_name = name.split('.')[-1] if '.' in name else name
        # Convert to lowercase and replace underscores
        friendly_name = simple_name.replace('_', ' ').lower()
        table_descriptions.append(friendly_name)
    
    # Build the message
    if len(table_descriptions) == 0:
        return "Hello! I'm your database assistant."
    elif len(table_descriptions) == 1:
        return f"Hello! I'm your database assistant. Ask me about {table_descriptions[0]}."
    elif len(table_descriptions) == 2:
        return f"Hello! I'm your database assistant. Ask me about {table_descriptions[0]} and {table_descriptions[1]}."
    else:
        # Join all but last with commas, and last with 'and'
        all_but_last = ", ".join(table_descriptions[:-1])
        return f"Hello! I'm your database assistant. Ask me about {all_but_last}, and {table_descriptions[-1]}."


def get_system_prompt():
    """
    Generate SYSTEM_PROMPT dynamically with current database schema.
    This ensures the AI always has up-to-date schema information.
    
    Returns:
        str: System prompt with current database schema
    """
    # Get fresh schema based on current config
    current_schema = get_database_schema(
        config.CONNECTION_STRING,
        config.DB_SERVER,
        config.DB_NAME
    )
    
    return f"""You are a helpful assistant for a database system. 
Your job is to convert user questions into SQL queries for Microsoft SQL Server.

{current_schema}

IMPORTANT RULES:
1. If the user asks a question that requires database information, generate a SQL SELECT query
2. If the user asks general questions like "What can you do?", "Help", "Hello", respond with "NO_QUERY_NEEDED:" followed by your response
3. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
4. Use proper JOIN syntax when querying multiple tables
5. Use WHERE clauses for filtering
6. When joining names from multiple columns, use + for concatenation (e.g., FirstName + ' ' + LastName)
7. Use appropriate filters based on the database context (e.g., IsActive, Status, etc.)
8. ALWAYS use schema-qualified table names (schema.table) when tables have schema prefixes
9. PAY ATTENTION to conversation history - if the user refers to "them", "those", "it", etc., check previous context
10. If a user asks a follow-up question, consider what was discussed before

SQL SERVER SPECIFIC SYNTAX (VERY IMPORTANT):
- Use TOP N instead of LIMIT N (e.g., SELECT TOP 1 * FROM TableName)
- Use + for string concatenation
- Use GETDATE() for current date
- Use DATEPART() for date parts
- Use LEN() instead of LENGTH()
- Use ISNULL() instead of IFNULL()
- When using GROUP BY with aggregates, include all non-aggregated columns

EXAMPLES:
User: "Show me all customers"
Response: SELECT * FROM dbo.Customers

User: "What are their names?"  (follow-up to previous query about customers)
Response: SELECT CustomerID, FirstName + ' ' + LastName AS FullName FROM dbo.Customers

User: "How many orders do we have?"
Response: SELECT COUNT(*) AS TotalOrders FROM dbo.Orders

User: "Hello"
Response: NO_QUERY_NEEDED: Hello! I can help you query your database. Ask me questions about your data!

RESPONSE FORMAT:
- If a database query is needed: Return ONLY the SQL query (no explanations, no markdown)
- If no query is needed: Start with "NO_QUERY_NEEDED:" followed by your conversational response

Now process the user's input based on the conversation context.
"""


def validate_query_safety(query):
    """
    Validate that the query is safe to execute (SELECT only, no dangerous operations).
    
    Args:
        query (str): SQL query to validate
        
    Returns:
        tuple: (is_safe, error_message)
    """
    query_upper = query.strip().upper()
    
    # Check it starts with SELECT or WITH (CTE)
    if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
        return False, "Only SELECT queries are allowed"
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 
        'TRUNCATE', 'EXEC', 'EXECUTE', 'SP_', 'XP_', 'MERGE'
    ]
    
    for keyword in dangerous_keywords:
        # Use word boundaries to avoid false positives (e.g., "DROPPED" column name)
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, query_upper):
            return False, f"Dangerous keyword detected: {keyword}"
    
    # Check for semicolons (multiple statements)
    if ';' in query.rstrip(';'):  # Allow trailing semicolon
        return False, "Multiple statements not allowed"
    
    return True, None


def query_db(query):
    """
    Execute SQL query and return results.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        list: Query results as list of dictionaries or error dict
    """
    # Validate query safety first
    is_safe, error_msg = validate_query_safety(query)
    if not is_safe:
        return {"error": f"🛡️ Security: {error_msg}"}
    
    try:
        # Connect to database
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        
        # Fetch all results
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                column_name = columns[idx]
                
                # Handle different data types
                if value is None:
                    row_dict[column_name] = None
                elif isinstance(value, Decimal):
                    # Preserve precision - don't round
                    row_dict[column_name] = float(value)
                elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                    # Handle datetime objects
                    row_dict[column_name] = value.isoformat()
                elif isinstance(value, (bytes, bytearray)):
                    # Handle binary data
                    try:
                        row_dict[column_name] = value.decode('utf-8', errors='ignore')
                    except:
                        row_dict[column_name] = '<binary data>'
                elif isinstance(value, bool):
                    # Handle boolean
                    row_dict[column_name] = value
                elif isinstance(value, (int, float, str)):
                    # Handle basic types
                    row_dict[column_name] = value
                else:
                    # Fallback: convert to string for unknown types (UUID, XML, etc.)
                    try:
                        row_dict[column_name] = str(value)
                    except:
                        row_dict[column_name] = '<unprintable>'
                    
            results.append(row_dict)
        
        # Close connection
        cursor.close()
        conn.close()
        
        return results
    
    except pyodbc.Error as e:
        error_msg = str(e)
        if "Invalid object name" in error_msg:
            return {"error": f"Table or view not found. Please check the table name and schema."}
        elif "Invalid column name" in error_msg:
            return {"error": f"Column not found in the table."}
        elif "Syntax error" in error_msg or "Incorrect syntax" in error_msg:
            return {"error": f"SQL syntax error: {error_msg}"}
        else:
            return {"error": f"Database error: {error_msg}"}
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def is_sql_query(text):
    """
    Check if the text is a SQL query.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if it's a SQL query, False otherwise
    """
    text_upper = text.strip().upper()
    sql_keywords = ['SELECT', 'WITH']
    return any(text_upper.startswith(keyword) for keyword in sql_keywords)


def fix_sql_syntax(query):
    """
    Fix common SQL syntax issues for SQL Server.
    
    Args:
        query (str): SQL query to fix
        
    Returns:
        str: Fixed SQL query
    """
    # Replace LIMIT with TOP
    # Pattern: LIMIT n at the end of query
    limit_pattern = r'\s+LIMIT\s+(\d+)\s*;?\s*$'
    match = re.search(limit_pattern, query, re.IGNORECASE)
    if match:
        limit_value = match.group(1)
        # Remove LIMIT clause
        query = re.sub(limit_pattern, '', query, flags=re.IGNORECASE)
        # Add TOP after SELECT
        query = re.sub(r'\bSELECT\b', f'SELECT TOP {limit_value}', query, count=1, flags=re.IGNORECASE)
    
    # Replace LENGTH() with LEN()
    query = re.sub(r'\bLENGTH\s*\(', 'LEN(', query, flags=re.IGNORECASE)
    
    # Replace IFNULL() with ISNULL()
    query = re.sub(r'\bIFNULL\s*\(', 'ISNULL(', query, flags=re.IGNORECASE)
    
    return query.strip()


def extract_sql_from_response(ai_response):
    """
    Robustly extract SQL query from AI response, handling various markdown formats.
    
    Args:
        ai_response (str): AI response text
        
    Returns:
        str: Extracted SQL query
    """
    # Try to find code block with sql marker
    code_block_pattern = r'```(?:sql|SQL)?\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, ai_response, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: return as-is
    return ai_response.strip()


def get_sql_query_from_ai(user_prompt, conversation_history=None):
    """
    Send user prompt to Azure OpenAI and get SQL query or conversational response.
    Includes retry logic for transient failures and conversation history for context.
    
    Args:
        user_prompt (str): User's question
        conversation_history (list): Previous messages for context (optional)
        
    Returns:
        tuple: (query_or_response, needs_database)
            - query_or_response: SQL query or conversational response
            - needs_database: True if database query needed, False otherwise
    """
    client = get_openai_client()
    if not client:
        return "Error: OpenAI client not initialized. Check your API configuration.", False
    
    # Get fresh system prompt with current schema
    system_prompt = get_system_prompt()
    
    # Build message history for context-aware responses
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (limit to last 10 messages to avoid token overflow)
    if conversation_history:
        # Filter out the welcome message and limit history
        filtered_history = [msg for msg in conversation_history if msg.get("role") != "system"]
        # Take last 10 messages (5 exchanges)
        recent_history = filtered_history[-10:] if len(filtered_history) > 10 else filtered_history
        
        for msg in recent_history:
            role = msg.get("role")
            content = msg.get("content", "")
            
            # Clean up assistant messages - remove SQL code blocks to save tokens
            # Keep only the natural language summary
            if role == "assistant" and "**SQL Query:**" in content:
                # Extract only the summary part (before the SQL block)
                summary_part = content.split("**SQL Query:**")[0].strip()
                if summary_part:
                    messages.append({"role": "assistant", "content": summary_part})
            elif content and role in ["user", "assistant"]:
                messages.append({"role": role, "content": content})
    
    # Add current user prompt
    messages.append({"role": "user", "content": user_prompt})
    
    # Retry logic for transient failures
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                temperature=0.3  # Slightly higher for better understanding
            )
            
            ai_response = response.choices[0].message.content
            if not ai_response:
                return "Error: Empty response from AI", False
                
            ai_response = ai_response.strip()
            
            # Check if AI indicates no query is needed
            if ai_response.startswith("NO_QUERY_NEEDED:"):
                conversational_response = ai_response.replace("NO_QUERY_NEEDED:", "").strip()
                return conversational_response, False
            
            # Extract SQL from markdown code blocks
            query = extract_sql_from_response(ai_response)
            
            # Verify it's actually a SQL query
            if not is_sql_query(query):
                # If it's not a SQL query, treat it as a conversational response
                return query, False
            
            return query, True
            
        except Exception as e:
            error_str = str(e)
            
            # Check for rate limiting
            if "429" in error_str or "rate" in error_str.lower():
                if attempt < MAX_RETRIES - 1:
                    st.warning(f"⏳ Rate limit reached, retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    return "Error: Rate limit exceeded. Please try again in a moment.", False
            
            # Check for authentication errors
            elif "401" in error_str or "authentication" in error_str.lower():
                return "Error: Authentication failed. Please check your API key in the sidebar.", False
            
            # Check for model not found
            elif "404" in error_str or "not found" in error_str.lower():
                return f"Error: Model '{config.AZURE_OPENAI_DEPLOYMENT}' not found. Check deployment name.", False
            
            # Other errors
            else:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return f"Error: {error_str}", False
    
    return "Error: Maximum retries exceeded", False


def format_results(results):
    """
    Format query results for display.
    
    Args:
        results (list): Query results
        
    Returns:
        str: Formatted results
    """
    if isinstance(results, dict) and "error" in results:
        return f"❌ Error: {results['error']}"
    
    if not results:
        return "No results found."
    
    if len(results) == 1 and len(results[0]) == 1:
        # Single value result
        key = list(results[0].keys())[0]
        value = results[0][key]
        return f"Result: {value}"
    
    # Multiple rows/columns
    output = []
    for idx, row in enumerate(results, 1):
        output.append(f"\nRow {idx}:")
        for key, value in row.items():
            output.append(f"  {key}: {value}")
    
    return "\n".join(output)


def get_ai_summary(user_prompt, query, results):
    """
    Get Azure OpenAI to summarize the results in natural language.
    Limits result size to avoid token overflow.
    
    Args:
        user_prompt (str): Original user question
        query (str): SQL query that was executed
        results (list): Query results
        
    Returns:
        str: Natural language summary
    """
    client = get_openai_client()
    if not client:
        return "Summary unavailable: OpenAI client not initialized."
    
    try:
        # Limit results sent to AI to avoid token limits
        summary_results = results[:MAX_SUMMARY_ROWS] if len(results) > MAX_SUMMARY_ROWS else results
        result_count_note = f" (showing first {MAX_SUMMARY_ROWS} of {len(results)})" if len(results) > MAX_SUMMARY_ROWS else ""
        
        summary_prompt = f"""
User asked: "{user_prompt}"

SQL Query executed: {query}

Results{result_count_note}: {json.dumps(summary_results, indent=2, default=str)}

Provide a clear, natural language answer to the user's question based on these results.

IMPORTANT FORMATTING RULES:
- Use proper spacing between words
- Format numbers with appropriate spacing (e.g., "received a 4,067.80" not "receiveda4067.7988")
- Use complete sentences with proper punctuation
- Add line breaks between different points if listing multiple items
- Be concise and friendly
- If there are multiple results, summarize them clearly with bullet points or numbered lists
- If there are more results than shown, mention the total count
"""
        
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains database query results in natural language. Always use proper spacing between words, format numbers clearly, and write in complete, well-structured sentences."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        return summary.strip() if summary else "Summary generation returned empty response."
    
    except Exception as e:
        error_str = str(e)
        if "token" in error_str.lower() or "length" in error_str.lower():
            return f"⚠️ Results too large to summarize ({len(results)} rows). Showing data table below."
        return f"Error generating summary: {error_str}"


def main():
    """Streamlit chat-style UI using `st.chat_input` and `st.chat_message`."""
    st.set_page_config(page_title="Database Chatbot", layout="wide")

    # Validate configuration first
    if not validate_and_show_config_errors():
        st.stop()
    
    # Initialize session state table_names if not exists
    if 'table_names' not in st.session_state:
        st.session_state.table_names = []
    
    # Get dynamic title based on database name
    dynamic_title = get_dynamic_app_title()
    st.title(dynamic_title)

    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize session state for configuration if not exists
        if 'config_updated' not in st.session_state:
            st.session_state.config_updated = False
        
        with st.expander("🔧 Azure OpenAI Settings", expanded=False):
            # Azure Endpoint dropdown with custom option
            endpoint_options = [
                "https://ai-proxy.lab.epam.com",
                "https://api.openai.com/v1",
                "Custom..."
            ]
            
            default_endpoint = config.AZURE_OPENAI_ENDPOINT if config.AZURE_OPENAI_ENDPOINT in endpoint_options else "Custom..."
            selected_endpoint = st.selectbox(
                "Azure Endpoint",
                options=endpoint_options,
                index=endpoint_options.index(default_endpoint) if default_endpoint in endpoint_options else 0
            )
            
            if selected_endpoint == "Custom...":
                azure_endpoint = st.text_input(
                    "Enter Custom Endpoint",
                    value=config.AZURE_OPENAI_ENDPOINT or "",
                    placeholder="https://your-endpoint.openai.azure.com"
                )
            else:
                azure_endpoint = selected_endpoint
            
            # Model/Deployment dropdown with custom option
            model_options = [
                "gpt-4o",
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "Custom..."
            ]
            
            default_model = config.AZURE_OPENAI_DEPLOYMENT if config.AZURE_OPENAI_DEPLOYMENT in model_options else "Custom..."
            selected_model = st.selectbox(
                "Model / Deployment",
                options=model_options,
                index=model_options.index(default_model) if default_model in model_options else 0
            )
            
            if selected_model == "Custom...":
                azure_deployment = st.text_input(
                    "Enter Custom Model/Deployment",
                    value=config.AZURE_OPENAI_DEPLOYMENT or "",
                    placeholder="your-deployment-name"
                )
            else:
                azure_deployment = selected_model
            
            # API Key input
            azure_api_key = st.text_input(
                "Azure OpenAI API Key",
                value=config.AZURE_OPENAI_API_KEY or "",
                type="password",
                placeholder="Enter your API key"
            )
        
        with st.expander("🗄️ Database Settings", expanded=False):
            # Database Server dropdown with custom option
            server_options = [
                "localhost",
                "127.0.0.1",
                "Custom..."
            ]
            
            default_server = config.DB_SERVER if config.DB_SERVER in server_options else "Custom..."
            selected_server = st.selectbox(
                "Database Server",
                options=server_options,
                index=server_options.index(default_server) if default_server in server_options else 0
            )
            
            if selected_server == "Custom...":
                db_server = st.text_input(
                    "Enter Custom Server",
                    value=config.DB_SERVER or "",
                    placeholder="server-name or IP address"
                )
            else:
                db_server = selected_server
            
            # Database Name
            db_name = st.text_input(
                "Database Name",
                value=config.DB_NAME or "SchoolDB",
                placeholder="SchoolDB"
            )
            
            # Username
            db_username = st.text_input(
                "Username",
                value=config.DB_USERNAME or "",
                placeholder="Enter database username"
            )
            
            # Password
            db_password = st.text_input(
                "Password",
                value=config.DB_PASSWORD or "",
                type="password",
                placeholder="Enter database password"
            )
        
        # Apply configuration button
        if st.button("💾 Apply Configuration", type="primary"):
            # Update config module with new values
            config.AZURE_OPENAI_ENDPOINT = azure_endpoint
            config.AZURE_OPENAI_DEPLOYMENT = azure_deployment
            config.AZURE_OPENAI_API_KEY = azure_api_key
            config.DB_SERVER = db_server
            config.DB_NAME = db_name
            config.DB_USERNAME = db_username
            config.DB_PASSWORD = db_password
            
            # Rebuild connection string
            config.CONNECTION_STRING = config.build_connection_string(
                db_server, db_name, db_username, db_password
            )
            
            # Reinitialize OpenAI client in session state
            try:
                st.session_state.openai_client = AzureOpenAI(
                    api_key=azure_api_key,
                    api_version=config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=azure_endpoint
                )
            except Exception as e:
                st.error(f"Failed to initialize OpenAI client: {e}")
                st.stop()
            
            # Clear schema cache to reload with new DB connection
            st.cache_data.clear()
            st.session_state.config_updated = True
            st.success("✅ Configuration updated successfully!")
            st.rerun()
        
        st.markdown("---")
        
        # Current Configuration Display
        with st.expander("📊 Current Active Configuration", expanded=False):
            st.write(f"**Endpoint:** {config.AZURE_OPENAI_ENDPOINT}")
            st.write(f"**Model:** {config.AZURE_OPENAI_DEPLOYMENT}")
            st.write(f"**Database:** {config.DB_NAME} on {config.DB_SERVER}")
        
        # Add refresh schema button
        if st.button("🔄 Refresh Database Schema"):
            st.cache_data.clear()
            st.success("Schema cache cleared! Schema will be refreshed on next query.")
        
        st.markdown("---")
        st.write("Enter a natural language question below. Press Enter to send. The assistant will generate a SQL SELECT query, execute it against the database, and summarize the results.")
        st.info("💡 The database schema is automatically retrieved and cached. Click 'Refresh Database Schema' if you've made changes to your database structure.")
        
        # Add expandable section to view the retrieved schema
        with st.expander("📋 View Retrieved Database Schema"):
            current_schema = get_database_schema(
                config.CONNECTION_STRING,
                config.DB_SERVER,
                config.DB_NAME
            )
            st.code(current_schema, language="text")

    # Get dynamic description based on tables
    dynamic_description = get_dynamic_app_description()
    st.write(dynamic_description)

    # Initialize chat history in session_state with dynamic welcome message
    if "messages" not in st.session_state:
        dynamic_welcome = get_dynamic_welcome_message()
        st.session_state.messages = [
            {"role": "assistant", "content": dynamic_welcome}
        ]
    
    # Limit chat history to prevent memory issues
    if len(st.session_state.messages) > MAX_CHAT_MESSAGES:
        # Keep first (welcome) + last N messages
        st.session_state.messages = [
            st.session_state.messages[0]
        ] + st.session_state.messages[-(MAX_CHAT_MESSAGES-1):]

    # Display chat history
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        with st.chat_message(role):
            # content can be plain text or markdown
            st.markdown(content)

    # Use Streamlit's chat_input so Enter submits the prompt
    if prompt := st.chat_input("Type your question and press Enter"):
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant placeholder while processing
        #with st.chat_message("assistant"):
        #    message_placeholder = st.empty()
        #    message_placeholder.markdown("Processing your request... ⏳")

        # Process the prompt: get SQL or conversational response
        # Pass conversation history for context-aware responses
        response, needs_database = get_sql_query_from_ai(prompt, st.session_state.messages)

        # Handle errors
        if isinstance(response, str) and response.startswith("Error:"):
            assistant_content = f"❌ {response}"
            # Update placeholder and append to history
            with st.chat_message("assistant"):
                st.markdown(assistant_content)
            st.session_state.messages.append({"role": "assistant", "content": assistant_content})
            return

        if not needs_database:
            # Conversational response (no DB query)
            assistant_content = response
            with st.chat_message("assistant"):
                st.markdown(assistant_content)
            st.session_state.messages.append({"role": "assistant", "content": assistant_content})
            return

        # It's a SQL query
        query = fix_sql_syntax(response)

        # Show generated SQL in the assistant message
        #with st.chat_message("assistant"):
        #    st.markdown("**Generated SQL Query:**")
        #    st.code(query, language="sql")

        # Execute the query (but do NOT display raw results to the user).
        # We still run the query so the AI can summarize the actual data.
        with st.spinner("Executing SQL query..."):
            results = query_db(query)

        if isinstance(results, dict) and "error" in results:
            assistant_content = f"❌ Database Error: {results['error']}"
            with st.chat_message("assistant"):
                st.markdown(assistant_content)
            st.session_state.messages.append({"role": "assistant", "content": assistant_content})
            return

        # Generate a natural-language summary from the query results
        summary = get_ai_summary(prompt, query, results)

        with st.chat_message("assistant"):
            # Display the summary
            st.markdown(summary)
            
            # Display results as a table if there are multiple rows
            if results and len(results) > 0:
                st.markdown("**Results:**")
                
                # Check if it's a single value result
                if len(results) == 1 and len(results[0]) == 1:
                    # Single value - just show it
                    key = list(results[0].keys())[0]
                    value = results[0][key]
                    st.info(f"**{key}:** {value}")
                else:
                    # Multiple rows or columns - show as dataframe
                    try:
                        # Limit displayed rows for very large results
                        if len(results) > MAX_DISPLAY_ROWS:
                            st.warning(f"⚠️ Showing first {MAX_DISPLAY_ROWS} of {len(results)} results")
                            display_results = results[:MAX_DISPLAY_ROWS]
                        else:
                            display_results = results
                        
                        df = pd.DataFrame(display_results)
                        
                        # Convert any remaining object columns to strings
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                df[col] = df[col].astype(str)
                        
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying table: {e}")
                        st.json(results[:10])  # Fallback to JSON
            elif not results or len(results) == 0:
                st.info("✓ Query executed successfully but returned no results.")
            
            # Show the SQL query
            st.markdown("**SQL Query:**")
            st.code(query, language="sql")

        # Append assistant summary (and SQL) to chat history for persistence.
        # Note: We don't include the full table in history to keep it manageable
        combined = f"{summary}\n\n**SQL Query:**\n```sql\n{query}\n```"
        st.session_state.messages.append({"role": "assistant", "content": combined})


if __name__ == "__main__":
    main()