// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/playground/page.jsx
// Main playground page for code editing, execution, and learning
// Refactored from massive 817-line component into focused modular components
// RELEVANT FILES: PlaygroundToolbar.jsx, PlaygroundLayout.jsx, PlaygroundTemplates.js, TemplatesLibrary.jsx

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText } from 'lucide-react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TemplatesLibrary from '@/components/playground/TemplatesLibrary';
import { usePlaygroundStore } from '@/hooks/usePlaygroundStore';
import PlaygroundToolbar from './components/PlaygroundToolbar';
import PlaygroundLayout from './components/PlaygroundLayout';

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

  const handleTemplatesToggle = () => {
    setShowTemplates(!showTemplates);
  };

  const handleTemplateSelect = (template) => {
    loadTemplate(template);
    setLanguage(template.language);
    setShowTemplates(false);
  };

  return (
    <ProtectedRoute>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border-b"
        >
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Code Playground</h1>
                <p className="text-sm text-gray-600">Write, run, and experiment with code</p>
              </div>
            </div>
            
            {selectedTemplate && (
              <div className="text-sm text-gray-600">
                Current: <span className="font-medium">{selectedTemplate.name}</span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Toolbar */}
        <PlaygroundToolbar
          language={language}
          setLanguage={setLanguage}
          theme={theme}
          setTheme={setTheme}
          isRunning={isRunning}
          runCode={runCode}
          stopCode={stopCode}
          saveCode={saveCode}
          shareCode={shareCode}
          viewMode={viewMode}
          setViewMode={setViewMode}
          onTemplatesToggle={handleTemplatesToggle}
        />

        {/* Main Content */}
        <div className="flex-1 p-4 overflow-hidden">
          <AnimatePresence>
            {showTemplates && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
                onClick={(e) => e.target === e.currentTarget && setShowTemplates(false)}
              >
                <div className="w-full max-w-6xl max-h-[80vh] overflow-hidden">
                  <TemplatesLibrary
                    onSelectTemplate={handleTemplateSelect}
                    onClose={() => setShowTemplates(false)}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <PlaygroundLayout
            viewMode={viewMode}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            code={code}
            setCode={setCode}
            language={language}
            theme={theme}
            output={output}
            isRunning={isRunning}
          />
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default PlaygroundPage;