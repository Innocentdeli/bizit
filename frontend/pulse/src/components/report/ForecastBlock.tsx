'use client';

import React from 'react';
import { TrendingUp, ArrowRightCircle, Zap, ShieldCheck } from 'lucide-react';
import { IntelligenceReport } from '@/types';
import { clsx } from 'clsx';

interface ForecastBlockProps {
    report: IntelligenceReport;
}

const ForecastBlock = ({ report }: ForecastBlockProps) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Forecast Card */}
            <div className="bg-white rounded-3xl p-8 border border-bizit-dark/5 shadow-sm space-y-6">
                <div className="flex items-center gap-2 text-bizit-dark">
                    <TrendingUp size={24} className="text-bizit-green" />
                    <h3 className="text-lg font-bold">Strategic Forecast</h3>
                </div>

                <div className="space-y-6">
                    <div className="p-4 rounded-2xl bg-bizit-green/5 border border-bizit-green/10">
                        <p className="text-bizit-dark text-sm font-medium leading-relaxed italic">
                            "{report.headline}"
                        </p>
                    </div>

                    <div className="space-y-4">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-bizit-gray/40">Market Trajectories</h4>
                        <div className="space-y-3">
                            {report.forecast && report.forecast.length > 0 ? (
                                report.forecast.map((tf, i) => (
                                    <div key={i} className="relative pl-6 space-y-2 group">
                                        <div className="absolute left-0 top-1.5 h-3 w-3 rounded-full bg-bizit-green shadow-[0_0_10px_rgba(34,197,94,0.4)]" />
                                        {i < report.forecast!.length - 1 && (
                                            <div className="absolute left-1.5 top-5 bottom-0 w-px bg-bizit-green/20" />
                                        )}

                                        <div className="space-y-1">
                                            <span className="text-xs font-bold text-bizit-green uppercase">
                                                {tf.scenario}
                                            </span>
                                            <p className="text-sm text-bizit-gray leading-snug">
                                                {tf.trajectory}
                                            </p>
                                            <div className="flex items-center gap-3 pt-1">
                                                <div className="flex items-center gap-1.5">
                                                    <Zap size={10} className="text-bizit-gold" />
                                                    <span className="text-[10px] text-bizit-gray/60 font-medium italic">Trigger: {tf.triggers}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="p-4 rounded-xl border border-dashed border-bizit-dark/5 flex items-center justify-center">
                                    <p className="text-xs text-bizit-gray/40 italic">No historical trajectories synthesized.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Recommended Actions */}
            <div className="bg-bizit-dark rounded-3xl p-8 shadow-2xl space-y-6 relative overflow-hidden group">
                {/* Decorative Pattern */}
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-[2s]">
                    <ShieldCheck size={120} className="text-white" />
                </div>

                <div className="flex items-center gap-2 text-bizit-green relative z-10">
                    <ArrowRightCircle size={24} />
                    <h3 className="text-lg font-bold text-white">Sovereign Directives</h3>
                </div>

                <div className="space-y-5 relative z-10">
                    {report.recommendations && report.recommendations.length > 0 ? (
                        report.recommendations.map((rec, i) => (
                            <div
                                key={i}
                                className="flex items-start gap-4 p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-bizit-green/30 hover:shadow-[0_0_20px_rgba(34,197,94,0.1)] transition-all duration-300 group/rec"
                            >
                                <div className="mt-1 h-7 w-7 flex items-center justify-center rounded-lg bg-bizit-green text-bizit-dark font-black text-xs shrink-0 group-hover/rec:scale-110 transition-transform">
                                    {i + 1}
                                </div>
                                <div className="space-y-2">
                                    <p className="text-white font-bold text-sm leading-snug group-hover/rec:text-bizit-green transition-colors">
                                        {rec.action}
                                    </p>
                                    <p className="text-white/40 text-xs leading-relaxed">
                                        {rec.detail}
                                    </p>
                                    <div className={clsx(
                                        "inline-block mt-2 px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border",
                                        rec.priority === 'HIGH' ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                            rec.priority === 'MEDIUM' ? "bg-bizit-gold/10 text-bizit-gold border-bizit-gold/20" :
                                                "bg-bizit-green/10 text-bizit-green border-bizit-green/20"
                                    )}>
                                        Priority: {rec.priority}
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="p-12 rounded-2xl border border-dashed border-white/10 flex flex-col items-center justify-center space-y-3">
                            <Zap size={24} className="text-white/10" />
                            <p className="text-xs text-white/40 italic">Synthesizing direct market maneuvers...</p>
                        </div>
                    )}
                </div>

                <div className="pt-6 mt-auto relative z-10 flex items-center justify-between">
                    <p className="text-[10px] text-white/20 uppercase font-black tracking-[0.3em]">Sovereign Kernel v2.4</p>
                    <div className="h-1.5 w-1.5 rounded-full bg-bizit-green animate-pulse" />
                </div>
            </div>
        </div>
    );
};

export default ForecastBlock;
