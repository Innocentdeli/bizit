'use client';

import React from 'react';
import { ShieldAlert, Users, Server, Activity, Lock } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

export default function AdminPage() {
    return (
        <div className="space-y-8 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <ShieldAlert className="text-red-600" />
                        Platform Administration
                    </h1>
                    <p className="text-bizit-gray text-sm">Restricted Access: Super Admin Only</p>
                </div>
                <div className="flex items-center gap-2 bg-red-50 text-red-600 px-3 py-1 rounded-full text-xs font-bold border border-red-100">
                    <Lock size={12} /> SECURE ZONE
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                    <div className="flex items-center gap-2 text-bizit-dark font-bold">
                        <Server size={18} className="text-blue-500" /> System Status
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">CPU Load</span>
                            <span className="font-mono font-bold text-green-600">12%</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Memory</span>
                            <span className="font-mono font-bold text-green-600">340MB</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Uptime</span>
                            <span className="font-mono font-bold">99.9%</span>
                        </div>
                    </div>
                </div>

                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                    <div className="flex items-center gap-2 text-bizit-dark font-bold">
                        <Users size={18} className="text-orange-500" /> User Stats
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Total Users</span>
                            <span className="font-mono font-bold">1,205</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Active Today</span>
                            <span className="font-mono font-bold text-blue-600">85</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">New (24h)</span>
                            <span className="font-mono font-bold text-green-600">+12</span>
                        </div>
                    </div>
                </div>

                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                    <div className="flex items-center gap-2 text-bizit-dark font-bold">
                        <Activity size={18} className="text-purple-500" /> Security Events
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Failed Logins</span>
                            <span className="font-mono font-bold text-orange-500">3</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">Flagged Reviews</span>
                            <span className="font-mono font-bold text-red-500">1</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-bizit-gray">System Version</span>
                            <span className="font-mono font-bold">v2.0.0</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-bizit-dark/5 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="font-bold text-bizit-dark">Recent User Activity</h3>
                    <BizitButton variant="outline" size="sm">View All Logs</BizitButton>
                </div>
                <div className="divide-y divide-gray-100">
                    {[
                        { u: 'Business Owner A', a: 'Updated Profile', t: '2 mins ago' },
                        { u: 'Admin User', a: 'System Health Check', t: '15 mins ago' },
                        { u: 'New User', a: 'Account Created', t: '1 hour ago' },
                        { u: 'System', a: 'Daily Backup Completed', t: '4 hours ago' }
                    ].map((log, i) => (
                        <div key={i} className="p-4 flex justify-between items-center hover:bg-gray-50">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-500">
                                    {log.u[0]}
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-bizit-dark">{log.u}</p>
                                    <p className="text-xs text-bizit-gray">{log.a}</p>
                                </div>
                            </div>
                            <span className="text-xs text-gray-400 font-mono">{log.t}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
