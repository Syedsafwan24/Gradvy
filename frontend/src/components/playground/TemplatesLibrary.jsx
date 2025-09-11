// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/playground/TemplatesLibrary.jsx
// Refactored templates library component with modular architecture
// Split from massive 740-line component into focused sub-components
// RELEVANT FILES: TemplateGrid.jsx, TemplateCard.jsx, TemplateFilters.jsx, PlaygroundTemplates.js

'use client';

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { defaultTemplates } from '@/app/app/playground/data/PlaygroundTemplates';
import TemplateFilters from './templates/TemplateFilters';
import TemplateGrid from './templates/TemplateGrid';

const TemplatesLibrary = ({ onSelectTemplate, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Extended templates with additional examples
  const extendedTemplates = useMemo(() => [
    ...defaultTemplates,
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
      setTodos([...todos, { id: Date.now(), text: inputValue, completed: false }]);
      setInputValue('');
    }
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h1>Todo App</h1>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Add a new todo..."
          style={{ padding: '10px', marginRight: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button onClick={addTodo} style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
          Add
        </button>
      </div>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {todos.map(todo => (
          <li key={todo.id} style={{ 
            padding: '10px', 
            marginBottom: '10px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span 
              style={{ 
                textDecoration: todo.completed ? 'line-through' : 'none',
                cursor: 'pointer'
              }}
              onClick={() => toggleTodo(todo.id)}
            >
              {todo.text}
            </span>
            <button 
              onClick={() => deleteTodo(todo.id)}
              style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px' }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TodoApp;`
    },
    {
      id: 'calculator',
      name: 'Calculator App',
      category: 'javascript',
      language: 'javascript',
      difficulty: 'beginner',
      tags: ['calculator', 'math', 'ui'],
      description: 'A simple calculator with basic arithmetic operations',
      code: `// Simple Calculator
class Calculator {
  constructor() {
    this.display = document.getElementById('display');
    this.currentValue = '0';
    this.previousValue = null;
    this.operator = null;
    this.waitingForNewValue = false;
  }

  updateDisplay() {
    this.display.textContent = this.currentValue;
  }

  inputNumber(number) {
    if (this.waitingForNewValue) {
      this.currentValue = number;
      this.waitingForNewValue = false;
    } else {
      this.currentValue = this.currentValue === '0' ? number : this.currentValue + number;
    }
    this.updateDisplay();
  }

  inputOperator(nextOperator) {
    const inputValue = parseFloat(this.currentValue);

    if (this.previousValue === null) {
      this.previousValue = inputValue;
    } else if (this.operator) {
      const currentValue = this.previousValue || 0;
      const newValue = this.calculate(currentValue, inputValue, this.operator);

      this.currentValue = String(newValue);
      this.previousValue = newValue;
      this.updateDisplay();
    }

    this.waitingForNewValue = true;
    this.operator = nextOperator;
  }

  calculate(firstValue, secondValue, operator) {
    switch (operator) {
      case '+': return firstValue + secondValue;
      case '-': return firstValue - secondValue;
      case '*': return firstValue * secondValue;
      case '/': return firstValue / secondValue;
      case '=': return secondValue;
      default: return secondValue;
    }
  }

  clear() {
    this.currentValue = '0';
    this.previousValue = null;
    this.operator = null;
    this.waitingForNewValue = false;
    this.updateDisplay();
  }
}

// Initialize calculator
const calc = new Calculator();

// HTML Structure (add this to your HTML)
console.log('Add this HTML to see the calculator:');
console.log(\`
<div style="width: 300px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
  <div id="display" style="font-size: 2em; text-align: right; padding: 10px; background: #f0f0f0; margin-bottom: 10px;">0</div>
  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px;">
    <button onclick="calc.clear()" style="grid-column: span 2; padding: 15px;">Clear</button>
    <button onclick="calc.inputOperator('/')" style="padding: 15px;">÷</button>
    <button onclick="calc.inputOperator('*')" style="padding: 15px;">×</button>
    <button onclick="calc.inputNumber('7')" style="padding: 15px;">7</button>
    <button onclick="calc.inputNumber('8')" style="padding: 15px;">8</button>
    <button onclick="calc.inputNumber('9')" style="padding: 15px;">9</button>
    <button onclick="calc.inputOperator('-')" style="padding: 15px;">-</button>
    <button onclick="calc.inputNumber('4')" style="padding: 15px;">4</button>
    <button onclick="calc.inputNumber('5')" style="padding: 15px;">5</button>
    <button onclick="calc.inputNumber('6')" style="padding: 15px;">6</button>
    <button onclick="calc.inputOperator('+')" style="padding: 15px;">+</button>
    <button onclick="calc.inputNumber('1')" style="padding: 15px;">1</button>
    <button onclick="calc.inputNumber('2')" style="padding: 15px;">2</button>
    <button onclick="calc.inputNumber('3')" style="padding: 15px;">3</button>
    <button onclick="calc.inputOperator('=')" style="grid-row: span 2; padding: 15px;">=</button>
    <button onclick="calc.inputNumber('0')" style="grid-column: span 2; padding: 15px;">0</button>
    <button onclick="calc.inputNumber('.')" style="padding: 15px;">.</button>
  </div>
</div>
\`);`
    }
  ], []);

  // Calculate template counts for filters
  const templateCounts = useMemo(() => ({
    all: extendedTemplates.length,
    javascript: extendedTemplates.filter(t => t.language === 'javascript').length,
    python: extendedTemplates.filter(t => t.language === 'python').length,
    html: extendedTemplates.filter(t => t.language === 'html').length,
    react: extendedTemplates.filter(t => t.category === 'react').length,
    beginner: extendedTemplates.filter(t => t.difficulty === 'beginner').length
  }), [extendedTemplates]);

  return (
    <Card className="w-full h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Templates Library</h2>
          <p className="text-gray-600 mt-1">Choose a template to start coding</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-hidden flex flex-col">
        <TemplateFilters
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          templateCounts={templateCounts}
        />

        <div className="flex-1 overflow-y-auto">
          <TemplateGrid
            templates={extendedTemplates}
            onSelectTemplate={onSelectTemplate}
            searchTerm={searchTerm}
            selectedCategory={selectedCategory}
          />
        </div>
      </div>
    </Card>
  );
};

export default TemplatesLibrary;