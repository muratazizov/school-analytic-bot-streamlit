import pyodbc
import json
import re
from decimal import Decimal
import datetime
import streamlit as st
from openai import AzureOpenAI
import config

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=config.AZURE_OPENAI_API_KEY,
    api_version=config.AZURE_OPENAI_API_VERSION,
    azure_endpoint=config.AZURE_OPENAI_ENDPOINT
)

# Database schema information for AI
DATABASE_SCHEMA = """
DATABASE SCHEMA:

Table: Students
- StudentID (INT, PRIMARY KEY)
- FirstName (NVARCHAR(50))
- LastName (NVARCHAR(50))
- DateOfBirth (DATE)
- Grade (INT) - Grade level 1-12
- EnrollmentDate (DATE)
- Email (NVARCHAR(100))
- IsActive (BIT) - 1=active, 0=inactive

Table: Teachers
- TeacherID (INT, PRIMARY KEY)
- FirstName (NVARCHAR(50))
- LastName (NVARCHAR(50))
- Email (NVARCHAR(100))
- HireDate (DATE)
- Department (NVARCHAR(50))
- IsActive (BIT)

Table: Subjects
- SubjectID (INT, PRIMARY KEY)
- SubjectName (NVARCHAR(100))
- SubjectCode (NVARCHAR(10))
- Description (NVARCHAR(500))
- CreditHours (INT)

Table: Classes
- ClassID (INT, PRIMARY KEY)
- SubjectID (INT, FOREIGN KEY)
- TeacherID (INT, FOREIGN KEY)
- Grade (INT)
- Section (NVARCHAR(10))
- AcademicYear (INT)
- Semester (NVARCHAR(20)) - 'Fall' or 'Spring'
- RoomNumber (NVARCHAR(20))

Table: ClassEnrollments
- EnrollmentID (INT, PRIMARY KEY)
- StudentID (INT, FOREIGN KEY)
- ClassID (INT, FOREIGN KEY)
- EnrollmentDate (DATE)

Table: Scores
- ScoreID (INT, PRIMARY KEY)
- StudentID (INT, FOREIGN KEY)
- ClassID (INT, FOREIGN KEY)
- Quarter (INT) - 1, 2, 3, or 4
- Score (DECIMAL(5,2)) - 0-100
- LetterGrade (NVARCHAR(2))
- RecordedDate (DATE)

Table: Attendance
- AttendanceID (INT, PRIMARY KEY)
- StudentID (INT, FOREIGN KEY)
- ClassID (INT, FOREIGN KEY)
- AttendanceDate (DATE)
- Status (NVARCHAR(20)) - 'Present', 'Absent', 'Tardy', 'Excused'
- Notes (NVARCHAR(500))

Table: Books
- BookID (INT, PRIMARY KEY)
- ISBN (NVARCHAR(20))
- Title (NVARCHAR(200))
- Author (NVARCHAR(100))
- Publisher (NVARCHAR(100))
- PublicationYear (INT)
- Category (NVARCHAR(50))
- TotalCopies (INT)
- AvailableCopies (INT)

Table: LibraryCheckouts
- CheckoutID (INT, PRIMARY KEY)
- BookID (INT, FOREIGN KEY)
- StudentID (INT, FOREIGN KEY)
- CheckoutDate (DATE)
- DueDate (DATE)
- ReturnDate (DATE) - NULL if not returned
- Status (NVARCHAR(20)) - 'Checked Out', 'Returned', 'Overdue'
"""

