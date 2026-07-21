import React from 'react';
import { 
  Mic, 
  Brain, 
  Timer, 
  FileText, 
  Languages, 
  Activity 
} from 'lucide-react';
import { StatCard } from './StatCard';
import { RecentActivity } from './RecentActivity';
import { QuickActions } from './QuickActions';

export const Dashboard: React.FC = () => {
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  const stats = [
    { title: 'Meeting Status', value: 'Idle', description: 'Waiting to start', icon: Mic },
    { title: 'Speech Model', value: 'Whisper Small', description: 'Local AI Model', icon: Brain },
    { title: 'Latency', value: '0 ms', description: 'Average Response', icon: Timer },
    { title: 'Words Processed', value: '0', description: 'Current Session', icon: FileText },
    { title: 'Language', value: 'English', description: 'Detected Language', icon: Languages },
    { title: 'System Health', value: 'Excellent', description: 'Everything operational', icon: Activity },
  ];

  return (
    <div className="flex flex-col gap-8">
      {/* Header Section */}
      <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">Monitor your meeting transcription system in real time.</p>
        </div>
        <div className="flex items-center rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm">
          {currentDate}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            description={stat.description}
            Icon={stat.icon}
          />
        ))}
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentActivity />
        </div>
        <div className="lg:col-span-1">
          <QuickActions />
        </div>
      </div>
    </div>
  );
};