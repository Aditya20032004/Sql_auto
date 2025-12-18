from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve HTML interface
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>English to SQL Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
            font-family: inherit;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .sql-output {
            background: #282c34;
            color: #61dafb;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin-top: 10px;
            word-break: break-all;
        }
        .examples {
            margin-top: 30px;
            padding: 20px;
            background: #f0f0f0;
            border-radius: 8px;
        }
        .example-item {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-item:hover {
            background: #e0e0e0;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ English to SQL</h1>
        <p class="subtitle">Convert natural language questions to SQL queries</p>
        
        <div class="input-group">
            <label for="schema">Database Schema (optional)</label>
            <input type="text" id="schema" placeholder="e.g., CREATE TABLE employees (name TEXT, salary REAL, department TEXT)">
        </div>
        
        <div class="input-group">
            <label for="question">Your Question</label>
            <textarea id="question" placeholder="e.g., What are the names of employees earning more than 50000?"></textarea>
        </div>
        
        <button onclick="generateSQL()">Generate SQL</button>
        <div class="loading" id="loading">⏳ Generating SQL...</div>
        
        <div class="result" id="result">
            <h3>Generated SQL:</h3>
            <div class="sql-output" id="sql-output"></div>
        </div>
        
        <div class="examples">
            <h3>Example Questions:</h3>
            <div class="example-item" onclick="setExample('employees', 'What are the names of all employees?')">
                📊 What are the names of all employees?
            </div>
            <div class="example-item" onclick="setExample('products', 'Which products cost more than 100?')">
                🛍️ Which products cost more than 100?
            </div>
            <div class="example-item" onclick="setExample('orders', 'What is the total amount of all orders?')">
                💰 What is the total amount of all orders?
            </div>
        </div>
    </div>
    
    <script>
        function setExample(table, question) {
            const schemas = {
                'employees': 'CREATE TABLE employees (name TEXT, salary REAL, department TEXT)',
                'products': 'CREATE TABLE products (name TEXT, price REAL, category TEXT)',
                'orders': 'CREATE TABLE orders (id REAL, customer TEXT, amount REAL)'
            };
            document.getElementById('schema').value = schemas[table] || '';
            document.getElementById('question').value = question;
        }
        
        async function generateSQL() {
            const schema = document.getElementById('schema').value.trim();
            const question = document.getElementById('question').value.trim();
            
            if (!question) {
                alert('Please enter a question!');
                return;
            }
            
            const input = schema ? `${schema} ; Question: ${question}` : question;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').classList.remove('show');
            
            try {
                const response = await fetch('/api/sql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input: input })
                });
                
                const data = await response.json();
                document.getElementById('sql-output').textContent = data.sql || data.error || 'No result';
                document.getElementById('result').classList.add('show');
            } catch (error) {
                document.getElementById('sql-output').textContent = 'Error: ' + error.message;
                document.getElementById('result').classList.add('show');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
        
    def do_POST(self):
        # Handle SQL generation
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            user_input = data.get('input', '')
            
            # Simple rule-based SQL generation (lightweight, no ML required)
            sql = generate_sql_simple(user_input)
            
            response = {'sql': sql}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {'error': str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

def generate_sql_simple(text):
    """Lightweight rule-based SQL generation"""
    text_lower = text.lower()
    
    # Extract table name from CREATE TABLE statement
    table = 'table'
    if 'create table' in text_lower:
        parts = text.split('CREATE TABLE', 1)[-1].split('(')[0].strip()
        table = parts.split()[0].strip()
    
    # Extract question
    if 'question:' in text_lower:
        question = text.split('Question:', 1)[-1].strip().lower()
    else:
        question = text_lower
    
    # Pattern matching for SQL generation
    if any(word in question for word in ['all', 'list', 'show', 'what are']):
        if 'name' in question:
            return f"SELECT name FROM {table}"
        return f"SELECT * FROM {table}"
    
    elif 'count' in question or 'how many' in question:
        return f"SELECT COUNT(*) FROM {table}"
    
    elif 'sum' in question or 'total' in question:
        if 'amount' in question:
            return f"SELECT SUM(amount) FROM {table}"
        if 'salary' in question:
            return f"SELECT SUM(salary) FROM {table}"
        return f"SELECT SUM(*) FROM {table}"
    
    elif 'average' in question or 'avg' in question:
        if 'salary' in question:
            return f"SELECT AVG(salary) FROM {table}"
        if 'price' in question:
            return f"SELECT AVG(price) FROM {table}"
        return f"SELECT AVG(*) FROM {table}"
    
    elif 'more than' in question or 'greater than' in question or '>' in question:
        # Extract number
        import re
        numbers = re.findall(r'\d+', question)
        value = numbers[0] if numbers else '100'
        
        if 'salary' in question:
            return f"SELECT * FROM {table} WHERE salary > {value}"
        if 'price' in question:
            return f"SELECT * FROM {table} WHERE price > {value}"
        if 'amount' in question:
            return f"SELECT * FROM {table} WHERE amount > {value}"
        return f"SELECT * FROM {table} WHERE value > {value}"
    
    elif 'less than' in question or '<' in question:
        import re
        numbers = re.findall(r'\d+', question)
        value = numbers[0] if numbers else '100'
        
        if 'salary' in question:
            return f"SELECT * FROM {table} WHERE salary < {value}"
        if 'price' in question:
            return f"SELECT * FROM {table} WHERE price < {value}"
        return f"SELECT * FROM {table} WHERE value < {value}"
    
    elif 'equal' in question or '=' in question or 'equals' in question:
        # Extract value after equal/equals
        import re
        if "'" in question:
            values = re.findall(r"'([^']*)'", question)
            if values and 'department' in question:
                return f"SELECT * FROM {table} WHERE department = '{values[0]}'"
            if values and 'category' in question:
                return f"SELECT * FROM {table} WHERE category = '{values[0]}'"
        return f"SELECT * FROM {table} WHERE column = 'value'"
    
    elif 'group by' in question:
        if 'department' in question:
            return f"SELECT department, COUNT(*) FROM {table} GROUP BY department"
        if 'category' in question:
            return f"SELECT category, COUNT(*) FROM {table} GROUP BY category"
        return f"SELECT column, COUNT(*) FROM {table} GROUP BY column"
    
    elif 'order by' in question or 'sort' in question:
        if 'desc' in question or 'highest' in question or 'largest' in question:
            return f"SELECT * FROM {table} ORDER BY column DESC"
        return f"SELECT * FROM {table} ORDER BY column ASC"
    
    else:
        # Default: select all
        return f"SELECT * FROM {table}"
