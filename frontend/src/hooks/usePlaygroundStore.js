'use client';

import { useState, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';

export const usePlaygroundStore = () => {
  const user = useSelector(selectCurrentUser);
  
  // Core playground state
  const [code, setCode] = useState(`console.log("Hello, World!");

// Welcome to the Gradvy Playground!
// Try writing some JavaScript code and click Run to see the output.

function greet(name) {
    return \`Hello, \${name}! Ready to learn?\`;
}

console.log(greet("Learner"));`);
  
  const [language, setLanguage] = useState('javascript');
  const [theme, setTheme] = useState('dark');
  const [isRunning, setIsRunning] = useState(false);
  const [output, setOutput] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  // Saved snippets and projects
  const [savedSnippets, setSavedSnippets] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);

  // Settings
  const [settings, setSettings] = useState({
    fontSize: 14,
    tabSize: 2,
    wordWrap: true,
    minimap: false,
    autoSave: true,
    autoRun: false
  });

  // Clear output
  const clearOutput = useCallback(() => {
    setOutput([]);
  }, []);

  // Add output line
  const addOutput = useCallback((message, type = 'log') => {
    const timestamp = new Date().toLocaleTimeString();
    setOutput(prev => [...prev, {
      id: Date.now() + Math.random(),
      message,
      type,
      timestamp
    }]);
  }, []);

  // Execute code based on language
  const runCode = useCallback(async () => {
    if (isRunning) return;
    
    setIsRunning(true);
    clearOutput();
    addOutput(`Running ${language} code...`, 'info');

    try {
      switch (language) {
        case 'javascript':
          await executeJavaScript(code);
          break;
        case 'python':
          await executePython(code);
          break;
        case 'html':
        case 'css':
          // For HTML/CSS, the preview panel handles execution
          addOutput(`${language.toUpperCase()} code loaded in preview panel.`, 'info');
          break;
        default:
          addOutput(`Language ${language} is not yet supported for execution.`, 'warn');
      }
    } catch (error) {
      addOutput(`Execution error: ${error.message}`, 'error');
    } finally {
      setIsRunning(false);
    }
  }, [code, language, isRunning, clearOutput, addOutput]);

  // JavaScript execution
  const executeJavaScript = useCallback(async (jsCode) => {
    return new Promise((resolve) => {
      try {
        // Capture console output
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        
        const logs = [];
        
        console.log = (...args) => {
          logs.push({ message: args.join(' '), type: 'log' });
          originalLog.apply(console, args);
        };
        
        console.error = (...args) => {
          logs.push({ message: args.join(' '), type: 'error' });
          originalError.apply(console, args);
        };
        
        console.warn = (...args) => {
          logs.push({ message: args.join(' '), type: 'warn' });
          originalWarn.apply(console, args);
        };

        // Execute the code
        const result = eval(jsCode);
        
        // If there's a return value and no console output, show the result
        if (result !== undefined && logs.length === 0) {
          logs.push({ message: String(result), type: 'log' });
        }
        
        // Restore original console functions
        console.log = originalLog;
        console.error = originalError;
        console.warn = originalWarn;
        
        // Add all captured logs to output
        logs.forEach(log => {
          addOutput(log.message, log.type);
        });
        
        if (logs.length === 0) {
          addOutput('Code executed successfully (no output)', 'info');
        }
        
        resolve();
      } catch (error) {
        addOutput(`Error: ${error.message}`, 'error');
        resolve();
      }
    });
  }, [addOutput]);

  // Python execution (simulated - would need a real Python interpreter)
  const executePython = useCallback(async (pythonCode) => {
    return new Promise((resolve) => {
      try {
        // This is a very basic Python simulation
        // In a real implementation, you'd use a Python interpreter like Pyodide
        
        addOutput('Note: Python execution is simulated in this demo', 'warn');
        
        // Look for print statements
        const printRegex = /print\((.*?)\)/g;
        let match;
        let foundOutput = false;
        
        while ((match = printRegex.exec(pythonCode)) !== null) {
          foundOutput = true;
          try {
            // Very basic evaluation of print arguments
            let printArg = match[1].trim();
            
            // Handle string literals
            if (printArg.startsWith('"') && printArg.endsWith('"')) {
              printArg = printArg.slice(1, -1);
            } else if (printArg.startsWith("'") && printArg.endsWith("'")) {
              printArg = printArg.slice(1, -1);
            }
            
            addOutput(printArg, 'log');
          } catch (e) {
            addOutput(`Print statement: ${match[1]}`, 'log');
          }
        }
        
        if (!foundOutput) {
          addOutput('Python code executed (no print statements found)', 'info');
        }
        
        resolve();
      } catch (error) {
        addOutput(`Python execution error: ${error.message}`, 'error');
        resolve();
      }
    });
  }, [addOutput]);

  // Stop code execution
  const stopCode = useCallback(() => {
    setIsRunning(false);
    addOutput('Execution stopped by user', 'warn');
  }, [addOutput]);

  // Save current code as snippet
  const saveCode = useCallback(async ({ name, description = '' }) => {
    try {
      const snippet = {
        id: Date.now(),
        name: name || `Snippet ${savedSnippets.length + 1}`,
        description,
        code,
        language,
        createdAt: new Date().toISOString(),
        userId: user?.id
      };
      
      setSavedSnippets(prev => [snippet, ...prev]);
      addOutput(`Code saved as "${snippet.name}"`, 'info');
      
      // In a real app, you'd save to backend here
      // await api.saveSnippet(snippet);
      
      return snippet;
    } catch (error) {
      addOutput(`Save error: ${error.message}`, 'error');
      throw error;
    }
  }, [code, language, savedSnippets.length, user?.id, addOutput]);

  // Load a template or snippet
  const loadTemplate = useCallback((template) => {
    setCode(template.code);
    setLanguage(template.language);
    setSelectedTemplate(template);
    addOutput(`Loaded template: ${template.name}`, 'info');
  }, [addOutput]);

  // Share code (generate shareable link)
  const shareCode = useCallback(async () => {
    try {
      const shareData = {
        code,
        language,
        createdAt: new Date().toISOString(),
        createdBy: user?.email || 'Anonymous'
      };
      
      // In a real app, you'd save to backend and get a share URL
      // const response = await api.shareCode(shareData);
      // return response.shareUrl;
      
      // For demo, just copy code to clipboard
      const shareText = `// Shared from Gradvy Playground
// Language: ${language}
// Created: ${shareData.createdAt}
// By: ${shareData.createdBy}

${code}`;
      
      await navigator.clipboard.writeText(shareText);
      addOutput('Code copied to clipboard for sharing', 'info');
      
      return window.location.href; // Mock share URL
    } catch (error) {
      addOutput(`Share error: ${error.message}`, 'error');
      throw error;
    }
  }, [code, language, user?.email, addOutput]);

  // Load saved snippet
  const loadSnippet = useCallback((snippet) => {
    setCode(snippet.code);
    setLanguage(snippet.language);
    addOutput(`Loaded snippet: ${snippet.name}`, 'info');
  }, [addOutput]);

  // Delete saved snippet
  const deleteSnippet = useCallback((snippetId) => {
    setSavedSnippets(prev => prev.filter(s => s.id !== snippetId));
    addOutput('Snippet deleted', 'info');
  }, [addOutput]);

  // Update settings
  const updateSettings = useCallback((newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  // Reset playground
  const reset = useCallback(() => {
    setCode('// Welcome to Gradvy Playground!\nconsole.log("Hello, World!");');
    setLanguage('javascript');
    clearOutput();
    setSelectedTemplate(null);
    addOutput('Playground reset', 'info');
  }, [clearOutput, addOutput]);

  // Export current state
  const exportProject = useCallback(() => {
    const project = {
      name: `Playground Project ${new Date().toISOString().split('T')[0]}`,
      code,
      language,
      createdAt: new Date().toISOString(),
      settings
    };
    
    const dataStr = JSON.stringify(project, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${project.name.toLowerCase().replace(/\s+/g, '-')}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    addOutput('Project exported successfully', 'info');
  }, [code, language, settings, addOutput]);

  // Import project
  const importProject = useCallback((projectData) => {
    try {
      setCode(projectData.code || '');
      setLanguage(projectData.language || 'javascript');
      if (projectData.settings) {
        setSettings(projectData.settings);
      }
      addOutput(`Project imported: ${projectData.name || 'Unnamed'}`, 'info');
    } catch (error) {
      addOutput(`Import error: ${error.message}`, 'error');
    }
  }, [addOutput]);

  return {
    // State
    code,
    language,
    theme,
    isRunning,
    output,
    selectedTemplate,
    savedSnippets,
    currentProject,
    settings,
    
    // Actions
    setCode,
    setLanguage,
    setTheme,
    runCode,
    stopCode,
    clearOutput,
    addOutput,
    saveCode,
    loadTemplate,
    shareCode,
    loadSnippet,
    deleteSnippet,
    updateSettings,
    reset,
    exportProject,
    importProject
  };
};