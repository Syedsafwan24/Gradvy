'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Search, 
  Code, 
  Globe, 
  Palette, 
  Smartphone, 
  Database,
  Zap,
  Star,
  Copy,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

const TemplatesLibrary = ({ templates, onSelect, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All Templates', icon: Code },
    { id: 'javascript', name: 'JavaScript', icon: Zap },
    { id: 'python', name: 'Python', icon: Database },
    { id: 'html', name: 'HTML/CSS', icon: Globe },
    { id: 'react', name: 'React', icon: Smartphone },
    { id: 'beginner', name: 'Beginner', icon: Star }
  ];

  const extendedTemplates = [
    ...templates,
    {
      id: 'todo-app',
      name: 'Todo App (React)',
      category: 'react',
      language: 'javascript',
      difficulty: 'intermediate',
      tags: ['react', 'hooks', 'state'],
      description: 'A simple todo application with add, remove, and toggle functionality',
      code: `import React, { useState } from 'react';

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const addTodo = () => {
    if (inputValue.trim()) {
      setTodos([...todos, {
        id: Date.now(),
        text: inputValue,
        completed: false
      }]);
      setInputValue('');
    }
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const removeTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h1>My Todo App</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add a new todo..."
          style={{
            width: '70%',
            padding: '10px',
            marginRight: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
        <button onClick={addTodo} style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}>
          Add
        </button>
      </div>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {todos.map(todo => (
          <li key={todo.id} style={{
            padding: '10px',
            margin: '5px 0',
            backgroundColor: '#f8f9fa',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span
              onClick={() => toggleTodo(todo.id)}
              style={{
                textDecoration: todo.completed ? 'line-through' : 'none',
                cursor: 'pointer',
                opacity: todo.completed ? 0.6 : 1
              }}
            >
              {todo.text}
            </span>
            <button
              onClick={() => removeTodo(todo.id)}
              style={{
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '5px 10px',
                cursor: 'pointer'
              }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      
      {todos.length === 0 && (
        <p style={{ textAlign: 'center', color: '#666', marginTop: '40px' }}>
          No todos yet. Add one above!
        </p>
      )}
    </div>
  );
}

ReactDOM.render(<TodoApp />, document.getElementById('root'));`
    },
    {
      id: 'calculator',
      name: 'Simple Calculator',
      category: 'javascript',
      language: 'javascript',
      difficulty: 'beginner',
      tags: ['math', 'functions', 'dom'],
      description: 'A basic calculator with arithmetic operations',
      code: `// Simple Calculator
function Calculator() {
    let display = document.getElementById('display');
    
    function clearDisplay() {
        display.value = '0';
    }
    
    function appendToDisplay(value) {
        if (display.value === '0' && value !== '.') {
            display.value = value;
        } else {
            display.value += value;
        }
    }
    
    function calculate() {
        try {
            display.value = eval(display.value);
        } catch (error) {
            display.value = 'Error';
        }
    }
    
    return {
        clear: clearDisplay,
        append: appendToDisplay,
        calculate: calculate
    };
}

// Create calculator interface
document.body.innerHTML = \`
<div style="max-width: 300px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; font-family: Arial, sans-serif;">
    <input type="text" id="display" value="0" readonly style="width: 100%; padding: 10px; font-size: 20px; text-align: right; margin-bottom: 15px;">
    
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
        <button onclick="calc.clear()" style="padding: 15px; font-size: 16px; background: #f0f0f0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">C</button>
        <button onclick="calc.append('/')" style="padding: 15px; font-size: 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">÷</button>
        <button onclick="calc.append('*')" style="padding: 15px; font-size: 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">×</button>
        <button onclick="calc.append('-')" style="padding: 15px; font-size: 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">-</button>
        
        <button onclick="calc.append('7')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">7</button>
        <button onclick="calc.append('8')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">8</button>
        <button onclick="calc.append('9')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">9</button>
        <button onclick="calc.append('+')" style="padding: 15px; font-size: 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; grid-row: span 2;">+</button>
        
        <button onclick="calc.append('4')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">4</button>
        <button onclick="calc.append('5')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">5</button>
        <button onclick="calc.append('6')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">6</button>
        
        <button onclick="calc.append('1')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">1</button>
        <button onclick="calc.append('2')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">2</button>
        <button onclick="calc.append('3')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">3</button>
        <button onclick="calc.calculate()" style="padding: 15px; font-size: 16px; background: #007bff; color: white; border: 1px solid #007bff; border-radius: 5px; cursor: pointer; grid-row: span 2;">=</button>
        
        <button onclick="calc.append('0')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; grid-column: span 2;">0</button>
        <button onclick="calc.append('.')" style="padding: 15px; font-size: 16px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer;">.</button>
    </div>
</div>
\`;

const calc = Calculator();
console.log('Calculator ready! Try performing some calculations.');`
    },
    {
      id: 'data-viz',
      name: 'Data Visualization',
      category: 'javascript',
      language: 'javascript',
      difficulty: 'intermediate',
      tags: ['charts', 'data', 'visualization'],
      description: 'Interactive data visualization with Chart.js',
      code: `// Data Visualization Example
// First, let's create some sample data
const salesData = [
    { month: 'Jan', sales: 4000, profit: 2400 },
    { month: 'Feb', sales: 3000, profit: 1398 },
    { month: 'Mar', sales: 2000, profit: 9800 },
    { month: 'Apr', sales: 2780, profit: 3908 },
    { month: 'May', sales: 1890, profit: 4800 },
    { month: 'Jun', sales: 2390, profit: 3800 }
];

// Create the HTML structure
document.body.innerHTML = \`
<div style="max-width: 1000px; margin: 20px auto; padding: 20px; font-family: Arial, sans-serif;">
    <h1 style="text-align: center; color: #333;">Sales Dashboard</h1>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
        <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #0369a1;">Total Sales</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #0369a1;">$16,060</p>
        </div>
        <div style="background: #f0fdf4; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #15803d;">Total Profit</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #15803d;">$26,104</p>
        </div>
        <div style="background: #fef3c7; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; color: #d97706;">Avg Growth</h3>
            <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #d97706;">+12.5%</p>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0;">Monthly Performance</h3>
            <canvas id="chart" width="400" height="200"></canvas>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0;">Recent Activity</h3>
            <div id="activity-feed"></div>
        </div>
    </div>
</div>
\`;

// Simple chart implementation (without external libraries)
function drawChart() {
    const canvas = document.getElementById('chart');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, width, height);
    
    // Chart settings
    const padding = 50;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // Find max value for scaling
    const maxValue = Math.max(...salesData.map(d => Math.max(d.sales, d.profit)));
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw data
    const barWidth = chartWidth / salesData.length / 2 - 10;
    
    salesData.forEach((data, index) => {
        const x = padding + (index * chartWidth / salesData.length);
        
        // Sales bar
        const salesHeight = (data.sales / maxValue) * chartHeight;
        ctx.fillStyle = '#3b82f6';
        ctx.fillRect(x, height - padding - salesHeight, barWidth, salesHeight);
        
        // Profit bar
        const profitHeight = (data.profit / maxValue) * chartHeight;
        ctx.fillStyle = '#10b981';
        ctx.fillRect(x + barWidth + 5, height - padding - profitHeight, barWidth, profitHeight);
        
        // Month labels
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(data.month, x + barWidth, height - padding + 20);
    });
    
    // Legend
    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(width - 150, 20, 15, 15);
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('Sales', width - 130, 32);
    
    ctx.fillStyle = '#10b981';
    ctx.fillRect(width - 150, 40, 15, 15);
    ctx.fillStyle = '#333';
    ctx.fillText('Profit', width - 130, 52);
}

// Activity feed
function updateActivityFeed() {
    const activities = [
        'New order received - $2,400',
        'Customer feedback: 5 stars',
        'Inventory restocked',
        'Marketing campaign launched',
        'Monthly report generated'
    ];
    
    const feed = document.getElementById('activity-feed');
    feed.innerHTML = activities.map((activity, index) => \`
        <div style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; border-left: 3px solid \${index % 2 === 0 ? '#3b82f6' : '#10b981'};">
            <p style="margin: 0; font-size: 14px;">\${activity}</p>
            <small style="color: #666;">\${Math.floor(Math.random() * 24)} hours ago</small>
        </div>
    \`).join('');
}

// Initialize dashboard
drawChart();
updateActivityFeed();

console.log('Data visualization dashboard created!');
console.log('Sales data:', salesData);`
    },
    {
      id: 'password-generator',
      name: 'Password Generator',
      category: 'javascript',
      language: 'javascript',
      difficulty: 'beginner',
      tags: ['security', 'random', 'utility'],
      description: 'Generate secure passwords with customizable options',
      code: `// Password Generator
class PasswordGenerator {
    constructor() {
        this.lowercase = 'abcdefghijklmnopqrstuvwxyz';
        this.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        this.numbers = '0123456789';
        this.symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    }
    
    generate(options = {}) {
        const {
            length = 12,
            includeLowercase = true,
            includeUppercase = true,
            includeNumbers = true,
            includeSymbols = true,
            excludeSimilar = false
        } = options;
        
        let chars = '';
        
        if (includeLowercase) chars += this.lowercase;
        if (includeUppercase) chars += this.uppercase;
        if (includeNumbers) chars += this.numbers;
        if (includeSymbols) chars += this.symbols;
        
        if (excludeSimilar) {
            chars = chars.replace(/[il1Lo0O]/g, '');
        }
        
        if (chars === '') {
            throw new Error('At least one character type must be selected');
        }
        
        let password = '';
        for (let i = 0; i < length; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        return password;
    }
    
    checkStrength(password) {
        let score = 0;
        let feedback = [];
        
        if (password.length >= 8) score += 2;
        else feedback.push('Use at least 8 characters');
        
        if (password.length >= 12) score += 1;
        
        if (/[a-z]/.test(password)) score += 1;
        else feedback.push('Include lowercase letters');
        
        if (/[A-Z]/.test(password)) score += 1;
        else feedback.push('Include uppercase letters');
        
        if (/[0-9]/.test(password)) score += 1;
        else feedback.push('Include numbers');
        
        if (/[^\\w\\s]/.test(password)) score += 2;
        else feedback.push('Include special characters');
        
        const strength = score < 3 ? 'Weak' : score < 5 ? 'Medium' : score < 7 ? 'Strong' : 'Very Strong';
        
        return { score, strength, feedback };
    }
}

// Create the UI
document.body.innerHTML = \`
<div style="max-width: 500px; margin: 50px auto; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); font-family: Arial, sans-serif; background: white;">
    <h1 style="text-align: center; color: #333; margin-bottom: 30px;">🔐 Password Generator</h1>
    
    <div style="margin-bottom: 20px;">
        <label style="display: block; margin-bottom: 10px; color: #555;">Password Length: <span id="lengthValue">12</span></label>
        <input type="range" id="lengthSlider" min="4" max="50" value="12" style="width: 100%;">
    </div>
    
    <div style="margin-bottom: 20px;">
        <label style="display: flex; align-items: center; margin-bottom: 10px; color: #555; cursor: pointer;">
            <input type="checkbox" id="lowercase" checked style="margin-right: 10px;"> Include Lowercase (a-z)
        </label>
        <label style="display: flex; align-items: center; margin-bottom: 10px; color: #555; cursor: pointer;">
            <input type="checkbox" id="uppercase" checked style="margin-right: 10px;"> Include Uppercase (A-Z)
        </label>
        <label style="display: flex; align-items: center; margin-bottom: 10px; color: #555; cursor: pointer;">
            <input type="checkbox" id="numbers" checked style="margin-right: 10px;"> Include Numbers (0-9)
        </label>
        <label style="display: flex; align-items: center; margin-bottom: 10px; color: #555; cursor: pointer;">
            <input type="checkbox" id="symbols" checked style="margin-right: 10px;"> Include Symbols (!@#$...)
        </label>
        <label style="display: flex; align-items: center; margin-bottom: 20px; color: #555; cursor: pointer;">
            <input type="checkbox" id="excludeSimilar" style="margin-right: 10px;"> Exclude Similar Characters (i, l, 1, L, o, 0, O)
        </label>
    </div>
    
    <button onclick="generatePassword()" style="width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-bottom: 20px;">
        Generate Password
    </button>
    
    <div style="position: relative; margin-bottom: 20px;">
        <input type="text" id="passwordOutput" readonly style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-family: monospace; font-size: 14px; background: #f8f9fa;">
        <button onclick="copyPassword()" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
            Copy
        </button>
    </div>
    
    <div id="strengthIndicator" style="margin-bottom: 20px;"></div>
    
    <div id="feedback" style="font-size: 12px; color: #666;"></div>
</div>
\`;

const generator = new PasswordGenerator();

function updateLengthDisplay() {
    const slider = document.getElementById('lengthSlider');
    const display = document.getElementById('lengthValue');
    display.textContent = slider.value;
}

function generatePassword() {
    const options = {
        length: parseInt(document.getElementById('lengthSlider').value),
        includeLowercase: document.getElementById('lowercase').checked,
        includeUppercase: document.getElementById('uppercase').checked,
        includeNumbers: document.getElementById('numbers').checked,
        includeSymbols: document.getElementById('symbols').checked,
        excludeSimilar: document.getElementById('excludeSimilar').checked
    };
    
    try {
        const password = generator.generate(options);
        document.getElementById('passwordOutput').value = password;
        
        const strength = generator.checkStrength(password);
        updateStrengthIndicator(strength);
        
    } catch (error) {
        alert(error.message);
    }
}

function updateStrengthIndicator(strength) {
    const indicator = document.getElementById('strengthIndicator');
    const feedback = document.getElementById('feedback');
    
    const colors = {
        'Weak': '#dc3545',
        'Medium': '#ffc107',
        'Strong': '#28a745',
        'Very Strong': '#17a2b8'
    };
    
    const color = colors[strength.strength];
    const percentage = (strength.score / 8) * 100;
    
    indicator.innerHTML = \`
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Password Strength: <strong style="color: \${color};">\${strength.strength}</strong></span>
            <span>\${strength.score}/8</span>
        </div>
        <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="width: \${percentage}%; height: 100%; background: \${color}; transition: width 0.3s ease;"></div>
        </div>
    \`;
    
    feedback.innerHTML = strength.feedback.length > 0 
        ? 'Suggestions: ' + strength.feedback.join(', ')
        : 'Great! This is a strong password.';
}

function copyPassword() {
    const passwordField = document.getElementById('passwordOutput');
    passwordField.select();
    document.execCommand('copy');
    
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.style.background = '#28a745';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '#28a745';
    }, 2000);
}

// Event listeners
document.getElementById('lengthSlider').addEventListener('input', updateLengthDisplay);
document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', generatePassword);
});

// Generate initial password
generatePassword();
console.log('Password Generator ready! 🔐');`
    }
  ];

  const filteredTemplates = extendedTemplates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          template.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || 
                           template.category === selectedCategory ||
                           template.language === selectedCategory ||
                           (selectedCategory === 'beginner' && template.difficulty === 'beginner');
    
    return matchesSearch && matchesCategory;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'advanced': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getLanguageIcon = (language) => {
    switch (language) {
      case 'javascript': return '🟨';
      case 'python': return '🐍';
      case 'html': return '🌐';
      case 'css': return '🎨';
      default: return '📄';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Code Templates</h2>
              <p className="text-gray-600 mt-1">Choose a template to get started quickly</p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Search and Categories */}
          <div className="p-6 border-b bg-gray-50">
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {categories.map(category => {
                const Icon = category.icon;
                return (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory(category.id)}
                    className="flex items-center space-x-1"
                  >
                    <Icon className="h-3 w-3" />
                    <span>{category.name}</span>
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Templates Grid */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {filteredTemplates.length === 0 ? (
              <div className="text-center py-12">
                <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
                <p className="text-gray-600">Try adjusting your search or category filter.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredTemplates.map(template => (
                  <Card key={template.id} className="p-4 hover:shadow-lg transition-shadow cursor-pointer group">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-xl">{getLanguageIcon(template.language)}</span>
                        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">
                          {template.name}
                        </h3>
                      </div>
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigator.clipboard.writeText(template.code);
                          }}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {template.description}
                    </p>

                    <div className="flex flex-wrap gap-1 mb-3">
                      <Badge className={getDifficultyColor(template.difficulty)}>
                        {template.difficulty}
                      </Badge>
                      {template.tags?.slice(0, 2).map(tag => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-xs">
                        {template.language}
                      </Badge>
                      <Button
                        size="sm"
                        onClick={() => onSelect(template)}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        Use Template
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default TemplatesLibrary;