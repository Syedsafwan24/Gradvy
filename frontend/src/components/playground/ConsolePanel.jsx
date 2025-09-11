'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Trash2, Copy, Download, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const ConsolePanel = ({ output = [], onClear, fontSize = 12 }) => {
  const [filter, setFilter] = useState('all'); // 'all', 'logs', 'errors', 'warnings'
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const consoleRef = useRef(null);
  const endRef = useRef(null);

  // Auto-scroll to bottom when new output arrives
  useEffect(() => {
    if (isAutoScroll && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [output, isAutoScroll]);

  const handleScroll = () => {
    if (consoleRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = consoleRef.current;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
      setIsAutoScroll(isAtBottom);
    }
  };

  const formatOutput = (outputArray) => {
    if (!Array.isArray(outputArray)) {
      return typeof outputArray === 'string' ? outputArray : JSON.stringify(outputArray, null, 2);
    }

    return outputArray
      .filter(item => {
        if (filter === 'all') return true;
        if (filter === 'logs') return item.type === 'log';
        if (filter === 'errors') return item.type === 'error';
        if (filter === 'warnings') return item.type === 'warn';
        return true;
      })
      .map((item, index) => ({
        ...item,
        id: index,
        timestamp: item.timestamp || new Date().toLocaleTimeString()
      }));
  };

  const getLineIcon = (type) => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warn':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📝';
    }
  };

  const getLineClass = (type) => {
    switch (type) {
      case 'error':
        return 'text-red-600 bg-red-50';
      case 'warn':
        return 'text-amber-600 bg-amber-50';
      case 'info':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-700 bg-gray-50';
    }
  };

  const copyToClipboard = () => {
    const formattedOutput = formatOutput(output);
    const text = formattedOutput.map(item => 
      `[${item.timestamp}] ${item.message}`
    ).join('\n');
    
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
    });
  };

  const downloadLogs = () => {
    const formattedOutput = formatOutput(output);
    const content = formattedOutput.map(item => 
      `[${item.timestamp}] ${getLineIcon(item.type)} ${item.message}`
    ).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `console-logs-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formattedOutput = formatOutput(output);
  const hasOutput = formattedOutput.length > 0;

  const getFilterCount = (filterType) => {
    if (!Array.isArray(output)) return 0;
    if (filterType === 'all') return output.length;
    return output.filter(item => item.type === filterType).length;
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100">
      {/* Console Header */}
      <div className="flex items-center justify-between p-2 border-b border-slate-700 bg-slate-800">
        <div className="flex items-center space-x-2">
          <Terminal className="h-4 w-4 text-green-400" />
          <span className="text-sm font-medium">Console</span>
          {hasOutput && (
            <Badge variant="secondary" className="text-xs">
              {formattedOutput.length} lines
            </Badge>
          )}
        </div>

        <div className="flex items-center space-x-1">
          {/* Filter Buttons */}
          <div className="flex items-center space-x-1 mr-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                filter === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              All ({getFilterCount('all')})
            </button>
            <button
              onClick={() => setFilter('logs')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                filter === 'logs' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Logs ({getFilterCount('log')})
            </button>
            <button
              onClick={() => setFilter('errors')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                filter === 'errors' 
                  ? 'bg-red-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Errors ({getFilterCount('error')})
            </button>
            <button
              onClick={() => setFilter('warnings')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                filter === 'warnings' 
                  ? 'bg-amber-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Warnings ({getFilterCount('warn')})
            </button>
          </div>

          {/* Action Buttons */}
          <Button
            variant="ghost"
            size="sm"
            onClick={copyToClipboard}
            disabled={!hasOutput}
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-100"
          >
            <Copy className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={downloadLogs}
            disabled={!hasOutput}
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-100"
          >
            <Download className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            disabled={!hasOutput}
            className="h-7 w-7 p-0 text-slate-400 hover:text-red-400"
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Console Content */}
      <div 
        ref={consoleRef}
        className="flex-1 overflow-auto p-2 space-y-1"
        onScroll={handleScroll}
        style={{ fontSize: `${fontSize}px` }}
      >
        {!hasOutput ? (
          <div className="flex items-center justify-center h-full text-slate-500">
            <div className="text-center">
              <Terminal className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Console output will appear here...</p>
              <p className="text-xs mt-1">Run your code to see logs, errors, and output.</p>
            </div>
          </div>
        ) : (
          <>
            {formattedOutput.map((item) => (
              <div
                key={item.id}
                className={`flex items-start space-x-2 p-2 rounded text-sm font-mono ${
                  item.type === 'error' 
                    ? 'bg-red-900/20 border-l-2 border-red-500' 
                    : item.type === 'warn'
                    ? 'bg-amber-900/20 border-l-2 border-amber-500'
                    : item.type === 'info'
                    ? 'bg-blue-900/20 border-l-2 border-blue-500'
                    : 'bg-slate-800/50 border-l-2 border-green-500'
                }`}
              >
                <span className="flex-shrink-0 text-xs opacity-60">
                  {item.timestamp}
                </span>
                <span className="flex-shrink-0">
                  {getLineIcon(item.type)}
                </span>
                <div className="flex-1 whitespace-pre-wrap break-words">
                  {typeof item.message === 'object' 
                    ? JSON.stringify(item.message, null, 2)
                    : item.message
                  }
                </div>
              </div>
            ))}
            <div ref={endRef} />
          </>
        )}
      </div>

      {/* Auto-scroll Indicator */}
      {!isAutoScroll && hasOutput && (
        <div className="px-2 py-1 bg-slate-800 border-t border-slate-700">
          <button
            onClick={() => {
              setIsAutoScroll(true);
              endRef.current?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            ↓ Scroll to bottom
          </button>
        </div>
      )}
    </div>
  );
};

export default ConsolePanel;