# System prompt for AI
SYSTEM_PROMPT = f"""You are a helpful assistant for a school database system. 
Your job is to convert user questions into SQL queries for Microsoft SQL Server.

{DATABASE_SCHEMA}

IMPORTANT RULES:
1. If the user asks a question that requires database information, generate a SQL SELECT query
2. If the user asks general questions like "What can you do?", "Help", "Hello", respond with "NO_QUERY_NEEDED:" followed by your response
3. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
4. Use proper JOIN syntax when querying multiple tables
5. Use WHERE clauses for filtering
6. For student names, join FirstName and LastName
7. Current academic year is 2024, semester is 'Fall'
8. Always check IsActive = 1 for active students/teachers

SQL SERVER SPECIFIC SYNTAX (VERY IMPORTANT):
- Use TOP N instead of LIMIT N (e.g., SELECT TOP 1 * FROM Students)
- Use + for string concatenation (e.g., FirstName + ' ' + LastName)
- Use GETDATE() for current date
- Use DATEPART() for date parts
- Use LEN() instead of LENGTH()
- Use ISNULL() instead of IFNULL()
- When using GROUP BY with aggregates, include all non-aggregated columns

RESPONSE FORMAT:
- If a database query is needed: Return ONLY the SQL query
- If no query is needed: Start with "NO_QUERY_NEEDED:" followed by your conversational response

EXAMPLES:

User: "How many students are studying at school?"
Response: SELECT COUNT(*) AS TotalStudents FROM Students WHERE IsActive = 1;

User: "What books has John Adams checked out?"
Response: SELECT b.Title, b.Author, lc.CheckoutDate, lc.Status FROM LibraryCheckouts lc JOIN Books b ON lc.BookID = b.BookID JOIN Students s ON lc.StudentID = s.StudentID WHERE s.FirstName = 'John' AND s.LastName = 'Adams';

User: "What is John Adams' math score for quarter 3?"
Response: SELECT sc.Score, sc.LetterGrade FROM Scores sc JOIN Students s ON sc.StudentID = s.StudentID JOIN Classes c ON sc.ClassID = c.ClassID JOIN Subjects sub ON c.SubjectID = sub.SubjectID WHERE s.FirstName = 'John' AND s.LastName = 'Adams' AND sub.SubjectName LIKE '%Math%' AND sc.Quarter = 3;

User: "The most successful student" or "The best student"
Response: SELECT TOP 1 s.FirstName + ' ' + s.LastName AS StudentName, AVG(sc.Score) AS AverageScore FROM Scores sc JOIN Students s ON sc.StudentID = s.StudentID WHERE s.IsActive = 1 GROUP BY s.StudentID, s.FirstName, s.LastName ORDER BY AverageScore DESC;

User: "Show me the top 5 students by average score"
Response: SELECT TOP 5 s.FirstName + ' ' + s.LastName AS StudentName, AVG(sc.Score) AS AverageScore FROM Scores sc JOIN Students s ON sc.StudentID = s.StudentID WHERE s.IsActive = 1 GROUP BY s.StudentID, s.FirstName, s.LastName ORDER BY AverageScore DESC;

User: "List all teachers"
Response: SELECT FirstName + ' ' + LastName AS TeacherName, Department, Email FROM Teachers WHERE IsActive = 1;

User: "Show me students in grade 9"
Response: SELECT FirstName + ' ' + LastName AS StudentName, Email, Grade FROM Students WHERE Grade = 9 AND IsActive = 1;

User: "What can you do?"
Response: NO_QUERY_NEEDED: I can help you retrieve information from the school database! I can answer questions about:
- Students (enrollment, grades, contact information)
- Teachers (departments, contact information)
- Classes and subjects
- Student scores and grades by quarter
- Attendance records
- Library books and checkouts
Just ask me a question and I'll query the database for you!

User: "Hello"
Response: NO_QUERY_NEEDED: Hello! I'm your school database assistant. How can I help you today?

User: "Help"
Response: NO_QUERY_NEEDED: I can help you find information about students, teachers, classes, grades, attendance, and library books. Try asking questions like:
- "How many students are enrolled?"
- "What books has [student name] checked out?"
- "What is [student name]'s score in [subject]?"
- "Show me all teachers in the Mathematics department"
- "Who is the best student?"

Now process the user's input.
"""


