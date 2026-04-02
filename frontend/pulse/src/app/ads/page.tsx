'use client';

import React from 'react';
import { Megaphone, TrendingUp, Users, Target, ShieldCheck } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import { fetchAPI } from '@/lib/api';

export default function AdsPage() {
    const [campaigns, setCampaigns] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        async function loadAds() {
            const data = await fetchAPI('/ads/campaigns/b-101');
            if (data && data.campaigns) {
                setCampaigns(data.campaigns);
            }
            setLoading(false);
        }
        loadAds();
    }, []);

    return (
        <div className="space-y-8 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <Megaphone className="text-bizit-green" />
                        Ad Manager
                    </h1>
                    <p className="text-bizit-gray text-sm">Reach more customers with targeted campaigns.</p>
                </div>
                <BizitButton variant="primary" size="sm">Create Campaign</BizitButton>
            </div>

            {/* Campaign Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider mb-2">
                        <Users size={14} /> Impressions
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">
                        {campaigns.reduce((sum, c) => sum + (c.impressions || 0), 0).toLocaleString()}
                    </p>
                    <span className="text-xs text-green-600 font-bold">+24% vs last week</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider mb-2">
                        <Target size={14} /> Total Clicks
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">
                        {campaigns.reduce((sum, c) => sum + (c.clicks || 0), 0).toLocaleString()}
                    </p>
                    <span className="text-xs text-green-600 font-bold">Live Data</span>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <div className="flex items-center gap-2 text-bizit-gray text-xs font-bold uppercase tracking-wider mb-2">
                        <TrendingUp size={14} /> Avg. Spend
                    </div>
                    <p className="text-3xl font-bold text-bizit-dark">
                        ₦{(campaigns.reduce((sum, c) => sum + (c.budget || 0), 0) / (campaigns.length || 1)).toLocaleString()}
                    </p>
                    <span className="text-xs text-bizit-green font-bold">Optimized By Kernel</span>
                </div>
            </div>

            {/* Active Campaigns */}
            <div className="bg-white rounded-2xl border border-bizit-dark/5 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="font-bold text-bizit-dark">Active Campaigns</h3>
                    {loading && <span className="text-xs text-bizit-gray animate-pulse">Syncing...</span>}
                </div>
                <div className="divide-y divide-gray-100">
                    {campaigns.length === 0 && !loading && (
                        <div className="p-10 text-center text-bizit-gray italic">No active campaigns found.</div>
                    )}
                    {campaigns.map((camp, i) => {
                        const isAuto = camp.title.includes('AUTO:');
                        return (
                            <div key={i} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-gray-50 border-l-4 border-transparent hover:border-bizit-green transition-all">
                                <div>
                                    <h4 className="font-bold text-bizit-dark flex items-center gap-2">
                                        {camp.title}
                                        {isAuto && (
                                            <span className="px-2 py-0.5 bg-bizit-dark text-white text-[9px] rounded font-bold flex items-center gap-1">
                                                <ShieldCheck size={10} className="text-bizit-green" /> SOVEREIGN AUTO
                                            </span>
                                        )}
                                    </h4>
                                    <div className="flex gap-2 mt-1">
                                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${camp.status === 'ACTIVE' ? 'bg-green-100 text-green-600' :
                                            'bg-gray-100 text-gray-500'
                                            }`}>
                                            {camp.status}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex gap-8 text-sm">
                                    <div>
                                        <p className="text-bizit-gray text-xs">Budget</p>
                                        <p className="font-bold text-bizit-dark">₦{camp.budget.toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <p className="text-bizit-gray text-xs">Performance</p>
                                        <p className="font-bold text-bizit-dark">{camp.impressions} Views</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <BizitButton variant="outline" size="sm">{isAuto ? 'View History' : 'Edit'}</BizitButton>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
