# 🤖 Database Chatbot (Azure OpenAI)

> Powered by Azure OpenAI GPT-4o

A general-purpose intelligent chatbot that works with any SQL Server database. Ask questions in natural language and get instant answers from your data.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Usage Guide](#usage-guide)
- [How It Works](#how-it-works)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Configuration Options](#configuration-options)
- [Security Considerations](#security-considerations)
- [Extending the Application](#extending-the-application)
- [Sample Queries](#sample-queries)
- [FAQ](#faq)
- [Support & Resources](#support--resources)

---

## 🎯 Project Overview

This is an intelligent chatbot application that allows users to query **any SQL Server database** using natural language. The application automatically detects your database structure, converts user questions into SQL queries, executes them, and returns results in a conversational format.

**Perfect for:**
- School and educational institutions
- Corporate databases
- E-commerce and inventory systems
- HR and employee management systems
- Customer relationship management (CRM)
- Any SQL Server database with structured data

---

## ✨ Features

- ✅ **Azure OpenAI GPT-4o Integration** - Advanced natural language processing
- ✅ **Dynamic Schema Detection** - Automatically retrieves and adapts to database structure
- ✅ **Multi-Schema Support** - Detects all schemas (dbo, SalesLT, HumanResources, etc.)
- ✅ **Dynamic Interface** - Title, descriptions, and messages adapt to actual database content
- ✅ **Interactive Results Table** - Pandas DataFrame with sortable, searchable data display
- ✅ **SQL Server Database** - Supports any database with multiple tables
- ✅ **Automatic SQL Syntax Correction** - Converts LIMIT → TOP for SQL Server
- ✅ **Streamlit Web Interface** - Beautiful browser-based chat interface
- ✅ **Real-time Configuration** - Change database and AI settings without restarting
- ✅ **Real-time Query Execution** - Instant results from database
- ✅ **Natural Language Responses** - AI-generated conversational summaries
- ✅ **Schema Caching** - Optimized performance with 1-hour cache

### 🌐 Streamlit Web UI

When using Streamlit, you'll get a browser-based chat interface with:
- **Chat-style interaction** - Press Enter to submit questions (no button needed)
- **Dynamic title** - Automatically shows your database name
- **Dynamic descriptions** - Lists actual tables from your database (across all schemas)
- **Interactive data tables** - Sortable, searchable results with pandas DataFrames
- **Message history** - Persistent conversation throughout session
- **Generated SQL query display** - See the SQL that was executed
- **Natural language summaries** - AI explains results in plain English
- **Live configuration** - Change Azure OpenAI and database settings on the fly
- **Schema viewer** - Inspect your complete database structure (all schemas) in the sidebar
- **Full-width display** - Tables use container width for optimal viewing

#### 💡 Streamlit Tips

**Session State & Caching:**
- Store conversation history in `st.session_state` for persistent interactions
- Cache expensive operations (AI calls, DB queries) with `st.cache_data` / `st.cache_resource`
- Example patterns:
  - Cache database connections: `st.cache_resource`
  - Cache query results: `st.cache_data(key=...)`

> ⚠️ **Security Note:** Never cache sensitive credentials or API keys. Keep secrets in environment variables or Streamlit secrets manager.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Azure OpenAI API (GPT-4o) | Natural language processing |
| SQL Server | Database management |
| Python 3.8+ | Application logic |
| Streamlit >=1.28.0 | Web interface with interactive components |
| Pandas >=2.0.0 | Data manipulation and table display |
| pyodbc >=5.0.1 | Database connectivity |

---

## 📁 Project Structure

```plaintext
school-analytic-bot-streamlit/
│
├── app.py                 # Main application file
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── school_db.sql         # Sample database (school example)
├── DYNAMIC_INTERFACE.md  # Documentation for dynamic features
└── README.md             # This file
```

---

## 📥 Installation Guide

### Step 1: Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ Microsoft SQL Server installed and running
- ✅ SQL Server ODBC Driver 17 installed
- ✅ Azure OpenAI API access with valid credentials
- ✅ pip (Python package manager)

### Step 2: Download Project Files

Download all project files to a directory, for example:

```plaintext
C:\Projects\school-chatbot\
```

### Step 3: Install Python Dependencies

Open Command Prompt or Terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `openai>=1.12.0` - Azure OpenAI client
- `pyodbc>=5.0.1` - Database connectivity
- `python-dotenv>=1.0.0` - Environment variable management
- `streamlit>=1.28.0` - Web UI framework with interactive components
- `pandas>=2.0.0` - Data manipulation and DataFrame display

### Step 4: Configure Environment Variables

Create a file named `.env` in the project root directory with the following content:

```env
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
```

> ⚠️ **IMPORTANT:** Replace the placeholder values with your actual credentials!

### Step 5: Create or Connect to Database

**Option A - Use the Sample School Database:**

1. Open **SQL Server Management Studio (SSMS)**
2. Connect to your SQL Server instance
3. Open the `school_db.sql` file
4. Execute the script (F5 or click Execute)
5. Verify that the SchoolDB database is created with sample data

**Option B - Connect to Your Existing Database:**

1. Ensure your database is accessible and running
2. Note the database name, server address, and credentials
3. Configure the `.env` file with your database details (see Step 4)
4. The app will automatically detect and adapt to your database schema
   - **Multi-schema support**: Detects tables across all schemas (dbo, SalesLT, HumanResources, Production, etc.)
   - **Schema-qualified names**: Tables displayed as `schema.table` for clarity
   - Works with AdventureWorks, WideWorldImporters, and any multi-schema database

### Step 6: Run the Application

In the project directory, run:

**Streamlit Web UI (Recommended):**

```bash
streamlit run app.py
```

The browser-based chat interface will automatically open at `http://localhost:8501`.

The app will automatically:
- Detect your database schema
- Display your database name in the title
- List available tables in the description
- Adapt all messages to match your data structure

---

## 🚀 Usage Guide

### Starting the Chatbot

**Web UI Mode:**
```bash
streamlit run app.py
```

The chatbot will:
1. Connect to your database
2. Retrieve the complete schema automatically (all user schemas)
3. Display a dynamic interface matching your database
4. Show query results as interactive, sortable tables
5. Wait for your questions

### Dynamic Configuration

The app now supports **real-time configuration** through the sidebar:

- **Azure OpenAI Settings**: Change endpoint, model, and API key
- **Database Settings**: Switch between databases without restarting
- **Schema Refresh**: Manually refresh if database structure changes
- **Apply Configuration**: Save and apply changes instantly

### Asking Questions

Simply type your question in natural language. The app adapts to **any database structure**. Here are examples using the sample school database:

#### � Example Queries (School Database)

**Student Queries:**

- "How many students are studying at school?"
- "Show me all students in grade 9"
- "Who is the best student?"
- "List top 5 students by average score"

**Teacher Queries:**

- "List all teachers"
- "Show me teachers in the Mathematics department"
- "Who teaches Biology?"

**Grades & Scores:**

- "What is John Adams' math score?"
- "Show me all scores for Emily Johnson"
- "What are the average scores by subject?"
- "The most successful student"

**Library Queries:**

- "What books has John Adams checked out?"
- "Show me all available books"
- "Which books are currently checked out?"

**Attendance:**

- "Show John Adams' attendance record"
- "How many days was Michael Brown absent?"

#### 💼 Example Queries (Other Database Types)

**For E-commerce Database:**
- "Show me the top 10 selling products this month"
- "What's the total revenue by category?"
- "List all pending orders"

**For HR Database:**
- "How many employees are in each department?"
- "Show me all employees hired in 2024"
- "What's the average salary by position?"

**For CRM Database:**
- "List all customers from New York"
- "Show me active support tickets"
- "What's the customer retention rate?"

**For AdventureWorks Database (Multi-Schema):**
- "List me all Customers" (queries SalesLT.Customer)
- "Show me all products" (queries SalesLT.Product)
- "What are the top 5 orders by total?" (queries SalesLT.SalesOrderHeader)

#### 💬 General Questions

- "What can you do?"
- "Help"
- "Hello"

**Note:** The chatbot automatically adapts its responses based on your actual database tables and structure.

### Exiting the Chatbot

Simply close the browser tab or stop the Streamlit server with **Ctrl+C** in the terminal.

---

## ⚙️ How It Works

### Workflow

```mermaid
graph LR
    A[User Question] --> B[Azure OpenAI GPT-4o]
    B --> C[SQL Query Generation]
    C --> D[Syntax Correction]
    D --> E[Query Execution]
    E --> F[Results Retrieval]
    F --> G[AI Summary]
    G --> H[Display Response]
```

1. **User Input** - User enters a question in natural language
2. **AI Processing** - Question is sent to Azure OpenAI GPT-4o
3. **SQL Generation** - AI converts the question to a SQL query (with schema-qualified table names)
4. **Syntax Correction** - SQL syntax is automatically corrected for SQL Server
5. **Execution** - Query is executed against the database
6. **Results** - Results are retrieved and formatted as pandas DataFrame
7. **Summary** - AI generates a natural language summary
8. **Display** - Shows summary + interactive table + SQL query
9. **Response** - Full response is displayed to the user

### Key Functions

| Function | Purpose |
|----------|---------|
| `get_database_schema()` | Dynamically retrieves database structure from **all user schemas** |
| `get_dynamic_app_title()` | Generates app title based on database name |
| `get_dynamic_app_description()` | Creates description from actual table names (strips schema prefix) |
| `get_dynamic_welcome_message()` | Generates welcome message matching database |
| `query_db(query)` | Executes SQL query and returns results as list of dicts |
| `get_sql_query_from_ai()` | Converts natural language to SQL with schema-qualified names |
| `fix_sql_syntax()` | Corrects SQL syntax for SQL Server (LIMIT→TOP, etc.) |
| `get_ai_summary()` | Generates natural language response |
| `main()` | Main Streamlit UI with chat loop and **DataFrame display** |

---

## 🗄️ Database Schema

### Sample Database (school_db.sql)

The repository includes a sample school database for testing and demonstration purposes:

### Tables Overview

| Table | Description |
|-------|-------------|
| **Students** | Student information and enrollment |
| **Teachers** | Teacher information and departments |
| **Subjects** | Course subjects and descriptions |
| **Classes** | Class schedules and assignments |
| **ClassEnrollments** | Student-class relationships |
| **Scores** | Student grades by quarter |
| **Attendance** | Daily attendance records |
| **Books** | Library book inventory |
| **LibraryCheckouts** | Book checkout history |

### Sample Data

- 📚 **8 Students** (grades 7-11)
- 👨‍🏫 **4 Teachers** (Math, English, Science, History)
- 📖 **5 Subjects**
- 🏛️ **5 Classes** (Fall 2024 semester)

### Multi-Schema Database Support

The application fully supports databases with multiple schemas:

- **Automatic Detection**: Queries `INFORMATION_SCHEMA` to find all user schemas (excludes system schemas)
- **Schema-Qualified Names**: Tables displayed as `schema.table` (e.g., `SalesLT.Customer`, `HumanResources.Employee`)
- **Foreign Key Relationships**: Includes schema in relationship descriptions
- **Compatible Databases**: Works with AdventureWorks, WideWorldImporters, custom multi-schema databases

Example schemas detected:
- `dbo.*` - Default schema tables
- `SalesLT.*` - Sales and customer data
- `HumanResources.*` - Employee information
- `Production.*` - Product catalog
- `Purchasing.*` - Vendor and purchase orders
- 📊 Multiple scores, attendance records, and library checkouts

### Using Your Own Database

The application automatically adapts to **any SQL Server database**:

1. Connect to your database via the `.env` file or sidebar configuration
2. The app retrieves the schema automatically using `INFORMATION_SCHEMA`
3. Table names and structure are detected dynamically
4. The interface updates to show your actual database content
5. Ask questions about your data in natural language

**No code changes required!** The app is database-agnostic and works with any properly structured SQL Server database.

---

## 🎨 Dynamic Features

### Automatic Database Adaptation

The application **automatically adapts** to any SQL Server database:

**Dynamic Title:**
- Shows your actual database name
- Format: `🏫 {Your_Database_Name} Chatbot (Azure OpenAI)`

**Dynamic Description:**
- Lists all tables from your database
- Converts table names to friendly format
- Example: "Ask me questions about customers, orders, products, or inventory."

**Dynamic Welcome Message:**
- Greets users with context about available data
- Example: "Hello! I'm your database assistant. Ask me about employees, departments, projects, and timesheets."

**Dynamic Schema Detection:**
- Retrieves all tables and columns automatically
- Detects primary keys and foreign key relationships
- Caches schema for 1 hour (configurable)
- Manual refresh available via sidebar button

### How It Works

1. **On Startup:** App connects to your database and queries `INFORMATION_SCHEMA`
2. **Schema Parsing:** Extracts table names, column definitions, data types, and relationships
3. **UI Generation:** Creates dynamic title, description, and welcome message
4. **AI Context:** Provides complete schema to Azure OpenAI for accurate SQL generation
5. **Caching:** Stores schema for 1 hour to optimize performance

See `DYNAMIC_INTERFACE.md` for detailed technical documentation.

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to database"

**Solution:**
- ✅ Verify SQL Server is running
- ✅ Check `DB_SERVER`, `DB_USERNAME`, `DB_PASSWORD` in `.env`
- ✅ Ensure SQL Server allows SQL authentication
- ✅ Test connection using SSMS

### Problem: "Azure OpenAI API error"

**Solution:**
- ✅ Verify `AZURE_OPENAI_API_KEY` is correct
- ✅ Check endpoint URL is accessible
- ✅ Ensure you have API quota available
- ✅ Verify deployment name is correct (`gpt-4o`)

### Problem: "Incorrect syntax near 'LIMIT'"

**Solution:**
- ✅ This should be automatically fixed by `fix_sql_syntax()`
- ✅ If persists, update the `SYSTEM_PROMPT` to emphasize SQL Server syntax
- ✅ Manually check the generated query

### Problem: "Object of type Decimal is not JSON serializable"

**Solution:**
- ✅ This is fixed in `query_db()` function
- ✅ Ensure you're using the latest version of `app.py`
- ✅ Decimal values are automatically converted to float

### Problem: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
```
- ✅ Ensure you're in the correct directory
- ✅ Check Python version (3.8+)

### Problem: Slow responses

**Solution:**
- ✅ Azure OpenAI might be rate-limited
- ✅ Check your internet connection
- ✅ Verify API endpoint is responsive
- ✅ Consider reducing temperature parameter

---

## ⚙️ Configuration Options

### Azure OpenAI Settings (config.py)

```python
AZURE_OPENAI_API_KEY       # Your API key
AZURE_OPENAI_ENDPOINT      # API endpoint URL
AZURE_OPENAI_API_VERSION   # API version
AZURE_OPENAI_DEPLOYMENT    # Model deployment name
```

### Database Settings (config.py)

```python
DB_SERVER                  # SQL Server hostname/IP
DB_NAME                    # Database name (e.g., SchoolDB, InventoryDB, etc.)
DB_USERNAME                # SQL Server username
DB_PASSWORD                # SQL Server password
DB_DRIVER                  # ODBC driver name
```

**Note:** You can also change these settings via the sidebar in real-time without editing files.

### AI Behavior (app.py)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `temperature` | 0 | SQL generation (deterministic) |
| `temperature` | 0.7 | Summaries (creative) |
| `SYSTEM_PROMPT` | Dynamic | Instructions for AI behavior (adapts to your data) |
| `DATABASE_SCHEMA` | Auto-retrieved | Schema information retrieved from database |
| `ttl` | 3600 | Schema cache duration (1 hour) |

---

## 🔒 Security Considerations

### Important Security Notes

1. ⚠️ **NEVER** commit `.env` file to version control
2. 🔐 Use strong passwords for database access
3. 🛡️ Restrict database user permissions (SELECT only recommended)
4. 🔑 Keep Azure OpenAI API key confidential
5. 📦 Use environment variables for all sensitive data
6. ⏱️ Consider implementing rate limiting for production use
7. ✅ Validate and sanitize all user inputs
8. 🔒 Use parameterized queries (already implemented)

### Best Practices

- 🔄 Regularly rotate API keys
- 🎯 Use separate credentials for development/production
- 📊 Monitor API usage and costs
- 📝 Implement logging for audit trails
- 💾 Regular database backups
- ⬆️ Keep dependencies updated

---

## 🚀 Extending the Application

### Already Implemented

- ✅ **Dynamic Interface** - Automatically adapts to any database
- ✅ **Real-time Configuration** - Change settings without restart
- ✅ **Schema Caching** - Optimized performance
- ✅ **Chat History** - Persistent conversation in session
- ✅ **SQL Syntax Correction** - Automatic SQL Server compatibility

### Optional Future Enhancements

#### 1. 🌐 Production Deployment
- Deploy to Azure App Service, AWS, or other cloud platforms
- Add authentication and user management
- Implement multi-tenant support

#### 2. 📝 Enhanced Features
- Export query results to CSV/Excel
- Save favorite queries
- Query history across sessions
- Scheduled reports
- Add query analytics

#### 3. 📤 Export Functionality
- Export results to CSV
- Generate PDF reports
- Excel integration

#### 4. 📊 Visualization
- Add charts for grades
- Attendance graphs
- Performance dashboards

#### 5. 🔐 Authentication
- User login system
- Role-based access control
- Student/Teacher/Admin roles

#### 6. 🎯 Advanced Features
- Voice input (speech-to-text)
- Multi-language support
- Email notifications
- Scheduled reports

### Adding New Tables

1. Create table in SQL Server
2. Update `DATABASE_SCHEMA` in `app.py`
3. Add example queries to `SYSTEM_PROMPT`
4. Test with various questions

### Modifying AI Behavior

Edit `SYSTEM_PROMPT` in `app.py` to:
- Add new query patterns
- Change response style
- Add domain-specific rules
- Improve query accuracy

---

## 📊 Sample Queries

### Query: "How many students are studying at school?"

**Generated SQL:**
```sql
SELECT COUNT(*) AS TotalStudents 
FROM Students 
WHERE IsActive = 1;
```
**Result:** 8 students

---

### Query: "Who is the best student?"

**Generated SQL:**
```sql
SELECT TOP 1 
    s.FirstName + ' ' + s.LastName AS StudentName, 
    AVG(sc.Score) AS AverageScore 
FROM Scores sc 
JOIN Students s ON sc.StudentID = s.StudentID 
WHERE s.IsActive = 1 
GROUP BY s.StudentID, s.FirstName, s.LastName 
ORDER BY AverageScore DESC;
```
**Result:** Emily Johnson with average score 93.17

---

### Query: "What books has John Adams checked out?"

**Generated SQL:**
```sql
SELECT b.Title, b.Author, lc.CheckoutDate, lc.Status 
FROM LibraryCheckouts lc 
JOIN Books b ON lc.BookID = b.BookID 
JOIN Students s ON lc.StudentID = s.StudentID 
WHERE s.FirstName = 'John' AND s.LastName = 'Adams';
```
**Result:** 3 books (To Kill a Mockingbird, The Hunger Games, Harry Potter)

---

### Query: "List all teachers in Mathematics department"

**Generated SQL:**
```sql
SELECT FirstName + ' ' + LastName AS TeacherName, Email, HireDate 
FROM Teachers 
WHERE Department = 'Mathematics' AND IsActive = 1;
```
**Result:** Robert Thompson

---

## ❓ FAQ

### Q: Can I use a different database (MySQL, PostgreSQL)?

**A:** Yes, but you'll need to modify the connection string and SQL syntax in `query_db()` and `fix_sql_syntax()` functions.

### Q: Can I use regular OpenAI instead of Azure OpenAI?

**A:** Yes, change the import to `from openai import OpenAI` and update the client initialization in `app.py`.

### Q: How much does it cost to run?

**A:** Costs depend on Azure OpenAI usage. Each query makes 2 API calls (one for SQL generation, one for summary). Monitor your usage.

### Q: Can multiple users use this simultaneously?

**A:** The current version is single-user. For multi-user, implement a web server with session management.

### Q: How accurate are the SQL queries?

**A:** Accuracy depends on question clarity and AI training. The system includes examples and schema information to improve accuracy.

### Q: Can I add more sample data?

**A:** Yes, add INSERT statements to `school_db.sql` or use SSMS to manually insert data.

### Q: Is this production-ready?

**A:** This is a solid foundation but consider adding:
- Authentication
- Rate limiting
- Comprehensive logging
- Error monitoring
- Load balancing (for web version)

### Q: Can I modify the database schema?

**A:** Yes, but update `DATABASE_SCHEMA` in `app.py` to match your changes.

---

## 📚 Support & Resources

### Documentation

- [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [pyodbc](https://github.com/mkleehammer/pyodbc)
- [SQL Server](https://docs.microsoft.com/en-us/sql/)
- [Streamlit](https://docs.streamlit.io/)

### Common Resources

- [Python Documentation](https://docs.python.org/3/)
- [SQL Server Management Studio](https://docs.microsoft.com/en-us/sql/ssms/)
- [ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/)

### Getting Help

For issues with:
- **Azure OpenAI:** Check Azure portal and documentation
- **SQL Server:** Verify connection and permissions
- **Python:** Check error messages and stack traces

---

## 📝 Version History

### Version 1.0.0 (Current)

- ✅ Initial release
- ✅ Azure OpenAI integration
- ✅ SQL Server database support
- ✅ Natural language query processing
- ✅ Automatic SQL syntax correction
- ✅ Decimal type handling
- ✅ Conversational responses
- ✅ Error handling and recovery
- ✅ Streamlit web interface

---

## 📜 Credits & License

This project demonstrates integration of:
- **Azure OpenAI API** for natural language processing
- **SQL Server** for data storage
- **Python** for application logic
- **Streamlit** for web interface

Feel free to modify and extend this application for your needs.

---

<div align="center">

**Made with ❤️ using Azure OpenAI and Python**

For questions or issues, please review the [Troubleshooting](#troubleshooting) section above.

</div>