def query_db(query):
    """
    Execute SQL query and return results.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        list: Query results as list of dictionaries
    """
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
                    # Convert Decimal to float, round to 2 decimal places
                    row_dict[column_name] = round(float(value), 2)
                elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                    # Handle datetime objects
                    row_dict[column_name] = value.isoformat()
                elif isinstance(value, (bytes, bytearray)):
                    # Handle binary data
                    row_dict[column_name] = value.decode('utf-8', errors='ignore')
                elif isinstance(value, bool):
                    # Handle boolean
                    row_dict[column_name] = value
                elif isinstance(value, (int, float, str)):
                    # Handle basic types
                    row_dict[column_name] = value
                else:
                    # Fallback: convert to string
                    row_dict[column_name] = str(value)
                    
            results.append(row_dict)
        
        # Close connection
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        return {"error": str(e)}


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


def get_sql_query_from_ai(user_prompt):
    """
    Send user prompt to Azure OpenAI and get SQL query or conversational response.
    
    Args:
        user_prompt (str): User's question
        
    Returns:
        tuple: (query_or_response, needs_database)
            - query_or_response: SQL query or conversational response
            - needs_database: True if database query needed, False otherwise
    """
    try:
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Check if AI indicates no query is needed
        if ai_response.startswith("NO_QUERY_NEEDED:"):
            conversational_response = ai_response.replace("NO_QUERY_NEEDED:", "").strip()
            return conversational_response, False
        
        # Remove markdown code blocks if present
        query = ai_response
        if query.startswith("```sql"):
            query = query[6:]
        if query.startswith("```"):
            query = query[3:]
        if query.endswith("```"):
            query = query[:-3]
        
        query = query.strip()
        
        # Verify it's actually a SQL query
        if not is_sql_query(query):
            # If it's not a SQL query, treat it as a conversational response
            return query, False
        
        return query, True
    
    except Exception as e:
        return f"Error: {str(e)}", False


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
    
    Args:
        user_prompt (str): Original user question
        query (str): SQL query that was executed
        results (list): Query results
        
    Returns:
        str: Natural language summary
    """
    try:
        summary_prompt = f"""
User asked: "{user_prompt}"

SQL Query executed: {query}

Results: {json.dumps(results, indent=2)}

Provide a clear, natural language answer to the user's question based on these results.
Be concise and friendly. If there are multiple results, summarize them clearly.
"""
        
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains database query results in natural language."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def main():
    """Streamlit chat-style UI using `st.chat_input` and `st.chat_message`."""
    st.set_page_config(page_title="School DB Chatbot", layout="wide")

    st.title("🏫 School Database Chatbot (Azure OpenAI)")

    with st.sidebar:
        st.header("Configuration")
        st.write(f"**Azure Endpoint:** {config.AZURE_OPENAI_ENDPOINT}")
        st.write(f"**Model / Deployment:** {config.AZURE_OPENAI_DEPLOYMENT}")
        st.write(f"**Database:** {config.DB_NAME} on {config.DB_SERVER}")
        st.markdown("---")
        st.write("Enter a natural language question below. Press Enter to send. The assistant will generate a SQL SELECT query, execute it against the database, and summarize the results.")

    st.write("Ask me questions about students, teachers, classes, grades, attendance, or library books.")

    # Initialize chat history in session_state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your school database assistant. Ask me about students, teachers, classes, grades, attendance, or library books."}
        ]

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
        response, needs_database = get_sql_query_from_ai(prompt)

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

        # Generate a natural-language summary from the query results and show only
        # the generated SQL and the assistant's summary to the user.
        summary = get_ai_summary(prompt, query, results)

        with st.chat_message("assistant"):
            #st.markdown("**Answer:**")
            st.markdown(summary)
            st.markdown("**SQL Query:**")
            st.code(query, language="sql")

        # Append assistant summary (and SQL) to chat history for persistence.
        combined = f"Generated SQL Query:\n{query}\n\nAssistant Summary:\n{summary}"
        st.session_state.messages.append({"role": "assistant", "content": combined})


if __name__ == "__main__":
    main()