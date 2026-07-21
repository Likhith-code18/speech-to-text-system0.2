import React from 'react';
import { PlayCircle, Mic, MicOff, CheckCircle } from 'lucide-react';

const activities = [
  {
    id: 1,
    title: 'Application Started',
    time: 'Just now',
    icon: PlayCircle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
  },
  {
    id: 2,
    title: 'Waiting for microphone',
    time: '2 mins ago',
    icon: Mic,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50',
  },
  {
    id: 3,
    title: 'No active meeting',
    time: '5 mins ago',
    icon: MicOff,
    color: 'text-slate-400',
    bgColor: 'bg-slate-50',
  },
  {
    id: 4,
    title: 'Ready for transcription',
    time: '10 mins ago',
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-50',
  },
];

export const RecentActivity: React.FC = () => {
  return (
    <div className="flex h-full flex-col rounded-2xl border border-gray-100 bg-white p-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
      <h3 className="mb-6 text-lg font-semibold tracking-tight text-slate-900">Recent Activity</h3>
      
      <div className="relative flex-1">
        <div className="absolute bottom-0 left-[19px] top-2 w-px bg-gray-100" />
        
        <div className="space-y-6">
          {activities.map((activity) => {
            const Icon = activity.icon;
            return (
              <div key={activity.id} className="relative flex gap-4">
                <div className={`relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-4 border-white ${activity.bgColor} ${activity.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex flex-col pt-2">
                  <span className="text-sm font-medium text-slate-900">{activity.title}</span>
                  <span className="text-xs text-slate-500">{activity.time}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};