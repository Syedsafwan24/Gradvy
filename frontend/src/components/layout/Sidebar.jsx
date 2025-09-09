'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useSelector } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  User, 
  Settings, 
  Shield, 
  Menu, 
  X, 
  ChevronLeft,
  Brain,
  BarChart3,
  BookOpen,
  Users,
  Sliders
} from 'lucide-react';
import { selectCurrentUser } from '../../store/slices/authSlice';

const Sidebar = ({ isCollapsed, onToggle }) => {
  const user = useSelector(selectCurrentUser);
  const pathname = usePathname();

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Overview and analytics'
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: User,
      description: 'Manage your account',
      subItems: [
        {
          name: 'Overview',
          href: '/profile',
          description: 'Profile summary'
        },
        {
          name: 'Personal Info',
          href: '/profile/info',
          description: 'Edit details'
        },
        {
          name: 'Actions',
          href: '/profile/actions',
          description: 'Account actions'
        }
      ]
    },
    {
      name: 'Preferences',
      href: '/preferences',
      icon: Sliders,
      description: 'Learning preferences'
    },
    {
      name: 'Learning',
      href: '/learning',
      icon: BookOpen,
      description: 'Courses and progress'
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Learning insights'
    },
    {
      name: 'Community',
      href: '/community',
      icon: Users,
      description: 'Connect with learners'
    }
  ];

  const settingsItems = [
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'Account preferences',
      subItems: [
        {
          name: 'General',
          href: '/settings',
          description: 'Basic settings'
        },
        {
          name: 'Security',
          href: '/settings/security',
          description: 'Password & 2FA'
        },
        {
          name: 'Privacy',
          href: '/settings/privacy',
          description: 'Data settings'
        },
        {
          name: 'Account',
          href: '/settings/account',
          description: 'Account management'
        }
      ]
    }
  ];

  const isActive = (href) => {
    return pathname === href;
  };

  const isExactActive = (href) => {
    return pathname === href;
  };

  const hasActiveChild = (item) => {
    if (!item.subItems) return false;
    return item.subItems.some(subItem => isExactActive(subItem.href));
  };

  const NavItem = ({ item, isLast = false }) => {
    const Icon = item.icon;
    const active = isExactActive(item.href);
    const hasActiveSubItem = hasActiveChild(item);
    const showSubItems = !isCollapsed && (active || hasActiveSubItem) && item.subItems;

    return (
      <div className={!isLast ? 'mb-1' : ''}>
        <Link href={item.href}>
          <motion.div
            whileHover={{ x: 1 }}
            className={`group relative flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-100 ${
              active
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : hasActiveSubItem
                ? 'bg-blue-50 text-blue-600 border border-blue-100'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`}
          >
            <Icon className={`flex-shrink-0 ${isCollapsed ? 'w-5 h-5' : 'w-5 h-5 mr-3'} ${
              active
                ? 'text-blue-600'
                : hasActiveSubItem
                ? 'text-blue-500'
                : 'text-gray-500 group-hover:text-gray-700'
            }`} />
            
            <AnimatePresence>
              {!isCollapsed && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{ duration: 0.1 }}
                  className="flex flex-col overflow-hidden"
                >
                  <span className="truncate">{item.name}</span>
                  <span className="text-xs text-gray-500 truncate">{item.description}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {active && (
              <motion.div
                layoutId="activeIndicator"
                className="absolute right-2 w-2 h-2 bg-blue-600 rounded-full"
              />
            )}
            {hasActiveSubItem && !active && (
              <div className="absolute right-2 w-1.5 h-1.5 bg-blue-400 rounded-full" />
            )}
          </motion.div>
        </Link>

        {/* Sub Items */}
        <AnimatePresence>
          {showSubItems && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.1 }}
              className="ml-4 mt-1 space-y-0.5 overflow-hidden"
            >
              {item.subItems.map((subItem, index) => {
                const subActive = isExactActive(subItem.href);
                return (
                  <Link key={subItem.href} href={subItem.href}>
                    <div
                      className={`relative flex items-center px-3 py-2 text-sm rounded-md transition-all duration-100 ${
                        subActive
                          ? 'bg-blue-100 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <span className="text-sm">{subItem.name}</span>
                      {subActive && (
                        <div className="absolute right-2 w-1.5 h-1.5 bg-blue-600 rounded-full" />
                      )}
                    </div>
                  </Link>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  return (
    <motion.div
      animate={{ width: isCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-2"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Gradvy</span>
            </motion.div>
          )}
        </AnimatePresence>
        
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
        >
          {isCollapsed ? (
            <Menu className="h-5 w-5 text-gray-600" />
          ) : (
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-sm font-semibold text-blue-700">
              {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </span>
          </div>
          
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2 }}
                className="flex-1 min-w-0 overflow-hidden"
              >
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.first_name && user?.last_name 
                    ? `${user.first_name} ${user.last_name}`
                    : user?.email || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.email}
                </p>
                {user?.is_mfa_enabled && (
                  <div className="flex items-center mt-1">
                    <Shield className="h-3 w-3 text-green-600 mr-1" />
                    <span className="text-xs text-green-600">2FA Active</span>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-6">
        {/* Main Navigation */}
        <div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.h3
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3"
              >
                Navigation
              </motion.h3>
            )}
          </AnimatePresence>
          
          <div className="space-y-1">
            {navigationItems.map((item, index) => (
              <NavItem 
                key={item.href} 
                item={item} 
                isLast={index === navigationItems.length - 1}
              />
            ))}
          </div>
        </div>

        {/* Settings */}
        <div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.h3
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3"
              >
                Settings
              </motion.h3>
            )}
          </AnimatePresence>
          
          <div className="space-y-1">
            {settingsItems.map((item, index) => (
              <NavItem 
                key={item.href} 
                item={item} 
                isLast={index === settingsItems.length - 1}
              />
            ))}
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="text-center"
            >
              <p className="text-xs text-gray-500">
                Gradvy v1.0
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default Sidebar;