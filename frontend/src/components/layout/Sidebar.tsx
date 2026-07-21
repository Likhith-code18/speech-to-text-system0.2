import React, { useState } from 'react';
import { LayoutDashboard, Radio, History, Settings, Info } from 'lucide-react';
import { motion } from 'framer-motion';

type NavItem = {
  id: string;
  label: string;
  icon: React.ElementType;
};

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'live', label: 'Live Meeting', icon: Radio },
  { id: 'history', label: 'History', icon: History },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'about', label: 'About', icon: Info },
];

export const Sidebar: React.FC = () => {
  const [activeItem, setActiveItem] = useState<string>('dashboard');

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-gray-100 bg-white shadow-[1px_0_2px_rgba(0,0,0,0.02)]">
      <div className="flex h-16 shrink-0 items-center px-6">
        <span className="text-sm font-semibold tracking-wider text-slate-400 uppercase">
          Menu
        </span>
      </div>
      
      <nav className="flex-1 space-y-1 px-3 py-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={() => setActiveItem(item.id)}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
              className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-green-50 text-green-700' 
                  : 'text-slate-600 hover:bg-gray-50 hover:text-slate-900'
              }`}
            >
              <Icon 
                className={`h-5 w-5 transition-colors ${
                  isActive ? 'text-green-600' : 'text-slate-400 group-hover:text-slate-600'
                }`} 
              />
              {item.label}
              
              {isActive && (
                <motion.div
                  layoutId="active-pill"
                  className="absolute inset-0 rounded-xl border border-green-200/50 pointer-events-none"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </motion.button>
          );
        })}
      </nav>

      <div className="border-t border-gray-100 p-4">
        <div className="flex items-center gap-3 rounded-xl bg-gray-50 p-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm border border-gray-200">
            <span className="text-xs font-bold text-slate-700">EN</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-slate-900">Workspace</span>
            <span className="text-[10px] text-slate-500">Free Plan</span>
          </div>
        </div>
      </div>
    </aside>
  );
};