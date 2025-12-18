import json

def handler(request):
    if request.method == 'GET':
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
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
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
        
        <button onclick="generateSQL()" id="generateBtn">Generate SQL</button>
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
            <div class="example-item" onclick="setExample('students', 'Count students with GPA greater than 3.5')">
                🎓 Count students with GPA greater than 3.5
            </div>
        </div>
    </div>
    
    <script>
        function setExample(table, question) {
            const schemas = {
                'employees': 'CREATE TABLE employees (name TEXT, salary REAL, department TEXT)',
                'products': 'CREATE TABLE products (name TEXT, price REAL, category TEXT)',
                'orders': 'CREATE TABLE orders (id REAL, customer TEXT, amount REAL)',
                'students': 'CREATE TABLE students (name TEXT, gpa REAL, major TEXT)'
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
            const btn = document.getElementById('generateBtn');
            
            btn.disabled = true;
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
                btn.disabled = false;
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // Allow Enter key to submit
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                generateSQL();
            }
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }