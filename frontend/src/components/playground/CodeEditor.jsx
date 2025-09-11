'use client';

import React, { forwardRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';

const CodeEditor = forwardRef(({ 
  value, 
  language, 
  theme = 'vs-dark', 
  onChange, 
  options = {},
  onMount
}, ref) => {
  const handleEditorDidMount = (editor, monaco) => {
    // Configure Monaco Editor themes
    monaco.editor.defineTheme('gradvy-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6A9955' },
        { token: 'keyword', foreground: '569CD6' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' }
      ],
      colors: {
        'editor.background': '#0F172A',
        'editor.foreground': '#E2E8F0',
        'editorLineNumber.foreground': '#64748B',
        'editorLineNumber.activeForeground': '#F1F5F9',
        'editor.selectionBackground': '#334155',
        'editor.cursor': '#F1F5F9'
      }
    });

    monaco.editor.defineTheme('gradvy-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '008000' },
        { token: 'keyword', foreground: '0000FF' },
        { token: 'string', foreground: 'A31515' },
        { token: 'number', foreground: '098658' }
      ],
      colors: {
        'editor.background': '#FFFFFF',
        'editor.foreground': '#1E293B',
        'editorLineNumber.foreground': '#94A3B8',
        'editorLineNumber.activeForeground': '#1E293B',
        'editor.selectionBackground': '#E2E8F0',
        'editor.cursor': '#1E293B'
      }
    });

    // Set up language-specific configurations
    if (language === 'javascript') {
      monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
        target: monaco.languages.typescript.ScriptTarget.Latest,
        allowNonTsExtensions: true,
        moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
        module: monaco.languages.typescript.ModuleKind.CommonJS,
        noEmit: true,
        esModuleInterop: true,
        jsx: monaco.languages.typescript.JsxEmit.React,
        reactNamespace: 'React',
        allowJs: true,
        typeRoots: ['node_modules/@types']
      });

      monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
        noSemanticValidation: false,
        noSyntaxValidation: false,
        noSuggestionDiagnostics: true
      });
    }

    // Add common snippets
    const addSnippets = (lang) => {
      const snippets = {
        javascript: [
          {
            label: 'log',
            insertText: 'console.log(${1:message});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Log a message to the console'
          },
          {
            label: 'function',
            insertText: 'function ${1:name}(${2:params}) {\n\t${3:// body}\n\treturn ${4:value};\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a function'
          },
          {
            label: 'arrow',
            insertText: 'const ${1:name} = (${2:params}) => {\n\t${3:// body}\n\treturn ${4:value};\n};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create an arrow function'
          }
        ],
        python: [
          {
            label: 'print',
            insertText: 'print(${1:message})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Print a message'
          },
          {
            label: 'def',
            insertText: 'def ${1:name}(${2:params}):\n    ${3:# body}\n    return ${4:value}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Define a function'
          },
          {
            label: 'class',
            insertText: 'class ${1:ClassName}:\n    def __init__(self${2:, params}):\n        ${3:# initialization}\n        pass\n    \n    def ${4:method_name}(self${5:, params}):\n        ${6:# method body}\n        pass',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create a class'
          }
        ]
      };

      if (snippets[lang]) {
        monaco.languages.registerCompletionItemProvider(lang, {
          provideCompletionItems: (model, position) => {
            const suggestions = snippets[lang].map(snippet => ({
              ...snippet,
              kind: monaco.languages.CompletionItemKind.Snippet,
              range: {
                startLineNumber: position.lineNumber,
                endLineNumber: position.lineNumber,
                startColumn: position.column,
                endColumn: position.column
              }
            }));
            return { suggestions };
          }
        });
      }
    };

    addSnippets(language);

    // Store editor instance
    if (ref) {
      ref.current = editor;
    }

    // Call onMount callback
    if (onMount) {
      onMount(editor, monaco);
    }
  };

  const defaultOptions = {
    selectOnLineNumbers: true,
    automaticLayout: true,
    wordWrap: 'on',
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on',
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 20,
    lineNumbersMinChars: 3,
    renderLineHighlight: 'all',
    scrollBeyondLastLine: false,
    smoothScrolling: true,
    cursorStyle: 'line',
    cursorBlinking: 'smooth',
    renderWhitespace: 'selection',
    tabSize: 2,
    insertSpaces: true,
    detectIndentation: true,
    trimAutoWhitespace: true,
    acceptSuggestionOnEnter: 'on',
    suggestOnTriggerCharacters: true,
    tabCompletion: 'on',
    wordBasedSuggestions: true,
    parameterHints: {
      enabled: true
    },
    quickSuggestions: {
      other: true,
      comments: false,
      strings: false
    },
    ...options
  };

  return (
    <div className="h-full w-full">
      <Editor
        height="100%"
        defaultLanguage={language}
        language={language}
        value={value}
        theme={theme === 'dark' ? 'gradvy-dark' : 'gradvy-light'}
        onChange={onChange}
        onMount={handleEditorDidMount}
        options={defaultOptions}
        loading={
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        }
      />
    </div>
  );
});

CodeEditor.displayName = 'CodeEditor';

export default CodeEditor;