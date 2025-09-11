// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/playground/templates/TemplateFilters.jsx
// Search and category filtering controls for templates library
// Extracted from massive TemplatesLibrary component for better maintainability
// RELEVANT FILES: TemplateGrid.jsx, TemplateCard.jsx, TemplatesLibrary.jsx

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Code, 
  Globe, 
  Palette, 
  Smartphone, 
  Database,
  Zap,
  Star
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const TemplateFilters = ({ 
  searchTerm, 
  setSearchTerm, 
  selectedCategory, 
  setSelectedCategory,
  templateCounts = {}
}) => {
  const categories = [
    { id: 'all', name: 'All Templates', icon: Code, count: templateCounts.all || 0 },
    { id: 'javascript', name: 'JavaScript', icon: Zap, count: templateCounts.javascript || 0 },
    { id: 'python', name: 'Python', icon: Database, count: templateCounts.python || 0 },
    { id: 'html', name: 'HTML/CSS', icon: Globe, count: templateCounts.html || 0 },
    { id: 'react', name: 'React', icon: Smartphone, count: templateCounts.react || 0 },
    { id: 'beginner', name: 'Beginner', icon: Star, count: templateCounts.beginner || 0 }
  ];

  return (
    <div className="space-y-4 mb-6">
      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search templates..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </motion.div>

      {/* Category Filters */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-wrap gap-2"
      >
        {categories.map((category) => {
          const Icon = category.icon;
          const isSelected = selectedCategory === category.id;
          
          return (
            <Button
              key={category.id}
              variant={isSelected ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center space-x-2 ${
                isSelected 
                  ? 'bg-blue-600 hover:bg-blue-700' 
                  : 'hover:bg-gray-50'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{category.name}</span>
              {category.count > 0 && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  isSelected 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {category.count}
                </span>
              )}
            </Button>
          );
        })}
      </motion.div>
    </div>
  );
};

export default TemplateFilters;