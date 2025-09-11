'use client';

import React, { useEffect, useRef, useState } from 'react';
import { RefreshCw, AlertCircle, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const PreviewPanel = ({ code, language, isRunning }) => {
  const iframeRef = useRef(null);
  const [previewError, setPreviewError] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const generateHTMLPreview = (sourceCode, lang) => {
    try {
      let htmlContent = '';
      
      switch (lang) {
        case 'html':
          htmlContent = sourceCode;
          break;
          
        case 'javascript':
          htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Preview</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .output {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-family: monospace;
            min-height: 100px;
            white-space: pre-wrap;
        }
        .error {
            background: #fee;
            border-color: #fcc;
            color: #c33;
        }
        #root {
            min-height: 200px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: background-color 0.2s;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
    </style>
    <!-- React CDN for React examples -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
    <div class="container">
        <h2>🚀 JavaScript Playground</h2>
        <div id="root"></div>
        <div class="output" id="output">Ready to run JavaScript...</div>
    </div>
    <script>
        // Capture console output
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        const outputDiv = document.getElementById('output');
        
        function addToOutput(message, type = 'log') {
            const timestamp = new Date().toLocaleTimeString();
            const prefix = type === 'error' ? '❌' : type === 'warn' ? '⚠️' : '📝';
            outputDiv.innerHTML += \`[\${timestamp}] \${prefix} \${message}\\n\`;
            if (type === 'error') {
                outputDiv.classList.add('error');
            }
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }
        
        console.log = function(...args) {
            addToOutput(args.join(' '), 'log');
            originalLog.apply(console, args);
        };
        
        console.error = function(...args) {
            addToOutput(args.join(' '), 'error');
            originalError.apply(console, args);
        };
        
        console.warn = function(...args) {
            addToOutput(args.join(' '), 'warn');
            originalWarn.apply(console, args);
        };
        
        // Clear output and run code
        outputDiv.innerHTML = '';
        outputDiv.classList.remove('error');
        
        try {
            // Check if code contains JSX (React)
            const hasJSX = /${sourceCode}/.test(/jsx?\\s*:/i) || 
                         /${sourceCode}/.test(/<\\w+/) ||
                         /React/.test(\`${sourceCode}\`);
            
            if (hasJSX) {
                // Transform and execute JSX
                const transformedCode = Babel.transform(\`${sourceCode.replace(/`/g, '\\`')}\`, {
                    presets: ['react', 'env']
                }).code;
                eval(transformedCode);
            } else {
                // Execute regular JavaScript
                eval(\`${sourceCode.replace(/`/g, '\\`')}\`);
            }
        } catch (error) {
            console.error('Error: ' + error.message);
        }
    </script>
</body>
</html>`;
          break;
          
        case 'css':
          htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Preview</title>
    <style>
        ${sourceCode}
    </style>
</head>
<body>
    <div class="demo-container">
        <h1>CSS Preview</h1>
        <p>This is a preview of your CSS styles.</p>
        <div class="demo-content">
            <button>Button</button>
            <div class="box">Box Element</div>
            <ul>
                <li>List Item 1</li>
                <li>List Item 2</li>
                <li>List Item 3</li>
            </ul>
        </div>
    </div>
</body>
</html>`;
          break;
          
        default:
          htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
            text-align: center;
        }
        .code-preview {
            background: #f1f3f4;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            text-align: left;
            max-height: 400px;
            overflow-y: auto;
        }
        .language-badge {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>📄 Code Preview</h2>
        <div class="language-badge">${lang.toUpperCase()}</div>
        <div class="code-preview">${sourceCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        <p>This language doesn't support live preview. Use the console to see output when you run the code.</p>
    </div>
</body>
</html>`;
      }
      
      return htmlContent;
    } catch (error) {
      return `
<!DOCTYPE html>
<html>
<head><title>Preview Error</title></head>
<body style="font-family: Arial, sans-serif; padding: 20px; color: #721c24; background: #f8d7da;">
    <h3>⚠️ Preview Error</h3>
    <p>${error.message}</p>
</body>
</html>`;
    }
  };

  const updatePreview = () => {
    if (!iframeRef.current) return;
    
    setIsRefreshing(true);
    setPreviewError(null);
    
    try {
      const htmlContent = generateHTMLPreview(code, language);
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      
      iframeRef.current.src = url;
      
      // Cleanup previous URL after a delay
      setTimeout(() => {
        URL.revokeObjectURL(url);
        setIsRefreshing(false);
      }, 1000);
      
    } catch (error) {
      setPreviewError(error.message);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    updatePreview();
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      updatePreview();
    }, 500); // Debounce updates

    return () => clearTimeout(timer);
  }, [code, language]);

  const isWebLanguage = ['html', 'css', 'javascript'].includes(language);

  return (
    <div className="h-full flex flex-col">
      {/* Preview Header */}
      <div className="flex items-center justify-between p-3 border-b bg-gray-50">
        <div className="flex items-center space-x-2">
          <Globe className="h-4 w-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Live Preview</span>
          <Badge variant={isWebLanguage ? 'default' : 'secondary'} className="text-xs">
            {language.toUpperCase()}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          {isRefreshing && (
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <RefreshCw className="h-3 w-3 animate-spin" />
              <span>Updating...</span>
            </div>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-3 w-3 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 relative">
        {previewError ? (
          <div className="h-full flex items-center justify-center p-6 bg-red-50">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-700 mb-2">Preview Error</h3>
              <p className="text-red-600 text-sm max-w-md">{previewError}</p>
            </div>
          </div>
        ) : (
          <iframe
            ref={iframeRef}
            className="w-full h-full border-0"
            sandbox="allow-scripts allow-same-origin allow-forms allow-modals"
            title="Code Preview"
          />
        )}
      </div>

      {/* Preview Status */}
      {!isWebLanguage && (
        <div className="p-3 bg-amber-50 border-t border-amber-200">
          <div className="flex items-center space-x-2 text-amber-700">
            <AlertCircle className="h-4 w-4" />
            <span className="text-xs">
              Live preview is only available for HTML, CSS, and JavaScript. 
              Run your code to see output in the console.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreviewPanel;