// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/components/playground/templates/TemplateGrid.jsx
// Grid component for displaying template cards in organized layout
// Extracted from massive TemplatesLibrary component for better maintainability
// RELEVANT FILES: TemplatesLibrary.jsx, TemplateCard.jsx, TemplateFilters.jsx

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import TemplateCard from './TemplateCard';

const TemplateGrid = ({ templates, onSelectTemplate, searchTerm, selectedCategory }) => {
  // Filter templates based on search and category
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || 
                           template.category === selectedCategory ||
                           template.language === selectedCategory ||
                           template.difficulty === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  if (filteredTemplates.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="text-gray-400 mb-4">
          <svg className="h-16 w-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
        <p className="text-gray-500">Try adjusting your search criteria or browse different categories.</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      {filteredTemplates.map((template, index) => (
        <motion.div
          key={template.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <TemplateCard
            template={template}
            onSelect={onSelectTemplate}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};

export default TemplateGrid;