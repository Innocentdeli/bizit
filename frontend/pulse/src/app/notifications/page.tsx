'use client';

import React from 'react';
import { Bell, TrendingUp, AlertTriangle, Briefcase, ChevronRight } from 'lucide-react';

const NOTIFICATIONS = [
    {
        id: 1,
        type: 'MARKET_ALERT',
        title: 'Demand Spike in Yaba',
        message: 'Tech co-working searches up 45% in your saved zone.',
        time: '2 hours ago',
        icon: TrendingUp,
        color: 'text-green-600',
        bg: 'bg-green-100'
    },
    {
        id: 2,
        type: 'COMPETITOR',
        title: 'New Entrant Alert',
        message: 'A new logistics hub just registered within 2km of your business.',
        time: '1 day ago',
        icon: AlertTriangle,
        color: 'text-orange-600',
        bg: 'bg-orange-100'
    },
    {
        id: 3,
        type: 'OPPORTUNITY',
        title: 'Underserved Market Gap',
        message: 'High demand for "Late Night Food" detected. Review data?',
        time: '2 days ago',
        icon: Briefcase,
        color: 'text-blue-600',
        bg: 'bg-blue-100'
    }
];

export default function NotificationsPage() {
    return (
        <div className="max-w-3xl mx-auto space-y-6 pb-20">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                    <Bell className="text-bizit-green" />
                    Pulse Alerts
                </h1>
                <button className="text-xs text-bizit-gray hover:text-bizit-dark">Mark all as read</button>
            </div>

            <div className="space-y-3">
                {NOTIFICATIONS.map((n) => (
                    <div key={n.id} className="p-4 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm hover:shadow-md transition-shadow flex items-start gap-4 cursor-pointer group">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${n.bg} ${n.color}`}>
                            <n.icon size={20} />
                        </div>
                        <div className="flex-1">
                            <div className="flex justify-between items-start">
                                <h3 className="font-bold text-sm text-bizit-dark group-hover:text-bizit-green transition-colors">{n.title}</h3>
                                <span className="text-[10px] text-bizit-gray">{n.time}</span>
                            </div>
                            <p className="text-xs text-bizit-dark/70 mt-1">{n.message}</p>
                        </div>
                        <ChevronRight size={16} className="text-gray-300 self-center group-hover:text-bizit-green" />
                    </div>
                ))}
            </div>

            <div className="text-center p-8 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                <p className="text-sm text-bizit-gray">That's all for now. We'll alert you when the market shifts.</p>
            </div>
        </div>
    );
}
