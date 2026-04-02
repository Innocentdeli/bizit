'use client';

import React, { useEffect, useState } from 'react';
import { LayoutDashboard, Users, Eye, Megaphone, MousePointer, TrendingUp, Calendar } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import { fetchAPI } from '@/lib/api';

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [recs, setRecs] = useState<any[]>([]);
    const [topics, setTopics] = useState<any>(null);

    useEffect(() => {
        async function loadData() {
            // Parallel fetch for speed
            const [overviewData, recData, audienceData] = await Promise.all([
                fetchAPI('/analytics/overview'),
                fetchAPI('/audit/business/b-101'),
                fetchAPI('/analytics/audience')
            ]);

            if (overviewData) setStats(overviewData);
            if (recData && recData.recommendations) setRecs(recData.recommendations);
            if (audienceData) setTopics(audienceData);
        }
        loadData();
    }, []);

    if (!stats) return <div className="p-10 text-center">Loading Dashboard...</div>;

    return (
        <div className="space-y-8 pb-20">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <LayoutDashboard className="text-bizit-green" />
                        Business Dashboard
                    </h1>
                    <p className="text-bizit-gray text-sm">Overview for {stats.business_id}</p>
                </div>
                <div className="flex gap-2">
                    <button className="bg-white border border-gray-200 text-bizit-dark px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
                        <Calendar size={14} /> {stats.period}
                    </button>
                    <BizitButton variant="primary" size="sm">Export Report</BizitButton>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider">
                        <TrendingUp size={14} className="text-bizit-green" /> Systemic Boost
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">+{stats.metrics.visibility_boost}</p>
                    <span className="text-[10px] text-bizit-green font-bold px-2 py-0.5 bg-green-50 rounded-full">Autonomous Signal</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider">
                        <Users size={14} /> Visitors
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">{stats.metrics.unique_visitors.toLocaleString()}</p>
                    <span className="text-xs text-green-600 font-bold">+8%</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider">
                        <Megaphone size={14} /> Active Ads
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">{stats.metrics.active_ads}</p>
                    <span className="text-xs text-bizit-green font-bold">Live Campaigns</span>
                </div>
                <div className="p-6 bg-bizit-dark text-white rounded-2xl border border-transparent shadow-lg space-y-2">
                    <div className="flex items-center gap-2 text-white/70 text-xs font-bold uppercase tracking-wider">
                        <TrendingUp size={14} /> Revenue (Est)
                    </div>
                    <p className="text-3xl font-bold">{stats.revenue_estimated}</p>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Main Chart */}
                <div className="md:col-span-2 bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <h3 className="font-bold text-bizit-dark mb-6">Traffic Overview</h3>
                    <div className="h-64 flex items-end justify-between gap-2 px-2 border-b border-dashed border-gray-200">
                        {stats.traffic_chart && stats.traffic_chart.map((h: number, i: number) => (
                            <div key={i} className="w-full bg-bizit-green opacity-80 hover:opacity-100 rounded-t-sm transition-all" style={{ height: `${h}%` }} />
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 text-xs text-bizit-gray font-mono">
                        <span>Day 1</span>
                        <span>Day 15</span>
                        <span>Day 30</span>
                    </div>
                </div>

                {/* Audience Insights */}
                <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-6">
                    <h3 className="font-bold text-bizit-dark">Audience</h3>

                    <div className="space-y-4">
                        {topics?.top_locations?.map((loc: string, i: number) => (
                            <div key={i}>
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="font-bold text-bizit-dark">{loc}</span>
                                    <span className="text-bizit-gray">{45 - (i * 10)}%</span>
                                </div>
                                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                    <div className={`h-full ${i === 0 ? 'bg-blue-500' : i === 1 ? 'bg-purple-500' : 'bg-pink-500'}`} style={{ width: `${45 - (i * 10)}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="pt-6 border-t">
                        <h4 className="font-bold text-sm mb-3">Top Interests</h4>
                        <div className="flex flex-wrap gap-2">
                            {topics?.demographics?.interests?.map((tag: string) => (
                                <span key={tag} className="px-2 py-1 bg-gray-100 text-bizit-dark text-[10px] font-bold rounded-md">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Module 9: Recommendations */}
            <div className="bg-gradient-to-r from-bizit-dark to-slate-900 rounded-2xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-bizit-green opacity-10 rounded-full blur-3xl -mr-16 -mt-16"></div>
                <div className="relative z-10">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="text-bizit-green" />
                        AI Smart Recommendations
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {recs.map((rec: any, i: number) => (
                            <div key={i} className="bg-white/10 backdrop-blur-md border border-white/10 p-4 rounded-xl hover:bg-white/20 transition-colors cursor-pointer">
                                <h3 className="font-bold text-lg mb-1">{rec.recommendation}</h3>
                                <p className="text-sm text-gray-300 mb-4 h-10 line-clamp-2">{rec.reason}</p>
                                <button className="text-xs font-bold text-bizit-green uppercase tracking-wider flex items-center gap-1 hover:gap-2 transition-all">
                                    {rec.action || 'View Action'} <LayoutDashboard size={12} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
