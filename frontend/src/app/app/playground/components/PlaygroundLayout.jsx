// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/playground/components/PlaygroundLayout.jsx
// Layout component managing different view modes for the playground
// Extracted from massive PlaygroundPage component for better maintainability  
// RELEVANT FILES: PlaygroundPage.jsx, PlaygroundToolbar.jsx, CodeEditor.jsx, PreviewPanel.jsx

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CodeEditor from '@/components/playground/CodeEditor';
import PreviewPanel from '@/components/playground/PreviewPanel';
import ConsolePanel from '@/components/playground/ConsolePanel';

const PlaygroundLayout = ({
  viewMode,
  activeTab,
  setActiveTab,
  code,
  setCode,
  language,
  theme,
  output,
  isRunning
}) => {
  const layoutVariants = {
    editor: {
      gridTemplateColumns: '1fr',
    },
    preview: {
      gridTemplateColumns: '1fr',
    },
    split: {
      gridTemplateColumns: '1fr 1fr',
    }
  };

  const renderEditor = () => (
    <Card className="h-full overflow-hidden">
      <CodeEditor
        code={code}
        onChange={setCode}
        language={language}
        theme={theme}
        className="h-full"
      />
    </Card>
  );

  const renderPreview = () => (
    <Card className="h-full overflow-hidden">
      <div className="h-full flex flex-col">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-2 shrink-0">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="console">Console</TabsTrigger>
          </TabsList>
          
          <TabsContent value="preview" className="flex-1 overflow-hidden">
            <PreviewPanel 
              code={code} 
              language={language}
              isRunning={isRunning}
            />
          </TabsContent>
          
          <TabsContent value="console" className="flex-1 overflow-hidden">
            <ConsolePanel 
              output={output}
              isRunning={isRunning}
            />
          </TabsContent>
        </Tabs>
      </div>
    </Card>
  );

  if (viewMode === 'editor') {
    return (
      <motion.div 
        className="h-full"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {renderEditor()}
      </motion.div>
    );
  }

  if (viewMode === 'preview') {
    return (
      <motion.div 
        className="h-full"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {renderPreview()}
      </motion.div>
    );
  }

  // Split view (default)
  return (
    <motion.div 
      className="grid gap-4 h-full"
      style={{ gridTemplateColumns: '1fr 1fr' }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key="editor"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -20, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="h-full"
        >
          {renderEditor()}
        </motion.div>
      </AnimatePresence>

      <AnimatePresence mode="wait">
        <motion.div
          key="preview"
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 20, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="h-full"
        >
          {renderPreview()}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

export default PlaygroundLayout;