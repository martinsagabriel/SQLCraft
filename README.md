# SQLCraft 🔄🗣️➡️SQL

A Python CLI tool that converts natural language text into SQL queries using Large Language Models (LLMs).

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features ✨

- **Natural Language to SQL Conversion** - Transform plain English requests into valid SQL queries
- **Schema-Aware Generation** - Context-aware using database schema definitions
- **SQL Validation** - Automatic formatting and basic security checks
- **Cross-Dialect Support** - Generate SQL for PostgreSQL, MySQL, SQLite, etc.

## Installation ⚙️

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- GROQ API key - [Get yours](https://console.groq.com/playground)

## Usage 🚀

### Basic Conversion
```bash
python main.py --prompt prompt.txt --schema schema.txt --question "Show users who joined this year"
```

### Example Output
```sql
SELECT id, product_name, price 
FROM products 
WHERE price > 100 
ORDER BY price DESC;
```

## Configuration ⚙️

1. Create `.env` file:
```ini
GROQ_API_KEY=your_api_key_here
DEFAULT_DB_SCHEMA=schemas/schema.txt
```

2. Schema file format (`schemas/primary.txt`):
```text
Table: employees
Columns:
    employee_id (INTEGER): A unique identifier for each employee.
    name (VARCHAR): The full name of the employee.
    email (VARCHAR): employee's email address
```

## WEB UI 🖥️
```bash	
streamlit run app.py
```

<!-- 
## Advanced Features 🔧

### Execute Directly Against Database
```bash
lingua-sql "Top 5 customers by purchases" --execute --db postgresql://user:pass@localhost/dbname
```

### Use Different LLM Backend
```bash
lingua-sql "Monthly sales report" --model sqlcoder-7b
```

### Generate for Specific SQL Dialect
```bash
lingua-sql "List inactive users" --dialect postgresql15
```

## Security Considerations 🔒

All generated queries undergo:
- Basic SQL injection prevention checks
- Read-only mode (configurable)
- Query whitelisting/blacklisting -->

**Always validate generated queries before production use!**

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

MIT License - See [LICENSE](LICENSE) for details

---