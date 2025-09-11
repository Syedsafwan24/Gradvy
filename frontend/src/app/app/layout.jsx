'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import { selectIsAuthenticated } from '@/store/slices/authSlice';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';

export default function AppLayout({ children }) {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Redirect to login if not authenticated when accessing app routes
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Show loading or redirect if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // App layout with sidebar
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <div className="h-6 w-px bg-sidebar-border" />
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">Gradvy</span>
            </div>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}