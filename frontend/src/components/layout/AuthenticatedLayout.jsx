'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { usePathname } from 'next/navigation';
import { selectIsAuthenticated } from '@/store/slices/authSlice';
import Navbar from './Navbar';
import Footer from './Footer';

const AuthenticatedLayout = ({ children }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const pathname = usePathname();

  // Check if we're on an app route
  const isAppRoute = pathname.startsWith('/app');
  
  // Check if we're on the home page
  const isHomePage = pathname === '/';

  // For app routes, just pass through children (app layout handles the sidebar)
  if (isAppRoute) {
    return <>{children}</>;
  }

  // For home page, always show navbar layout (regardless of auth status)
  if (isHomePage) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </div>
    );
  }

  // For all other routes (public pages), show navbar + footer layout
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
};

export default AuthenticatedLayout;