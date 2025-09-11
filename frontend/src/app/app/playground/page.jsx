'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Square, 
  Save, 
  Share2, 
  Download, 
  Upload, 
  Settings,
  Code,
  Eye,
  Split,
  Maximize2,
  FileText
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CodeEditor from '@/components/playground/CodeEditor';
import PreviewPanel from '@/components/playground/PreviewPanel';
import ConsolePanel from '@/components/playground/ConsolePanel';
import TemplatesLibrary from '@/components/playground/TemplatesLibrary';
import { usePlaygroundStore } from '@/hooks/usePlaygroundStore';

const PlaygroundPage = () => {
  const {
    code,
    language,
    theme,
    isRunning,
    output,
    selectedTemplate,
    setCode,
    setLanguage,
    setTheme,
    runCode,
    stopCode,
    saveCode,
    loadTemplate,
    shareCode
  } = usePlaygroundStore();

  const [viewMode, setViewMode] = useState('split'); // 'editor', 'preview', 'split'
  const [activeTab, setActiveTab] = useState('console');
  const [showTemplates, setShowTemplates] = useState(false);

  const editorRef = useRef(null);

  const languages = [
    { value: 'javascript', label: 'JavaScript', icon: '🟨' },
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'html', label: 'HTML', icon: '🌐' },
    { value: 'css', label: 'CSS', icon: '🎨' },
    { value: 'typescript', label: 'TypeScript', icon: '🔷' },
    { value: 'java', label: 'Java', icon: '☕' },
    { value: 'cpp', label: 'C++', icon: '⚡' },
    { value: 'json', label: 'JSON', icon: '📄' },
    { value: 'sql', label: 'SQL', icon: '🗄️' }
  ];

  const templates = [
    {
      id: 'hello-js',
      name: 'Hello World (JavaScript)',
      language: 'javascript',
      code: `console.log("Hello, World!");

// Welcome to the Gradvy Playground!
// Try writing some JavaScript code and click Run to see the output.

function greet(name) {
    return \`Hello, \${name}! Ready to learn?\`;
}

console.log(greet("Learner"));`
    },
    {
      id: 'hello-python',
      name: 'Hello World (Python)',
      language: 'python',
      code: `print("Hello, World!")

# Welcome to the Gradvy Playground!
# Try writing some Python code and click Run to see the output.

def greet(name):
    return f"Hello, {name}! Ready to learn?"

print(greet("Learner"))`
    },
    {
      id: 'basic-html',
      name: 'Basic HTML Template',
      language: 'html',
      code: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gradvy Playground</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Welcome to Gradvy Playground!</h1>
        <p>This is your space to experiment, learn, and create.</p>
        <button onclick="alert('Hello from JavaScript!')">Click me!</button>
    </div>
</body>
</html>`
    },
    {
      id: 'react-component',
      name: 'React Component',
      language: 'javascript',
      code: `// React Component Example
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h2>Counter: {count}</h2>
            <button 
                onClick={() => setCount(count + 1)}
                style={{ 
                    padding: '10px 20px', 
                    margin: '5px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px'
                }}
            >
                Increment
            </button>
            <button 
                onClick={() => setCount(count - 1)}
                style={{ 
                    padding: '10px 20px', 
                    margin: '5px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px'
                }}
            >
                Decrement
            </button>
        </div>
    );
}

// Render the component
ReactDOM.render(<Counter />, document.getElementById('root'));`
    },
    {
      id: 'vue-component',
      name: 'Vue.js Component',
      language: 'javascript',
      code: `// Vue.js Component Example
const { createApp } = Vue;

