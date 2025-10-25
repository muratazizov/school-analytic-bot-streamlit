
================================================================================
                    SCHOOL DATABASE CHATBOT
                    Powered by Azure OpenAI
================================================================================

PROJECT OVERVIEW
================================================================================
This is an intelligent chatbot application that allows users to query a school
to convert user questions into SQL queries, executes them against a SQL Server
database, and returns results in a conversational format.

FEATURES
================================================================================
✓ Azure OpenAI GPT-4o integration
✓ SQL Server database with 9 comprehensive tables
✓ Automatic SQL syntax correction (LIMIT → TOP)

 If you use Streamlit you'll get a browser-based chat interface.

 STREAMLIT USAGE (WEB UI)
 -------------------------
 - Open the URL shown in the terminal after running `streamlit run app.py` (usually http://localhost:8501).
 - Use the text area to enter natural language questions and click the Ask button.
 - The app will display the generated SQL, show results in a table, and provide a natural-language summary.

 TIPS: session-state & caching
 -----------------------------
 - The Streamlit app can store conversation history in `st.session_state` so messages persist across interactions.
 - Cache expensive operations (AI calls or DB queries) with `st.cache_data` / `st.cache_resource` to improve responsiveness during development.
 - Example patterns:
    - Cache database connection objects with `st.cache_resource`.
    - Cache query results with `st.cache_data(key=...)` when the same SQL is executed repeatedly.

 Security note: avoid caching sensitive credentials or API keys. Keep secrets in environment variables or the Streamlit secrets manager.
TECHNOLOGY STACK
================================================================================
- Azure OpenAI API (GPT-4o)
 - Streamlit (Web UI)

PROJECT STRUCTURE
================================================================================
school-chatbot/
│
├── app.py                 # Main application file
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── school_db.sql         # Database creation script
└── README.txt            # This file

INSTALLATION GUIDE
================================================================================

STEP 1: PREREQUISITES
---------------------
Before you begin, ensure you have:
- Python 3.8 or higher installed
- Microsoft SQL Server installed and running
- SQL Server ODBC Driver 17 installed
- Azure OpenAI API access with valid credentials
- pip (Python package manager)

STEP 2: DOWNLOAD PROJECT FILES
-------------------------------
Download all project files to a directory, for example:
C:\Projects\school-chatbot\

STEP 3: INSTALL PYTHON DEPENDENCIES
------------------------------------
Open Command Prompt or Terminal in the project directory and run:

    pip install -r requirements.txt

This will install:
- openai>=1.12.0
- pyodbc>=5.0.1
- python-dotenv>=1.0.0
 - streamlit (optional, for web UI)

STEP 4: CONFIGURE ENVIRONMENT VARIABLES
----------------------------------------
Create a file named ".env" in the project root directory with the following:

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://ai-proxy.lab.epam.com
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Database Configuration
DB_SERVER=localhost
DB_NAME=SchoolDB
DB_USERNAME=sa
DB_PASSWORD=your_password

IMPORTANT: Replace the placeholder values with your actual credentials!

STEP 5: CREATE DATABASE
------------------------
1. Open SQL Server Management Studio (SSMS)
2. Connect to your SQL Server instance
3. Open the "school_db.sql" file
4. Execute the script (F5 or click Execute)
5. Verify that the SchoolDB database is created with sample data

STEP 6: RUN THE APPLICATION
----------------------------
In the project directory, run:

Option A — Run as a console app (original behavior):

   python app.py

Option B — Run with Streamlit (recommended for a web UI):

   streamlit run app.py

If you use Streamlit you'll get a browser-based chat interface. You should see:
======================================================================
🏫 SCHOOL DATABASE CHATBOT (Azure OpenAI)
======================================================================

USAGE GUIDE
================================================================================

STARTING THE CHATBOT
---------------------
Run: python app.py

The chatbot will display connection information and wait for your input.

ASKING QUESTIONS
----------------
Simply type your question in natural language. Examples:

STUDENTS:
- "How many students are studying at school?"
- "Show me all students in grade 9"
- "Who is the best student?"
- "List top 5 students by average score"

TEACHERS:
- "List all teachers"
- "Show me teachers in the Mathematics department"
- "Who teaches Biology?"

GRADES & SCORES:
- "What is John Adams' math score?"
- "Show me all scores for Emily Johnson"
- "What are the average scores by subject?"
- "The most successful student"

LIBRARY:
- "What books has John Adams checked out?"
- "Show me all available books"
- "Which books are currently checked out?"

ATTENDANCE:
- "Show John Adams' attendance record"
- "How many days was Michael Brown absent?"

GENERAL QUESTIONS:
- "What can you do?"
- "Help"
- "Hello"

EXITING THE CHATBOT
-------------------
Type any of these commands:
- quit
- exit
- bye

Or press Ctrl+C

HOW IT WORKS
================================================================================

WORKFLOW:
---------
1. User enters a question in natural language
2. Question is sent to Azure OpenAI GPT-4o
3. AI converts the question to a SQL query
4. SQL syntax is automatically corrected for SQL Server
5. Query is executed against the database
6. Results are retrieved and formatted
7. AI generates a natural language summary
8. Response is displayed to the user

KEY FUNCTIONS:
--------------
- query_db(query)           : Executes SQL query and returns results
- get_sql_query_from_ai()   : Converts natural language to SQL
- fix_sql_syntax()          : Corrects SQL syntax for SQL Server
- get_ai_summary()          : Generates natural language response
- main()                    : Main chatbot loop

DATABASE SCHEMA
================================================================================

TABLES:
-------
1. Students         - Student information and enrollment
2. Teachers         - Teacher information and departments
3. Subjects         - Course subjects and descriptions
4. Classes          - Class schedules and assignments
5. ClassEnrollments - Student-class relationships
6. Scores           - Student grades by quarter
7. Attendance       - Daily attendance records
8. Books            - Library book inventory
9. LibraryCheckouts - Book checkout history

SAMPLE DATA:
------------
- 8 Students (grades 7-11)
- 4 Teachers (Math, English, Science, History)
- 5 Subjects
- 5 Classes (Fall 2024 semester)
- Multiple scores, attendance records, and library checkouts

TROUBLESHOOTING
================================================================================

PROBLEM: "Cannot connect to database"
SOLUTION:
- Verify SQL Server is running
- Check DB_SERVER, DB_USERNAME, DB_PASSWORD in .env
- Ensure SQL Server allows SQL authentication
- Test connection using SSMS

PROBLEM: "Azure OpenAI API error"
SOLUTION:
- Verify AZURE_OPENAI_API_KEY is correct
- Check endpoint URL is accessible
- Ensure you have API quota available
- Verify deployment name is correct (gpt-4o)

PROBLEM: "Incorrect syntax near 'LIMIT'"
SOLUTION:
- This should be automatically fixed by fix_sql_syntax()
- If persists, update the SYSTEM_PROMPT to emphasize SQL Server syntax
- Manually check the generated query

PROBLEM: "Object of type Decimal is not JSON serializable"
SOLUTION:
- This is fixed in query_db() function
- Ensure you're using the latest version of app.py
- Decimal values are automatically converted to float

PROBLEM: "Module not found" errors
SOLUTION:
- Run: pip install -r requirements.txt
- Ensure you're in the correct directory
- Check Python version (3.8+)

PROBLEM: Slow responses
SOLUTION:
- Azure OpenAI might be rate-limited
- Check your internet connection
- Verify API endpoint is responsive
- Consider reducing temperature parameter

CONFIGURATION OPTIONS
================================================================================

AZURE OPENAI SETTINGS (config.py):
-----------------------------------
- AZURE_OPENAI_API_KEY      : Your API key
- AZURE_OPENAI_ENDPOINT     : API endpoint URL
- AZURE_OPENAI_API_VERSION  : API version
- AZURE_OPENAI_DEPLOYMENT   : Model deployment name

DATABASE SETTINGS (config.py):
-------------------------------
- DB_SERVER                 : SQL Server hostname/IP
- DB_NAME                   : Database name (SchoolDB)
- DB_USERNAME               : SQL Server username
- DB_PASSWORD               : SQL Server password
- DB_DRIVER                 : ODBC driver name

AI BEHAVIOR (app.py):
---------------------
- temperature               : 0 for SQL generation (deterministic)
                             0.7 for summaries (creative)
- SYSTEM_PROMPT            : Instructions for AI behavior
- DATABASE_SCHEMA          : Schema information for AI

SECURITY CONSIDERATIONS
================================================================================

IMPORTANT SECURITY NOTES:
-------------------------
1. NEVER commit .env file to version control
2. Use strong passwords for database access
3. Restrict database user permissions (SELECT only recommended)
4. Keep Azure OpenAI API key confidential
5. Use environment variables for all sensitive data
6. Consider implementing rate limiting for production use
7. Validate and sanitize all user inputs
8. Use parameterized queries (already implemented)

BEST PRACTICES:
---------------
- Regularly rotate API keys
- Use separate credentials for development/production
- Monitor API usage and costs
- Implement logging for audit trails
- Regular database backups
- Keep dependencies updated

EXTENDING THE APPLICATION
================================================================================

OPTIONAL ENHANCEMENTS:
----------------------
1. Web Interface
   - Add Flask or FastAPI
   - Create HTML/CSS frontend
   - Deploy to cloud (Azure, AWS, etc.)

2. Query History
   - Save conversation logs
   - Implement session management
   - Add query analytics

3. Export Functionality
   - Export results to CSV
   - Generate PDF reports
   - Excel integration

4. Visualization
   - Add charts for grades
   - Attendance graphs
   - Performance dashboards

5. Authentication
   - User login system
   - Role-based access control
   - Student/Teacher/Admin roles

6. Advanced Features
   - Voice input (speech-to-text)
   - Multi-language support
   - Email notifications
   - Scheduled reports

ADDING NEW TABLES:
------------------
1. Create table in SQL Server
2. Update DATABASE_SCHEMA in app.py
3. Add example queries to SYSTEM_PROMPT
4. Test with various questions

MODIFYING AI BEHAVIOR:
----------------------
Edit SYSTEM_PROMPT in app.py to:
- Add new query patterns
- Change response style
- Add domain-specific rules
- Improve query accuracy

SAMPLE QUERIES & EXPECTED RESULTS
================================================================================

QUERY: "How many students are studying at school?"
SQL: SELECT COUNT(*) AS TotalStudents FROM Students WHERE IsActive = 1;
RESULT: 8 students

QUERY: "Who is the best student?"
SQL: SELECT TOP 1 s.FirstName + ' ' + s.LastName AS StudentName, 
     AVG(sc.Score) AS AverageScore FROM Scores sc 
     JOIN Students s ON sc.StudentID = s.StudentID 
     WHERE s.IsActive = 1 
     GROUP BY s.StudentID, s.FirstName, s.LastName 
     ORDER BY AverageScore DESC;
RESULT: Emily Johnson with average score 93.17

QUERY: "What books has John Adams checked out?"
SQL: SELECT b.Title, b.Author, lc.CheckoutDate, lc.Status 
     FROM LibraryCheckouts lc 
     JOIN Books b ON lc.BookID = b.BookID 
     JOIN Students s ON lc.StudentID = s.StudentID 
     WHERE s.FirstName = 'John' AND s.LastName = 'Adams';
RESULT: 3 books (To Kill a Mockingbird, The Hunger Games, Harry Potter)

QUERY: "List all teachers in Mathematics department"
SQL: SELECT FirstName + ' ' + LastName AS TeacherName, Email, HireDate 
     FROM Teachers 
     WHERE Department = 'Mathematics' AND IsActive = 1;
RESULT: Robert Thompson

FREQUENTLY ASKED QUESTIONS (FAQ)
================================================================================

Q: Can I use a different database (MySQL, PostgreSQL)?
A: Yes, but you'll need to modify the connection string and SQL syntax
   in query_db() and fix_sql_syntax() functions.

Q: Can I use regular OpenAI instead of Azure OpenAI?
A: Yes, change the import to "from openai import OpenAI" and update
   the client initialization in app.py.

Q: How much does it cost to run?
A: Costs depend on Azure OpenAI usage. Each query makes 2 API calls
   (one for SQL generation, one for summary). Monitor your usage.

Q: Can multiple users use this simultaneously?
A: The current version is single-user. For multi-user, implement
   a web server with session management.

Q: How accurate are the SQL queries?
A: Accuracy depends on question clarity and AI training. The system
   includes examples and schema information to improve accuracy.

Q: Can I add more sample data?
A: Yes, add INSERT statements to school_db.sql or use SSMS to
   manually insert data.

Q: Is this production-ready?
A: This is a solid foundation but consider adding:
   - Authentication
   - Rate limiting
   - Comprehensive logging
   - Error monitoring
   - Load balancing (for web version)

Q: Can I modify the database schema?
A: Yes, but update DATABASE_SCHEMA in app.py to match your changes.

SUPPORT & RESOURCES
================================================================================

DOCUMENTATION:
--------------
- Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- pyodbc: https://github.com/mkleehammer/pyodbc
- SQL Server: https://docs.microsoft.com/en-us/sql/

COMMON RESOURCES:
-----------------
- Python Documentation: https://docs.python.org/3/
- SQL Server Management Studio: Download from Microsoft
- ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/

GETTING HELP:
-------------
For issues with:
- Azure OpenAI: Check Azure portal and documentation
- SQL Server: Verify connection and permissions
- Python: Check error messages and stack traces

VERSION HISTORY
================================================================================

Version 1.0.0 (Current)
-----------------------
- Initial release
- Azure OpenAI integration
- SQL Server database support
- Natural language query processing
- Automatic SQL syntax correction
- Decimal type handling
- Conversational responses
- Error handling and recovery

CREDITS & LICENSE
================================================================================

This project demonstrates integration of:
- Azure OpenAI API for natural language processing
- SQL Server for data storage
- Python for application logic

Feel free to modify and extend this application for your needs.

================================================================================
                        END OF README
================================================================================

For questions or issues, please review the Troubleshooting section above.