// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/playground/data/PlaygroundTemplates.js
// Playground code templates and examples extracted from massive playground page
// Contains all template data for different programming languages and frameworks
// RELEVANT FILES: PlaygroundPage.jsx, TemplatesLibrary.jsx, CodeEditor.jsx, PlaygroundToolbar.jsx

export const defaultTemplates = [
  {
    id: 'welcome-html',
    name: 'Welcome HTML',
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
    <div style="padding: 20px; text-align: center;">
      <h2>{{ message }}</h2>
      <p>Count: {{ count }}</p>
      <button @click="increment" style="margin: 5px; padding: 10px 20px; background: #42b883; color: white; border: none; border-radius: 5px;">+</button>
      <button @click="decrement" style="margin: 5px; padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 5px;">-</button>
    </div>
  \`
}).mount('#app');`
  },
  {
    id: 'python-basics',
    name: 'Python Basics',
    language: 'python',
    code: `# Python Basics Example
print("Welcome to Python Playground!")

# Variables and data types
name = "Gradvy"
version = 2024
features = ["Learning", "AI-Powered", "Interactive"]

print(f"Platform: {name}")
print(f"Version: {version}")
print("Features:")
for feature in features:
    print(f"  - {feature}")

# Simple function
def calculate_learning_score(hours_studied, assignments_completed):
    base_score = hours_studied * 10
    bonus = assignments_completed * 5
    return min(base_score + bonus, 100)

# Test the function
score = calculate_learning_score(8, 12)
print(f"\\nYour learning score: {score}/100")

if score >= 80:
    print("Excellent work! 🎉")
elif score >= 60:
    print("Good progress! 👍")
else:
    print("Keep learning! 📚")`
  },
  {
    id: 'css-animations',
    name: 'CSS Animations',
    language: 'css',
    code: `/* CSS Animations Playground */
body {
    margin: 0;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: Arial, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.animation-container {
    text-align: center;
}

.bounce-box {
    width: 100px;
    height: 100px;
    background: #ff6b6b;
    margin: 20px auto;
    border-radius: 10px;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-30px); }
}

.pulse-text {
    color: white;
    font-size: 2em;
    animation: pulse 3s infinite;
}

@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
    100% { opacity: 1; transform: scale(1); }
}

.rotate-element {
    width: 80px;
    height: 80px;
    background: #4ecdc4;
    margin: 20px auto;
    animation: rotate 4s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}`
  },
  {
    id: 'javascript-es6',
    name: 'Modern JavaScript',
    language: 'javascript',
    code: `// Modern JavaScript (ES6+) Features
console.log("🚀 Modern JavaScript Playground");

// Destructuring
const student = {
    name: "Alex",
    age: 22,
    courses: ["React", "Node.js", "Python"],
    grades: { math: 90, science: 85 }
};

const { name, courses, grades: { math } } = student;
console.log(\`Student: \${name}, Math Grade: \${math}\`);

// Arrow functions and array methods
const courseStats = courses
    .map(course => ({ name: course, difficulty: Math.floor(Math.random() * 5) + 1 }))
    .filter(course => course.difficulty >= 3)
    .sort((a, b) => b.difficulty - a.difficulty);

console.log("Advanced Courses:", courseStats);

// Async/await example
async function fetchLearningData() {
    try {
        // Simulate API call
        const data = await new Promise(resolve => 
            setTimeout(() => resolve({ 
                totalHours: 120, 
                completedProjects: 8,
                skillLevel: "Intermediate"
            }), 1000)
        );
        
        console.log("Learning Progress:", data);
        return data;
    } catch (error) {
        console.error("Failed to fetch data:", error);
    }
}

// Template literals and promises
const generateReport = (data) => \`
📊 Learning Report
==================
Total Study Hours: \${data.totalHours}
Projects Completed: \${data.completedProjects}
Current Skill Level: \${data.skillLevel}
==================
\`;

fetchLearningData().then(data => {
    if (data) console.log(generateReport(data));
});`
  }
];

export const templateCategories = [
  { id: 'all', name: 'All Templates', count: defaultTemplates.length },
  { id: 'html', name: 'HTML', count: defaultTemplates.filter(t => t.language === 'html').length },
  { id: 'javascript', name: 'JavaScript', count: defaultTemplates.filter(t => t.language === 'javascript').length },
  { id: 'python', name: 'Python', count: defaultTemplates.filter(t => t.language === 'python').length },
  { id: 'css', name: 'CSS', count: defaultTemplates.filter(t => t.language === 'css').length },
];

export const getTemplatesByCategory = (category) => {
  if (category === 'all') return defaultTemplates;
  return defaultTemplates.filter(template => template.language === category);
};

export const getTemplateById = (id) => {
  return defaultTemplates.find(template => template.id === id);
};

export default {
  defaultTemplates,
  templateCategories,
  getTemplatesByCategory,
  getTemplateById
};