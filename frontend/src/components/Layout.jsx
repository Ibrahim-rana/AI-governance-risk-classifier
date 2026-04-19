import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, FileText, Settings } from 'lucide-react';

const Layout = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'New Assessment', href: '/assessment', icon: ShieldCheck },
    { name: 'Documents', href: '/documents', icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-slate-200 flex flex-col hidden md:flex">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <ShieldCheck className="h-6 w-6 text-primary-600 mr-3" />
          <span className="font-bold text-slate-900 text-lg">AI Risk Classifier</span>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={`flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <item.icon
                  className={`flex-shrink-0 -ml-1 mr-3 h-5 w-5 ${
                    isActive ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-500'
                  }`}
                  aria-hidden="true"
                />
                {item.name}
              </NavLink>
            );
          })}
        </nav>
        
        <div className="p-4 border-t border-slate-200">
          <button className="flex items-center w-full px-3 py-2 text-sm font-medium text-slate-600 rounded-md hover:bg-slate-50 hover:text-slate-900">
            <Settings className="flex-shrink-0 -ml-1 mr-3 h-5 w-5 text-slate-400" />
            Settings
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <div className="md:hidden h-16 bg-white border-b border-slate-200 flex items-center px-4">
          <ShieldCheck className="h-6 w-6 text-primary-600 mr-3" />
          <span className="font-bold text-slate-900 text-lg">AI Risk Classifier</span>
        </div>

        <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