createApp({
  data() {
    return {
      count: 0,
      message: 'Hello Vue.js!'
    }
  },
  methods: {
    increment() {
      this.count++
    },
    decrement() {
      this.count--
    }
  },
  template: \`
    <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
      <h2>{{ message }}</h2>
      <p style="font-size: 24px; margin: 20px;">Count: {{ count }}</p>
      <button 
        @click="increment"
        style="padding: 10px 20px; margin: 5px; background: #42b883; color: white; border: none; border-radius: 5px; cursor: pointer;"
      >
        Increment
      </button>
      <button 
        @click="decrement"
        style="padding: 10px 20px; margin: 5px; background: #35495e; color: white; border: none; border-radius: 5px; cursor: pointer;"
      >
        Decrement
      </button>
    </div>
  \`
}).mount('#app')`
    },
    {
      id: 'python-ml',
      name: 'Python Machine Learning',
      language: 'python',
      code: `# Python Machine Learning Example
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Generate sample data
np.random.seed(42)
X = np.random.rand(100, 1) * 10
y = 2.5 * X.ravel() + np.random.rand(100) * 3

print("🤖 Machine Learning with Python")
print("================================")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
score = model.score(X_test, y_test)

print(f"Model Coefficient: {model.coef_[0]:.2f}")
print(f"Model Intercept: {model.intercept_:.2f}")
print(f"R² Score: {score:.3f}")

# Sample prediction
sample_input = [[5.0]]
prediction = model.predict(sample_input)
print(f"Prediction for input 5.0: {prediction[0]:.2f}")

print("\\n✅ Machine learning model trained successfully!")`
    },
    {
      id: 'typescript-class',
      name: 'TypeScript Classes',
      language: 'typescript',
      code: `// TypeScript Classes and Interfaces Example

interface User {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
}

interface UserRepository {
  findById(id: number): User | undefined;
  findAll(): User[];
  create(userData: Omit<User, 'id'>): User;
  update(id: number, updates: Partial<User>): User | undefined;
}

class InMemoryUserRepository implements UserRepository {
  private users: User[] = [];
  private nextId: number = 1;

  findById(id: number): User | undefined {
    return this.users.find(user => user.id === id);
  }

  findAll(): User[] {
    return [...this.users];
  }

  create(userData: Omit<User, 'id'>): User {
    const newUser: User = {
      id: this.nextId++,
      ...userData
    };
    this.users.push(newUser);
    return newUser;
  }

  update(id: number, updates: Partial<User>): User | undefined {
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) return undefined;
    
    this.users[userIndex] = { ...this.users[userIndex], ...updates };
    return this.users[userIndex];
  }
}

// Usage Example
const userRepo = new InMemoryUserRepository();

const user1 = userRepo.create({
  name: "Alice Johnson",
  email: "alice@example.com",
  isActive: true
});

const user2 = userRepo.create({
  name: "Bob Smith", 
  email: "bob@example.com",
  isActive: false
});

console.log("All Users:", userRepo.findAll());
console.log("User 1:", userRepo.findById(1));

userRepo.update(2, { isActive: true });
console.log("Updated User 2:", userRepo.findById(2));`
    },
    {
      id: 'java-oop',
      name: 'Java OOP Example',
      language: 'java',
      code: `// Java Object-Oriented Programming Example

public class BankAccount {
    private String accountNumber;
    private String accountHolder;
    private double balance;
    private static int totalAccounts = 0;
    
    // Constructor
    public BankAccount(String accountNumber, String accountHolder, double initialBalance) {
        this.accountNumber = accountNumber;
        this.accountHolder = accountHolder;
        this.balance = initialBalance;
        totalAccounts++;
    }
    
    // Deposit method
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println("Deposited $" + amount + ". New balance: $" + balance);
        } else {
            System.out.println("Invalid deposit amount");
        }
    }
    
    // Withdraw method
    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            System.out.println("Withdrawn $" + amount + ". New balance: $" + balance);
            return true;
        } else {
            System.out.println("Invalid withdrawal amount or insufficient funds");
            return false;
        }
    }
    
    // Getters
    public double getBalance() {
        return balance;
    }
    
    public String getAccountInfo() {
        return "Account: " + accountNumber + ", Holder: " + accountHolder + ", Balance: $" + balance;
    }
    
    public static int getTotalAccounts() {
        return totalAccounts;
    }
}

// Usage Example
class Main {
    public static void main(String[] args) {
        BankAccount account1 = new BankAccount("ACC001", "John Doe", 1000.0);
        BankAccount account2 = new BankAccount("ACC002", "Jane Smith", 500.0);
        
        System.out.println("=== Bank Account Demo ===");
        System.out.println(account1.getAccountInfo());
        
        account1.deposit(250.0);
        account1.withdraw(100.0);
        account1.withdraw(2000.0); // This should fail
        
        System.out.println("Final: " + account1.getAccountInfo());
        System.out.println("Total accounts created: " + BankAccount.getTotalAccounts());
    }
}`
    },
    {
      id: 'cpp-algorithms',
      name: 'C++ Algorithms',
      language: 'cpp',
      code: `// C++ Data Structures and Algorithms Example
#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>

class SortingAlgorithms {
public:
    // Bubble Sort Implementation
    static void bubbleSort(std::vector<int>& arr) {
        int n = arr.size();
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    std::swap(arr[j], arr[j + 1]);
                }
            }
        }
    }
    
    // Quick Sort Implementation
    static void quickSort(std::vector<int>& arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high);
            quickSort(arr, low, pi - 1);
            quickSort(arr, pi + 1, high);
        }
    }
    
private:
    static int partition(std::vector<int>& arr, int low, int high) {
        int pivot = arr[high];
        int i = (low - 1);
        
        for (int j = low; j <= high - 1; j++) {
            if (arr[j] < pivot) {
                i++;
                std::swap(arr[i], arr[j]);
            }
        }
        std::swap(arr[i + 1], arr[high]);
        return (i + 1);
    }
};

// Utility function to print array
void printArray(const std::vector<int>& arr, const std::string& label) {
    std::cout << label << ": ";
    for (int num : arr) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
}

int main() {
    std::vector<int> data = {64, 34, 25, 12, 22, 11, 90, 5};
    std::vector<int> bubbleData = data;
    std::vector<int> quickData = data;
    
    std::cout << "=== C++ Sorting Algorithms Demo ===" << std::endl;
    printArray(data, "Original array");
    
    // Bubble Sort with timing
    auto start = std::chrono::high_resolution_clock::now();
    SortingAlgorithms::bubbleSort(bubbleData);
    auto end = std::chrono::high_resolution_clock::now();
    auto bubbleTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    printArray(bubbleData, "Bubble sorted");
    std::cout << "Bubble sort time: " << bubbleTime.count() << " microseconds" << std::endl;
    
    // Quick Sort with timing
    start = std::chrono::high_resolution_clock::now();
    SortingAlgorithms::quickSort(quickData, 0, quickData.size() - 1);
    end = std::chrono::high_resolution_clock::now();
    auto quickTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    printArray(quickData, "Quick sorted");
    std::cout << "Quick sort time: " << quickTime.count() << " microseconds" << std::endl;
    
    return 0;
}`
    },
    {
      id: 'sql-advanced',
      name: 'Advanced SQL Queries',
      language: 'sql',
      code: `-- Advanced SQL Queries Example
-- Sample database: E-commerce platform

-- Create sample tables (for reference)
/*
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    registration_date DATE,
    city VARCHAR(50)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2)
);
*/

-- 1. Window Functions - Running totals and rankings
SELECT 
    customer_id,
    order_date,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS UNBOUNDED PRECEDING
    ) AS running_total,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id 
        ORDER BY total_amount DESC
    ) AS order_rank
FROM orders
WHERE order_date >= '2024-01-01';

-- 2. Complex JOIN with aggregations
SELECT 
    c.name,
    c.city,
    COUNT(o.order_id) AS total_orders,
    AVG(o.total_amount) AS avg_order_value,
    SUM(o.total_amount) AS total_spent,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.registration_date >= '2023-01-01'
GROUP BY c.customer_id, c.name, c.city
HAVING COUNT(o.order_id) > 0
ORDER BY total_spent DESC;

-- 3. Subqueries and CTEs - Find customers with above-average spending
WITH customer_spending AS (
    SELECT 
        customer_id,
        SUM(total_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
),
average_spending AS (
    SELECT AVG(total_spent) AS avg_spending
    FROM customer_spending
)
SELECT 
    c.name,
    c.email,
    cs.total_spent,
    ROUND(cs.total_spent - avgs.avg_spending, 2) AS above_average
FROM customers c
JOIN customer_spending cs ON c.customer_id = cs.customer_id
CROSS JOIN average_spending avgs
WHERE cs.total_spent > avgs.avg_spending
ORDER BY cs.total_spent DESC;

-- 4. Pivot-like query - Monthly order summary
SELECT 
    EXTRACT(YEAR FROM order_date) AS year,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN total_amount ELSE 0 END) AS jan_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN total_amount ELSE 0 END) AS feb_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN total_amount ELSE 0 END) AS mar_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 4 THEN total_amount ELSE 0 END) AS apr_sales,
    SUM(total_amount) AS total_yearly_sales
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY EXTRACT(YEAR FROM order_date)
ORDER BY year;

-- 5. Advanced filtering - Find loyal customers
SELECT 
    c.name,
    c.email,
    COUNT(o.order_id) AS order_count,
    AVG(o.total_amount) AS avg_order_value,
    DATEDIFF(MAX(o.order_date), MIN(o.order_date)) AS days_as_customer
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
HAVING 
    COUNT(o.order_id) >= 5 
    AND AVG(o.total_amount) > 100
    AND MAX(o.order_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY order_count DESC, avg_order_value DESC;`
    }
  ];

  const handleRunCode = async () => {
    await runCode();
  };

  const handleSaveCode = async () => {
    await saveCode({ name: `playground-${Date.now()}` });
  };

  const handleShareCode = async () => {
    const shareUrl = await shareCode();
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl);
      // Show toast notification
    }
  };

  const getCurrentLanguage = () => {
    return languages.find(lang => lang.value === language) || languages[0];
  };

  return (
    <ProtectedRoute>
      <div className="h-full flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-6"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Code className="h-6 w-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Playground</h1>
            </div>
            <Badge variant="outline" className="flex items-center space-x-1">
              <span>{getCurrentLanguage().icon}</span>
              <span>{getCurrentLanguage().label}</span>
            </Badge>
          </div>

          {/* Toolbar */}
          <div className="flex items-center space-x-2">
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map(lang => (
                  <SelectItem key={lang.value} value={lang.value}>
                    <span className="flex items-center space-x-2">
                      <span>{lang.icon}</span>
                      <span>{lang.label}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
              <Button
                variant={viewMode === 'editor' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('editor')}
              >
                <Code className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'split' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('split')}
              >
                <Split className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'preview' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('preview')}
              >
                <Eye className="h-4 w-4" />
              </Button>
            </div>

            <Button
              onClick={handleRunCode}
              disabled={isRunning}
              className="bg-green-600 hover:bg-green-700"
            >
              {isRunning ? (
                <>
                  <Square className="h-4 w-4 mr-2" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Run
                </>
              )}
            </Button>

            <div className="flex items-center space-x-1">
              <Button variant="outline" size="sm" onClick={handleSaveCode}>
                <Save className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleShareCode}>
                <Share2 className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowTemplates(true)}>
                <FileText className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Editor Section */}
          <div className={`${
            viewMode === 'editor' ? 'lg:col-span-3' : 
            viewMode === 'preview' ? 'hidden lg:block lg:col-span-1' : 
            'lg:col-span-2'
          } space-y-4`}>
            <Card className="h-[500px]">
              <CodeEditor
                ref={editorRef}
                value={code}
                language={language}
                theme={theme}
                onChange={setCode}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  automaticLayout: true,
                }}
              />
            </Card>

            {/* Console/Output */}
            <Card className="h-[200px]">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
                <div className="border-b px-4 py-2">
                  <TabsList>
                    <TabsTrigger value="console">Console</TabsTrigger>
                    <TabsTrigger value="output">Output</TabsTrigger>
                  </TabsList>
                </div>
                <TabsContent value="console" className="h-[calc(100%-60px)] mt-0">
                  <ConsolePanel output={output} />
                </TabsContent>
                <TabsContent value="output" className="h-[calc(100%-60px)] mt-0">
                  <div className="p-4 h-full">
                    <pre className="text-sm text-gray-700 overflow-auto h-full">
                      {output || 'Run your code to see output here...'}
                    </pre>
                  </div>
                </TabsContent>
              </Tabs>
            </Card>
          </div>

          {/* Preview Section */}
          {viewMode !== 'editor' && (
            <div className={`${
              viewMode === 'preview' ? 'lg:col-span-3' : 'lg:col-span-1'
            }`}>
              <Card className="h-[724px]">
                <div className="border-b px-4 py-2 flex items-center justify-between">
                  <h3 className="font-medium">Preview</h3>
                  <Button variant="ghost" size="sm">
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
                <div className="h-[calc(100%-60px)]">
                  <PreviewPanel 
                    code={code} 
                    language={language} 
                    isRunning={isRunning}
                  />
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Templates Modal */}
        {showTemplates && (
          <TemplatesLibrary
            templates={templates}
            onSelect={(template) => {
              loadTemplate(template);
              setShowTemplates(false);
            }}
            onClose={() => setShowTemplates(false)}
          />
        )}
      </div>
    </ProtectedRoute>
  );
};

export default PlaygroundPage;