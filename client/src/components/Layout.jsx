import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import { Separator } from "@/components/ui/separator";

function Layout({ children }) {
  return (
    <div className="flex flex-col h-screen">
      {/* Sticky Header */}
      <div className="sticky top-0 z-50">
        <Header />
      </div>
      
      <div className="flex flex-row flex-1 overflow-hidden">
        {/* Sticky Sidebar */}
        <div className="sticky top-0 h-screen">
          <Sidebar className="h-full bg-gray-800 text-white" />
        </div>

        {/* Vertical Separator */}
        <Separator orientation="vertical" className="bg-black py-4" />

        {/* Main Content Area */}
        <div className="flex-1 overflow-auto p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

export default Layout;
