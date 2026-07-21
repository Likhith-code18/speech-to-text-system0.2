import React from 'react';
import { Mic, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 flex h-16 w-full shrink-0 items-center border-b border-gray-100 bg-white/80 px-6 backdrop-blur-md">
      <div className="flex flex-1 items-center justify-between">
        
        {/* Logo & Branding */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-green-500/10 text-green-600 shadow-sm border border-green-500/20">
            <Mic className="h-5 w-5" />
          </div>
          <div className="flex flex-col justify-center">
            <span className="text-base font-semibold tracking-tight text-slate-900 leading-tight">
              EchoNote AI
            </span>
            <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
              Real-Time Meeting Intelligence
            </span>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2 rounded-full border border-green-100 bg-green-50 px-3 py-1">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
            </span>
            <span className="text-xs font-medium text-green-700">
              System Online
            </span>
          </div>
          
          <div className="h-4 w-px bg-gray-200" />
          
          <motion.button 
            whileHover={{ scale: 1.05, rotate: 15 }}
            whileTap={{ scale: 0.95 }}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-gray-50 hover:text-slate-900"
          >
            <Settings className="h-5 w-5" />
          </motion.button>
        </div>

      </div>
    </header>
  );
};