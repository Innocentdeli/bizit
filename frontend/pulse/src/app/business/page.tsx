'use client';

import React from 'react';
import Link from 'next/link';
import { MapPin, Star, Building2 } from 'lucide-react';

const BUSINESSES = [
    {
        id: 'b-101',
        name: 'Lagos Tech Hub',
        category: 'Technology & Innovation',
        location: 'Yaba, Lagos',
        rating: 4.8,
        reviews: 124,
        image: 'bg-blue-100'
    },
    {
        id: 'b-102',
        name: 'Mama Cassie\'s Catering',
        category: 'Food & Beverage',
        location: 'Ikeja, Lagos',
        rating: 4.5,
        reviews: 89,
        image: 'bg-orange-100'
    },
    {
        id: 'b-103',
        name: 'Blue Chip Logistics',
        category: 'Logistics',
        location: 'Apapa, Lagos',
        rating: 3.9,
        reviews: 42,
        image: 'bg-slate-100'
    }
];

export default function BusinessDirectoryPage() {
    return (
        <div className="space-y-8 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <Building2 className="text-bizit-green" />
                        Business Directory
                    </h1>
                    <p className="text-bizit-gray text-sm">Verified businesses across the network.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {BUSINESSES.map((business) => (
                    <Link href={`/business/${business.id}`} key={business.id} className="group block h-full">
                        <div className="bg-white rounded-2xl border border-bizit-dark/5 shadow-sm overflow-hidden h-full hover:shadow-md transition-shadow">
                            <div className={`h-32 w-full ${business.image} relative`}>
                                <div className="absolute top-4 right-4 bg-white/90 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-sm">
                                    <Star size={10} className="text-yellow-500" fill="currentColor" />
                                    {business.rating}
                                </div>
                            </div>
                            <div className="p-5 space-y-3">
                                <div>
                                    <h3 className="font-bold text-lg text-bizit-dark group-hover:text-bizit-green transition-colors">{business.name}</h3>
                                    <p className="text-xs text-bizit-gray font-medium uppercase tracking-wider">{business.category}</p>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-bizit-gray">
                                    <MapPin size={14} />
                                    {business.location}
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}
