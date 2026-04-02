'use client';

import React, { useState, useEffect } from 'react';
import { Map, Navigation, Layers, Search, MapPin } from 'lucide-react';
import BizitButton from '../common/BizitButton';

const MapModule = () => {
    const [loading, setLoading] = useState(true);
    const [businesses, setBusinesses] = useState<any[]>([]);

    useEffect(() => {
        const fetchPins = async () => {
            try {
                // Fetch pins centered on Lagos for default view
                const res = await fetch('http://localhost:8002/map/pins?lat=6.5244&lng=3.3792&radius=50.0');
                if (!res.ok) throw new Error('Failed to fetch pins');
                const data = await res.json();
                setBusinesses(data.pins);
            } catch (err) {
                console.error("Map hydration failure:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchPins();
    }, []);

    return (
        <div className="relative w-full h-[80vh] bg-gray-100 rounded-3xl overflow-hidden border border-bizit-dark/10 shadow-inner group">

            {/* Map Placeholder / Visual */}
            <div className={`absolute inset-0 bg-bizit-light transition-opacity duration-700 ${loading ? 'opacity-100' : 'opacity-100'}`}>
                <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#2563EB_1px,transparent_1px)] [background-size:20px_20px]" />

                {/* Simulated Pins */}
                {!loading && businesses.map((b, i) => (
                    <div
                        key={b.id}
                        className="absolute flex flex-col items-center cursor-pointer hover:scale-110 transition-transform"
                        style={{ top: `${40 + (i * 10)}%`, left: `${45 + (i * 5)}%` }} // Dummy positioning
                    >
                        <MapPin className="text-bizit-green drop-shadow-lg" size={32} fill="currentColor" />
                        <span className="bg-white px-2 py-1 rounded-md text-[10px] font-bold shadow-sm whitespace-nowrap mt-1">
                            {b.name}
                        </span>
                    </div>
                ))}
            </div>

            {/* Loading State */}
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-50">
                    <div className="flex flex-col items-center gap-3">
                        <Map className="animate-bounce text-bizit-green" size={32} />
                        <p className="text-xs font-bold text-bizit-dark tracking-widest uppercase">Initializing Geo-Spatial Grid...</p>
                    </div>
                </div>
            )}

            {/* Map Controls Overlay */}
            <div className="absolute top-6 left-6 flex flex-col gap-3">
                <div className="bg-white/90 backdrop-blur p-2 rounded-xl border shadow-sm">
                    <input
                        type="text"
                        placeholder="Search area..."
                        className="bg-transparent text-sm outline-none w-48 px-2"
                    />
                    <Search size={16} className="text-gray-400 absolute right-4 top-3" />
                </div>
                <div className="flex gap-2">
                    <button className="p-2 bg-white rounded-lg shadow-sm hover:bg-gray-50 border"><Layers size={18} /></button>
                    <button className="p-2 bg-white rounded-lg shadow-sm hover:bg-gray-50 border"><Navigation size={18} /></button>
                </div>
            </div>

            <div className="absolute bottom-6 right-6">
                <BizitButton variant="primary" className="shadow-lg">
                    Explore This Area
                </BizitButton>
            </div>
        </div>
    );
};

export default MapModule;
