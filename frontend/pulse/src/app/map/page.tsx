'use client';

import React from 'react';
import MapModule from '@/components/modules/MapModule';
import { Map as MapIcon } from 'lucide-react';

export default function MapPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <MapIcon className="text-bizit-green" />
                        Market Intelligence Map
                    </h1>
                    <p className="text-bizit-gray text-sm">Real-time business density and opportunity heatmaps.</p>
                </div>
                <div className="flex gap-2 text-xs">
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full">Live Feed</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">Lagos, NG</span>
                </div>
            </div>

            <MapModule />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <h3 className="font-bold text-bizit-dark mb-2">High Demand Zones</h3>
                    <p className="text-sm text-bizit-gray">Yaba and Ikeja showing 15% increase in food delivery requests.</p>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <h3 className="font-bold text-bizit-dark mb-2">Supply Gaps</h3>
                    <p className="text-sm text-bizit-gray">Shortage of premium co-working spaces in Lekki Phase 1.</p>
                </div>
                <div className="p-6 bg-white rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <h3 className="font-bold text-bizit-dark mb-2">Competitor Alert</h3>
                    <p className="text-sm text-bizit-gray">3 new logistics hubs registered in Apapa axis this week.</p>
                </div>
            </div>
        </div>
    );
}
