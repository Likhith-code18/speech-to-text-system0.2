import React from 'react';
import { motion } from 'framer-motion';
import { Play, History, Settings } from 'lucide-react';

const actions = [
  {
    id: 'start',
    label: 'Start Meeting',
    icon: Play,
    primary: true,
  },
  {
    id: 'history',
    label: 'Open History',
    icon: History,
    primary: false,
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    primary: false,
  },
];

export const QuickActions: React.FC = () => {
  return (
    <div className="flex flex-col rounded-2xl border border-gray-100 bg-white p-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
      <h3 className="mb-6 text-lg font-semibold tracking-tight text-slate-900">Quick Actions</h3>
      
      <div className="flex flex-col gap-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                action.primary
                  ? 'bg-green-500 text-white shadow-sm hover:bg-green-600'
                  : 'border border-gray-200 bg-white text-slate-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="h-4 w-4" />
              {action.label}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};