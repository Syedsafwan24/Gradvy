import React from 'react';
import { cn } from '@/lib/utils';

/**
 * PageLayout - Consistent page wrapper with header
 * @param {string} title - Page title
 * @param {string} description - Page description
 * @param {React.ReactNode} children - Page content
 * @param {React.ReactNode} actions - Optional action buttons
 * @param {string} className - Additional CSS classes
 */
export const PageLayout = ({ 
  title, 
  description, 
  children, 
  actions,
  className 
}) => {
  return (
    <div className={cn('p-4 sm:p-6 lg:p-8', className)}>
      {/* Page Header */}
      {(title || actions) && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 sm:mb-8">
          {title && (
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
                {title}
              </h1>
              {description && (
                <p className="text-sm sm:text-base text-gray-600 mt-2 line-clamp-2">
                  {description}
                </p>
              )}
            </div>
          )}
          {actions && (
            <div className="flex gap-3 shrink-0">
              {actions}
            </div>
          )}
        </div>
      )}
      
      {/* Page Content */}
      {children}
    </div>
  );
};

export default PageLayout;
