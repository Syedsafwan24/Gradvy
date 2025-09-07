'use client';

import React from 'react';
import { Settings, Shield, Eye, User, ChevronRight } from 'lucide-react';

const SettingsNav = ({ activeTab, onTabChange }) => {
  const navItems = [
    {
      id: 'general',
      label: 'General',
      icon: Settings,
      description: 'Profile and preferences'
    },
    {
      id: 'security',
      label: 'Security',
      icon: Shield,
      description: 'Password and 2FA'
    },
    {
      id: 'privacy',
      label: 'Privacy',
      icon: Eye,
      description: 'Data and permissions'
    },
    {
      id: 'account',
      label: 'Account',
      icon: User,
      description: 'Account management'
    }
  ];

  return (
    <nav className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">
        Settings
      </h3>
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        
        return (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`
              w-full text-left px-4 py-3 rounded-lg transition-colors
              flex items-center justify-between group
              ${isActive 
                ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                : 'hover:bg-gray-50 text-gray-700 hover:text-gray-900'
              }
            `}
          >
            <div className="flex items-center space-x-3">
              <Icon className={`h-5 w-5 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
              <div className="text-left">
                <div className="font-medium text-sm">
                  {item.label}
                </div>
                <div className="text-xs text-gray-500">
                  {item.description}
                </div>
              </div>
            </div>
            <ChevronRight 
              className={`h-4 w-4 transition-transform ${
                isActive ? 'text-blue-600' : 'text-gray-400'
              } group-hover:translate-x-1`} 
            />
          </button>
        );
      })}
    </nav>
  );
};

export default SettingsNav;