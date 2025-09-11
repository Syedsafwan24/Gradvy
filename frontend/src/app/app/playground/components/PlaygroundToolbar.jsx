// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/playground/components/PlaygroundToolbar.jsx
// Toolbar component for playground editor controls and actions
// Extracted from massive PlaygroundPage component for better maintainability
// RELEVANT FILES: PlaygroundPage.jsx, PlaygroundTemplates.js, CodeEditor.jsx, ConsolePanel.jsx

'use client';

import React from 'react';
import { 
  Play, 
  Square, 
  Save, 
  Share2, 
  Download, 
  Upload, 
  Settings,
  Eye,
  Split,
  Maximize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

const PlaygroundToolbar = ({
  language,
  setLanguage,
  theme,
  setTheme,
  isRunning,
  runCode,
  stopCode,
  saveCode,
  shareCode,
  viewMode,
  setViewMode,
  onTemplatesToggle
}) => {
  const languages = [
    { value: 'javascript', label: 'JavaScript', color: 'bg-yellow-500' },
    { value: 'python', label: 'Python', color: 'bg-blue-500' },
    { value: 'html', label: 'HTML', color: 'bg-orange-500' },
    { value: 'css', label: 'CSS', color: 'bg-purple-500' },
    { value: 'typescript', label: 'TypeScript', color: 'bg-blue-600' },
    { value: 'java', label: 'Java', color: 'bg-red-500' }
  ];

  const themes = [
    { value: 'vs-dark', label: 'Dark' },
    { value: 'light', label: 'Light' },
    { value: 'hc-black', label: 'High Contrast' }
  ];

  const getCurrentLanguage = () => {
    return languages.find(lang => lang.value === language) || languages[0];
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 border-b">
      {/* Left side - Language and Theme */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${getCurrentLanguage().color}`}></div>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languages.map(lang => (
                <SelectItem key={lang.value} value={lang.value}>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${lang.color}`}></div>
                    <span>{lang.label}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Select value={theme} onValueChange={setTheme}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Theme" />
          </SelectTrigger>
          <SelectContent>
            {themes.map(theme => (
              <SelectItem key={theme.value} value={theme.value}>
                {theme.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Center - Run Controls */}
      <div className="flex items-center space-x-2">
        {!isRunning ? (
          <Button onClick={runCode} className="bg-green-600 hover:bg-green-700">
            <Play className="h-4 w-4 mr-2" />
            Run
          </Button>
        ) : (
          <Button onClick={stopCode} variant="destructive">
            <Square className="h-4 w-4 mr-2" />
            Stop
          </Button>
        )}
        
        <div className="h-6 w-px bg-gray-300 mx-2" />
        
        <Button variant="outline" size="sm" onClick={saveCode}>
          <Save className="h-4 w-4 mr-2" />
          Save
        </Button>
        
        <Button variant="outline" size="sm" onClick={shareCode}>
          <Share2 className="h-4 w-4 mr-2" />
          Share
        </Button>
      </div>

      {/* Right side - View Controls */}
      <div className="flex items-center space-x-2">
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <Button
            variant={viewMode === 'editor' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('editor')}
            className="h-8"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'split' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('split')}
            className="h-8"
          >
            <Split className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'preview' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('preview')}
            className="h-8"
          >
            <Eye className="h-4 w-4" />
          </Button>
        </div>

        <Button variant="outline" size="sm" onClick={onTemplatesToggle}>
          Templates
        </Button>

        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
        
        <Button variant="outline" size="sm">
          <Upload className="h-4 w-4 mr-2" />
          Import
        </Button>
      </div>
    </div>
  );
};

export default PlaygroundToolbar;