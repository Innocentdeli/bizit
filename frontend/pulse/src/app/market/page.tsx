'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, Activity, AlertCircle, BarChart3, ArrowUpRight } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import { fetchAPI } from '@/lib/api';

export default function MarketPage() {
    const [snapshot, setSnapshot] = useState<any>(null);
    const [supplyDemand, setSupplyDemand] = useState<any>(null);
    const [gaps, setGaps] = useState<any[]>([]);

    useEffect(() => {
        async function loadData() {
            const [snap, supply, gapData] = await Promise.all([
                fetchAPI('/market/snapshot'),
                fetchAPI('/market/supply-demand'),
                fetchAPI('/market/gaps')
            ]);

            if (snap) setSnapshot(snap);
            if (supply) setSupplyDemand(supply);
            if (gapData && gapData.gaps) setGaps(gapData.gaps);
        }
        loadData();
    }, []);

    if (!snapshot) return <div className="p-10 text-center">Loading Market Intelligence...</div>;

    const m = snapshot.metrics;

    return (
        <div className="space-y-8 pb-20">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <BarChart3 className="text-bizit-green" />
                        Market Intelligence
                    </h1>
                    <p className="text-bizit-gray text-sm">Real-time supply, demand, and opportunity gaps.</p>
                </div>
                <div className="flex gap-2">
                    <select className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-bizit-green">
                        <option>Lagos, NG</option>
                        <option>Nairobi, KE</option>
                    </select>
                    <select className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-bizit-green">
                        <option>Technology</option>
                        <option>Food & Dining</option>
                        <option>Real Estate</option>
                    </select>
                </div>
            </div>

            {/* Module 6: Market Snapshot */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <p className="text-xs text-bizit-gray font-bold uppercase tracking-wider">Total Businesses</p>
                    <p className="text-3xl font-bold text-bizit-dark">{m.total_businesses.toLocaleString()}</p>
                    <span className="text-xs text-green-600 flex items-center gap-1"><TrendingUp size={12} /> {m.growth_trend}</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <p className="text-xs text-bizit-gray font-bold uppercase tracking-wider">Avg. Pricing</p>
                    <p className="text-3xl font-bold text-bizit-dark">{m.avg_pricing}</p>
                    <span className="text-xs text-red-500 flex items-center gap-1"><ArrowUpRight size={12} /> +5% inflation adj.</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm space-y-2">
                    <p className="text-xs text-bizit-gray font-bold uppercase tracking-wider">Saturation</p>
                    <div className="flex items-center gap-2">
                        <p className={`text-3xl font-bold ${m.saturation_score > 0.7 ? 'text-orange-500' : 'text-green-500'}`}>
                            {m.saturation_score > 0.7 ? 'High' : 'Low'}
                        </p>
                        <AlertCircle size={20} className={m.saturation_score > 0.7 ? 'text-orange-500' : 'text-green-500'} />
                    </div>
                    <span className="text-xs text-bizit-gray">{Math.round(m.saturation_score * 100)}% capacity</span>
                </div>
                <div className="p-6 bg-bizit-green text-white rounded-2xl border border-transparent shadow-lg space-y-2">
                    <p className="text-xs font-bold uppercase tracking-wider opacity-80">Market Grade</p>
                    <p className="text-3xl font-bold">B+</p>
                    <span className="text-xs opacity-80">Stable Growth</span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Module 7: Supply vs Demand */}
                <div className="lg:col-span-2 p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <h3 className="font-bold text-bizit-dark mb-6 flex items-center gap-2">
                        <Activity size={18} className="text-bizit-green" />
                        Supply vs Demand Signals
                    </h3>
                    <div className="h-64 flex items-end justify-between gap-4 px-4 pb-4 border-b border-dashed">
                        {/* Mock Chart Bars from API */}
                        {supplyDemand?.chart_data?.map((h: number, i: number) => (
                            <div key={i} className="w-full flex gap-1 items-end h-full">
                                <div style={{ height: `${h}%` }} className="w-full bg-bizit-green rounded-t-sm opacity-20 hover:opacity-100 transition-opacity"></div>
                                <div style={{ height: `${h * 0.7}%` }} className="w-full bg-bizit-dark rounded-t-sm opacity-10 hover:opacity-80 transition-opacity"></div>
                            </div>
                        ))}
                    </div>
                    <div className="flex items-center gap-6 mt-4 justify-center text-xs text-bizit-gray">
                        <div className="flex items-center gap-2"><div className="w-3 h-3 bg-bizit-green opacity-50 rounded-sm" /> Demand (Searches)</div>
                        <div className="flex items-center gap-2"><div className="w-3 h-3 bg-bizit-dark opacity-30 rounded-sm" /> Supply (Listings)</div>
                    </div>
                </div>

                {/* Module 8: Gap Detection */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-bold text-bizit-dark">Detected Gaps</h3>
                        <span className="text-xs font-bold text-bizit-green bg-bizit-green/10 px-2 py-1 rounded-full">{gaps.length} Opportunities</span>
                    </div>

                    <div className="space-y-3">
                        {gaps.map((gap: any, i: number) => (
                            <div key={i} className={`p-4 bg-white rounded-xl border border-l-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${gap.type === 'Underserved Service' ? 'border-l-bizit-gold' : 'border-l-blue-500'
                                }`}>
                                <h4 className="font-bold text-sm text-bizit-dark">{gap.type}</h4>
                                <p className="text-xs text-bizit-gray mt-1">{gap.description}</p>
                                <div className="mt-3 flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-bizit-green">Potential: {gap.potential_revenue}</span>
                                    <BizitButton variant="outline" size="sm" className="h-7 text-xs">View Data</BizitButton>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
