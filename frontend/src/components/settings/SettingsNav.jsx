'use client';

import React from 'react';
import { Settings, Shield, Eye, User, ChevronRight } from 'lucide-react';

const SettingsNav = ({ activeTab, onTabChange }) => {
  const navItems = [
    {
      id: 'general',
      label: 'General',
      icon: Settings,
      description: 'Profile and preferences',
      shortDesc: 'Profile'
    },
    {
      id: 'security',
      label: 'Security',
      icon: Shield,
      description: 'Password and 2FA',
      shortDesc: '2FA & Password'
    },
    {
      id: 'privacy',
      label: 'Privacy',
      icon: Eye,
      description: 'Data and permissions',
      shortDesc: 'Data & Privacy'
    },
    {
      id: 'account',
      label: 'Account',
      icon: User,
      description: 'Account management',
      shortDesc: 'Account'
    }
  ];

  return (
    <>
      {/* Mobile horizontal navigation */}
      <div className="lg:hidden">
        <div className="border-b border-gray-200 mb-4">
          <nav className="flex space-x-0 overflow-x-auto scrollbar-hide">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`
                    flex-shrink-0 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                    min-w-max flex items-center space-x-2
                    ${isActive 
                      ? 'border-blue-500 text-blue-600 bg-blue-50' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                  <span className="hidden sm:inline">{item.label}</span>
                  <span className="sm:hidden">{item.shortDesc}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop vertical navigation */}
      <nav className="hidden lg:block space-y-1 p-4">
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Settings
          </h3>
        </div>
        
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`
                w-full text-left px-3 py-3 rounded-lg transition-all duration-200
                flex items-center justify-between group relative
                ${isActive 
                  ? 'bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-200' 
                  : 'hover:bg-gray-50 text-gray-700 hover:text-gray-900 hover:shadow-sm'
                }
              `}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <div className={`
                  flex-shrink-0 p-1.5 rounded-md transition-colors
                  ${isActive ? 'bg-blue-100' : 'bg-gray-100 group-hover:bg-gray-200'}
                `}>
                  <Icon className={`h-4 w-4 ${
                    isActive ? 'text-blue-600' : 'text-gray-500 group-hover:text-gray-600'
                  }`} />
                </div>
                <div className="text-left min-w-0 flex-1">
                  <div className={`font-medium text-sm truncate ${
                    isActive ? 'text-blue-900' : 'text-gray-900'
                  }`}>
                    {item.label}
                  </div>
                  <div className={`text-xs truncate ${
                    isActive ? 'text-blue-600' : 'text-gray-500'
                  }`}>
                    {item.description}
                  </div>
                </div>
              </div>
              
              <ChevronRight 
                className={`h-4 w-4 transition-all duration-200 flex-shrink-0 ${
                  isActive 
                    ? 'text-blue-500 translate-x-0.5' 
                    : 'text-gray-400 group-hover:text-gray-500 group-hover:translate-x-0.5'
                }`} 
              />
              
              {/* Active indicator */}
              {isActive && (
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-blue-500 rounded-r-full" />
              )}
            </button>
          );
        })}
        
        {/* Bottom section with divider */}
        <div className="pt-4 mt-6 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center px-3">
            <p>Need help?</p>
            <button className="text-blue-600 hover:text-blue-700 font-medium mt-1">
              Contact Support
            </button>
          </div>
        </div>
      </nav>
    </>
  );
};

export default SettingsNav;