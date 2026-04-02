'use client';

import React from 'react';
import { Check, Zap, Shield, Globe } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

const PLANS = [
    {
        name: 'Starter',
        price: 'Free',
        description: 'For new businesses just getting started.',
        features: ['Basic Profile', 'Listing in Directory', 'Receive Reviews', 'Standard Support'],
        icon: Globe,
        cta: 'Get Started',
        popular: false
    },
    {
        name: 'Professional',
        price: '₦15,000',
        period: '/mo',
        description: 'For growing businesses needing insights.',
        features: ['Verified Badge', 'Analytics Dashboard', 'Priority Support', '3 Gap Alerts/mo', 'Review Management'],
        icon: Zap,
        cta: 'Upgrade to Pro',
        popular: true
    },
    {
        name: 'Sovereign',
        price: '₦50,000',
        period: '/mo',
        description: 'Maximum visibility and market dominance.',
        features: ['All Pro Features', 'Unlimited Market Intel', 'API Access', 'Dedicated Manager', 'Featured Listings'],
        icon: Shield,
        cta: 'Contact Sales',
        popular: false
    }
];

export default function PricingPage() {
    return (
        <div className="max-w-6xl mx-auto pb-20 space-y-10">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-bizit-dark">Simple, Transparent Pricing</h1>
                <p className="text-bizit-gray max-w-2xl mx-auto">
                    Choose the plan that fits your growth stage. Unlock powerful market intelligence and operational tools.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
                {PLANS.map((plan) => (
                    <div
                        key={plan.name}
                        className={`relative bg-white rounded-3xl p-8 border ${plan.popular ? 'border-bizit-green shadow-xl scale-105 z-10' : 'border-gray-200 shadow-sm'} flex flex-col`}
                    >
                        {plan.popular && (
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-bizit-green text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                Most Popular
                            </div>
                        )}
                        <div className="mb-6">
                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-4 ${plan.popular ? 'bg-bizit-green text-white' : 'bg-gray-100 text-bizit-dark'}`}>
                                <plan.icon size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-bizit-dark">{plan.name}</h3>
                            <p className="text-sm text-bizit-gray mt-2 h-10">{plan.description}</p>
                        </div>

                        <div className="mb-8">
                            <div className="flex items-baseline">
                                <span className="text-4xl font-bold text-bizit-dark">{plan.price}</span>
                                {plan.period && <span className="text-bizit-gray text-sm ml-1">{plan.period}</span>}
                            </div>
                        </div>

                        <ul className="space-y-4 mb-8 flex-1">
                            {plan.features.map((feature) => (
                                <li key={feature} className="flex items-center gap-3 text-sm text-bizit-dark">
                                    <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center text-green-600 shrink-0">
                                        <Check size={12} strokeWidth={3} />
                                    </div>
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        <BizitButton
                            variant={plan.popular ? 'primary' : 'outline'}
                            className="w-full justify-center"
                        >
                            {plan.cta}
                        </BizitButton>
                    </div>
                ))}
            </div>

            <div className="text-center p-8 bg-bizit-gold/5 rounded-3xl border border-bizit-gold/20">
                <h3 className="font-bold text-bizit-dark mb-2">Need a Custom Enterprise Solution?</h3>
                <p className="text-sm text-bizit-gray mb-4">We offer tailored data packages for government and large multinational corporations.</p>
                <button className="text-bizit-green font-bold text-sm hover:underline">Contact Enterprise Sales</button>
            </div>
        </div>
    );
}
