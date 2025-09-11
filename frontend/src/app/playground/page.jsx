/*
 * File: frontend/src/app/playground/page.jsx  
 * Description: Public playground page showcasing Gradvy's interactive coding environment
 * Purpose: Allow users to try coding features without registration, driving conversion to full platform
 * Relevant Files: components/playground/*, components/sections/Hero.jsx, app/layout.js
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Square, 
  RotateCcw, 
  Share2, 
  Save, 
  Download,
  Settings,
  Maximize2,
  Minimize2,
  FileText,
  Users,
  Zap,
  Coffee,
  Trophy
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from '@/store/slices/authSlice';
import Link from 'next/link';
import toast from 'react-hot-toast';
import Head from 'next/head';

import PlaygroundHero from '@/components/playground/PlaygroundHero';
import CodeEditor from '@/components/playground/CodeEditor';
import PreviewPanel from '@/components/playground/PreviewPanel';
import ConsolePanel from '@/components/playground/ConsolePanel';
import TemplatesLibrary from '@/components/playground/TemplatesLibrary';

export default function PlaygroundPage() {
  const [showPlayground, setShowPlayground] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('javascript');
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [output, setOutput] = useState('');
  const [showTemplates, setShowTemplates] = useState(false);
  const [editorTheme, setEditorTheme] = useState('dark');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSavePrompt, setShowSavePrompt] = useState(false);

  const editorRef = useRef(null);
  const isAuthenticated = useSelector(selectIsAuthenticated);

  const languages = [
    { id: 'javascript', name: 'JavaScript', icon: '🟨', color: 'bg-yellow-100 text-yellow-800' },
    { id: 'python', name: 'Python', icon: '🐍', color: 'bg-green-100 text-green-800' },
    { id: 'html', name: 'HTML/CSS', icon: '🌐', color: 'bg-orange-100 text-orange-800' },
    { id: 'react', name: 'React', icon: '⚛️', color: 'bg-blue-100 text-blue-800' }
  ];

  const defaultTemplates = [
    {
      id: 'hello-world-js',
      name: 'Hello World',
      language: 'javascript',
      category: 'beginner',
      difficulty: 'beginner',
      tags: ['basics', 'console'],
      description: 'Your first JavaScript program',
      code: `// Welcome to Gradvy Playground! 
console.log("Hello, World! 🌍");

// Try modifying this message
const greeting = "Welcome to coding!";
console.log(greeting);

// Create a simple function
function celebrate(name) {
    return \`🎉 Congratulations \${name}! You're coding! 🎉\`;
}

console.log(celebrate("Future Developer"));`
    },
    {
      id: 'interactive-demo',
      name: 'Interactive Demo',
      language: 'javascript',
      category: 'beginner',
      difficulty: 'beginner',
      tags: ['interactive', 'dom'],
      description: 'Interactive elements demo',
      code: `// Interactive Elements Demo
document.body.innerHTML = \`
<div style="padding: 20px; font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1 style="color: #4F46E5;">🎮 Interactive Playground</h1>
    <div style="margin: 20px 0;">
        <button id="colorBtn" style="padding: 10px 20px; background: #4F46E5; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">Change Color</button>
        <button id="countBtn" style="padding: 10px 20px; background: #059669; color: white; border: none; border-radius: 5px; cursor: pointer;">Count: 0</button>
    </div>
    <div id="output" style="padding: 20px; background: #F3F4F6; border-radius: 8px; margin: 20px 0;">
        <h3>Output Area</h3>
        <p>Click the buttons to see magic happen! ✨</p>
    </div>
    <div style="margin: 20px 0;">
        <input id="nameInput" placeholder="Enter your name..." style="padding: 10px; border: 1px solid #D1D5DB; border-radius: 5px; margin-right: 10px;">
        <button id="greetBtn" style="padding: 10px 20px; background: #DC2626; color: white; border: none; border-radius: 5px; cursor: pointer;">Greet Me!</button>
    </div>
</div>
\`;

let count = 0;
const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'];
let colorIndex = 0;

// Color changer
document.getElementById('colorBtn').addEventListener('click', () => {
    document.body.style.background = colors[colorIndex % colors.length];
    colorIndex++;
    document.getElementById('output').innerHTML = \`
        <h3>Color Changed! 🎨</h3>
        <p>Background color: \${colors[(colorIndex-1) % colors.length]}</p>
    \`;
});

// Counter
document.getElementById('countBtn').addEventListener('click', () => {
    count++;
    document.getElementById('countBtn').textContent = \`Count: \${count}\`;
    if (count === 10) {
        document.getElementById('output').innerHTML = \`
            <h3>🎉 Congratulations!</h3>
            <p>You reached 10 clicks! You're a clicking champion!</p>
        \`;
    }
});

// Greeting
document.getElementById('greetBtn').addEventListener('click', () => {
    const name = document.getElementById('nameInput').value || 'Anonymous Developer';
    document.getElementById('output').innerHTML = \`
        <h3>👋 Hello, \${name}!</h3>
        <p>Welcome to the world of interactive coding! Ready to build amazing things?</p>
        <p style="font-style: italic; color: #666;">Tip: Try changing your name and greeting again!</p>
    \`;
});

console.log('Interactive demo loaded! Try clicking the buttons! 🎮');`
    }
  ];

  useEffect(() => {
    if (currentLanguage === 'javascript' && !code) {
      setCode(defaultTemplates[0].code);
    }
  }, [currentLanguage, code]);

  const handleRunCode = async () => {
    if (!code.trim()) {
      toast.error('Please write some code first!');
      return;
    }

    setIsRunning(true);
    setOutput('');

    try {
      if (currentLanguage === 'javascript') {
        // Capture console.log output
        const originalLog = console.log;
        let capturedOutput = '';
        
        console.log = (...args) => {
          capturedOutput += args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
          ).join(' ') + '\n';
          originalLog(...args);
        };

        // Execute the code
        try {
          const result = eval(code);
          if (result !== undefined) {
            capturedOutput += `Result: ${result}\n`;
          }
        } catch (error) {
          capturedOutput += `Error: ${error.message}\n`;
        }

        // Restore original console.log
        console.log = originalLog;
        setOutput(capturedOutput || 'Code executed successfully!');
      } else {
        setOutput(`${currentLanguage} execution coming soon! 🚀\nFor now, try JavaScript to see your code in action.`);
      }
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleShare = () => {
    if (!isAuthenticated) {
      setShowSavePrompt(true);
      return;
    }
    
    toast.success('Share feature coming soon!');
  };

  const handleSave = () => {
    if (!isAuthenticated) {
      setShowSavePrompt(true);
      return;
    }
    
    toast.success('Save feature coming soon!');
  };

  const handleTemplateSelect = (template) => {
    setCode(template.code);
    setCurrentLanguage(template.language);
    setShowTemplates(false);
    toast.success(`Template "${template.name}" loaded!`);
  };

  const handleStartCoding = () => {
    setShowPlayground(true);
  };

  if (!showPlayground) {
    return (
      <>
        <Head>
          <title>Online Code Playground - Try Programming Languages Free | Gradvy</title>
          <meta name="description" content="Free online code playground. Write, run, and share JavaScript, Python, HTML/CSS code instantly. No setup required. Interactive coding environment with templates and real-time execution." />
          <meta name="keywords" content="online code editor, JavaScript playground, Python compiler, HTML CSS editor, free coding environment, programming practice, code sharing, web development tools" />
          <meta property="og:title" content="Free Online Code Playground - Gradvy" />
          <meta property="og:description" content="Write, run, and share code instantly with our free online playground. Support for JavaScript, Python, HTML/CSS and more." />
          <meta property="og:type" content="website" />
          <meta property="og:url" content="/playground" />
          <meta property="og:image" content="/images/playground-og.jpg" />
          <meta name="twitter:card" content="summary_large_image" />
          <meta name="twitter:title" content="Free Online Code Playground - Gradvy" />
          <meta name="twitter:description" content="Write, run, and share code instantly with our free online playground." />
          <meta name="twitter:image" content="/images/playground-twitter.jpg" />
          <link rel="canonical" href="/playground" />
        </Head>
        <div className="min-h-screen">
          <PlaygroundHero onStartCoding={handleStartCoding} />
        
        {/* Features Section */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                Why Developers Choose Our Playground
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Experience the most advanced online coding environment with features that make learning and building faster than ever.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {[
                {
                  icon: Zap,
                  title: 'Lightning Fast',
                  description: 'Instant code execution with no setup time',
                  color: 'text-yellow-600 bg-yellow-100'
                },
                {
                  icon: Users,
                  title: 'Collaborate Live',
                  description: 'Real-time coding with team members',
                  color: 'text-blue-600 bg-blue-100'
                },
                {
                  icon: Coffee,
                  title: 'Always Available',
                  description: 'Code anywhere, anytime, on any device',
                  color: 'text-brown-600 bg-amber-100'
                },
                {
                  icon: Trophy,
                  title: 'Learn & Grow',
                  description: 'Challenges and projects to advance skills',
                  color: 'text-purple-600 bg-purple-100'
                }
              ].map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="text-center"
                  >
                    <div className={`w-16 h-16 ${feature.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                      <Icon className="h-8 w-8" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
              Ready to Start Your Coding Journey?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of developers who are building amazing projects with Gradvy.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                onClick={handleStartCoding}
                className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-xl"
              >
                Try Playground Now
              </Button>
              <Link href="/register">
                <Button
                  variant="outline"
                  size="lg"
                  className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg font-semibold rounded-xl"
                >
                  Create Free Account
                </Button>
              </Link>
            </div>
          </div>
        </section>
        </div>
      </>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-100 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Header Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-gray-900">Gradvy Playground</h1>
            
            {/* Language Selector */}
            <div className="flex items-center space-x-2">
              {languages.map((lang) => (
                <Button
                  key={lang.id}
                  variant={currentLanguage === lang.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setCurrentLanguage(lang.id)}
                  className="flex items-center space-x-1"
                >
                  <span>{lang.icon}</span>
                  <span>{lang.name}</span>
                </Button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowTemplates(true)}
            >
              <FileText className="h-4 w-4 mr-1" />
              Templates
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>

            <Button
              size="sm"
              onClick={handleRunCode}
              disabled={isRunning}
              className="bg-green-600 hover:bg-green-700"
            >
              {isRunning ? (
                <Square className="h-4 w-4 mr-1" />
              ) : (
                <Play className="h-4 w-4 mr-1" />
              )}
              {isRunning ? 'Running...' : 'Run'}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Code Editor */}
        <div className="flex-1 flex flex-col">
          <div className="flex items-center justify-between bg-gray-800 text-white px-4 py-2 text-sm">
            <span>Code Editor</span>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSave}
                className="text-gray-300 hover:text-white"
              >
                <Save className="h-3 w-3 mr-1" />
                Save
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleShare}
                className="text-gray-300 hover:text-white"
              >
                <Share2 className="h-3 w-3 mr-1" />
                Share
              </Button>
            </div>
          </div>
          
          <div className="flex-1">
            <CodeEditor
              ref={editorRef}
              value={code}
              language={currentLanguage}
              theme={editorTheme}
              onChange={(value) => setCode(value || '')}
            />
          </div>
        </div>

        {/* Output Panel */}
        <div className="w-1/3 border-l border-gray-300 flex flex-col">
          <div className="bg-gray-800 text-white px-4 py-2 text-sm">
            <span>Output</span>
          </div>
          
          <div className="flex-1 bg-gray-900 text-green-400 p-4 overflow-y-auto font-mono text-sm">
            {output ? (
              <pre className="whitespace-pre-wrap">{output}</pre>
            ) : (
              <div className="text-gray-500">
                <p>Click "Run" to execute your code...</p>
                <p className="mt-2 text-xs">💡 Pro tip: Use console.log() to see output here!</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Templates Modal */}
      <AnimatePresence>
        {showTemplates && (
          <TemplatesLibrary
            templates={defaultTemplates}
            onSelect={handleTemplateSelect}
            onClose={() => setShowTemplates(false)}
          />
        )}
      </AnimatePresence>

      {/* Save Prompt Modal */}
      <AnimatePresence>
        {showSavePrompt && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setShowSavePrompt(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-lg p-6 max-w-md mx-4"
            >
              <h3 className="text-lg font-semibold mb-4">Save Your Work</h3>
              <p className="text-gray-600 mb-6">
                Sign up for free to save your code, access templates, and collaborate with others!
              </p>
              <div className="flex space-x-3">
                <Link href="/register" className="flex-1">
                  <Button className="w-full">Sign Up Free</Button>
                </Link>
                <Button
                  variant="outline"
                  onClick={() => setShowSavePrompt(false)}
                >
                  Later
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}