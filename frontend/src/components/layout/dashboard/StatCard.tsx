import React from 'react';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  description: string;
  Icon: LucideIcon;
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, description, Icon }) => {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="flex flex-col rounded-2xl border border-gray-100 bg-white p-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)] transition-shadow hover:shadow-[0_8px_30px_rgba(0,0,0,0.04)]"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-500">{title}</h3>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50 text-green-600">
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-4 flex flex-col gap-1">
        <span className="text-2xl font-semibold tracking-tight text-slate-900">{value}</span>
        <span className="text-xs font-medium text-slate-400">{description}</span>
      </div>
    </motion.div>
  );
};