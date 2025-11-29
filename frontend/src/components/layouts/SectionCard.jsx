import React from 'react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

/**
 * SectionCard - Consistent card wrapper for page sections
 * @param {string} title - Section title
 * @param {string} description - Section description
 * @param {React.ReactNode} children - Section content
 * @param {React.ReactNode} action - Optional action button/element
 * @param {string} className - Additional CSS classes for the card
 * @param {string} contentClassName - Additional CSS classes for the content wrapper
 */
export const SectionCard = ({ 
  title, 
  description, 
  children, 
  action,
  className,
  contentClassName 
}) => {
  return (
    <Card className={cn('p-4 sm:p-6 border border-gray-200 shadow-sm', className)}>
      {/* Section Header */}
      {(title || action) && (
        <div className="flex items-start justify-between mb-4">
          <div className="min-w-0 flex-1">
            {title && (
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 truncate">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {description}
              </p>
            )}
          </div>
          {action && (
            <div className="ml-4 shrink-0">
              {action}
            </div>
          )}
        </div>
      )}
      
      {/* Section Content */}
      <div className={cn(contentClassName)}>
        {children}
      </div>
    </Card>
  );
};

export default SectionCard;
