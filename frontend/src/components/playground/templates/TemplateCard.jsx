// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/playground/templates/TemplateCard.jsx
// Individual template card component with preview and selection functionality
// Extracted from massive TemplatesLibrary component for better maintainability
// RELEVANT FILES: TemplateGrid.jsx, TemplatesLibrary.jsx, TemplateFilters.jsx

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Code, 
  Globe, 
  Palette, 
  Smartphone, 
  Database,
  Zap,
  Star,
  Copy,
  ExternalLink,
  Eye
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const TemplateCard = ({ template, onSelect }) => {
  const [showPreview, setShowPreview] = useState(false);

  const getLanguageIcon = (language) => {
    const icons = {
      javascript: Zap,
      python: Database,
      html: Globe,
      css: Palette,
      react: Smartphone
    };
    return icons[language] || Code;
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-red-100 text-red-800'
    };
    return colors[difficulty] || 'bg-gray-100 text-gray-800';
  };

  const getLanguageColor = (language) => {
    const colors = {
      javascript: 'bg-yellow-500',
      python: 'bg-blue-500',
      html: 'bg-orange-500',
      css: 'bg-purple-500',
      react: 'bg-blue-600'
    };
    return colors[language] || 'bg-gray-500';
  };

  const LanguageIcon = getLanguageIcon(template.language);

  const handleSelect = () => {
    onSelect(template);
  };

  const copyToClipboard = async (e) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(template.code);
      // Could show toast notification here
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="group"
    >
      <Card className="h-full overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer border-gray-200">
        <div className="relative">
          {/* Header with language indicator */}
          <div className="p-4 pb-0">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getLanguageColor(template.language)}`}></div>
                <LanguageIcon className="h-4 w-4 text-gray-600" />
                <span className="text-sm text-gray-600 capitalize">{template.language}</span>
              </div>
              
              {template.difficulty && (
                <Badge className={getDifficultyColor(template.difficulty)}>
                  {template.difficulty}
                </Badge>
              )}
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
              {template.name}
            </h3>
            
            {template.description && (
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {template.description}
              </p>
            )}

            {/* Tags */}
            {template.tags && template.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {template.tags.slice(0, 3).map(tag => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {template.tags.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{template.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}

            {/* Footer Actions */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyToClipboard}
                  className="h-8 w-8 p-0"
                >
                  <Copy className="h-3 w-3" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowPreview(!showPreview);
                  }}
                  className="h-8 w-8 p-0"
                >
                  <Eye className="h-3 w-3" />
                </Button>
              </div>

              <Button 
                onClick={handleSelect}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700"
              >
                Use Template
              </Button>
            </div>
          </div>

          {/* Code Preview */}
          {showPreview && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t bg-gray-50 p-3"
            >
              <pre className="text-xs text-gray-700 overflow-x-auto max-h-32 overflow-y-auto">
                <code>{template.code.substring(0, 200)}...</code>
              </pre>
            </motion.div>
          )}
        </div>
      </Card>
    </motion.div>
  );
};

export default TemplateCard;