'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import SearchBar from '@/components/search/SearchBar';
import ThinkingTrace from '@/components/search/ThinkingTrace';
import ClarityCard from '@/components/search/ClarityCard';
import RecentSearches from '@/components/search/RecentSearches';
import { usePulseStore } from '@/store/usePulseStore';
import { Search, BrainCircuit, ShieldCheck, Zap } from 'lucide-react';
import type { ThinkingStep } from '@/types';

export default function Home() {
  const router = useRouter();
  const {
    setIsThinking,
    setCurrentQuery,
    addReport,
    setActiveReport,
    isThinking
  } = usePulseStore();

  const [currentQueryLocal, setCurrentQueryLocal] = useState('');
  const [clarityData, setClarityData] = useState<{ question: string; options: string[]; context?: any } | null>(null);
  const [steps, setSteps] = useState<ThinkingStep[]>([
    { id: '1', label: 'Strategic Mandate Inference', status: 'pending', icon: Zap },
    { id: '2', label: 'Intelligence Gathering', status: 'pending', icon: Search },
    { id: '3', label: 'Deep Analysis & Synthesis', status: 'pending', icon: BrainCircuit },
    { id: '4', label: 'Verification & Trust Check', status: 'pending', icon: ShieldCheck },
  ]);

  const handleSearch = async (query: string, options: any, clarification: string = '') => {
    setIsThinking(true);
    setCurrentQuery(query);
    setCurrentQueryLocal(query);
    setClarityData(null);

    // Reset steps
    setSteps(s => s.map(step => ({ ...step, status: 'pending' as const })));

    try {
      // Step 1: Mandate
      setSteps(s => s.map(step => step.id === '1' ? { ...step, status: 'loading' as const } : step));
      await new Promise(r => setTimeout(r, 800));
      setSteps(s => s.map(step => step.id === '1' ? { ...step, status: 'complete' as const } : step));

      // Step 2: Gathering
      setSteps(s => s.map(step => step.id === '2' ? { ...step, status: 'loading' as const } : step));

      const response = await fetch('http://localhost:8002/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          strategy: options.urgency,
          clarification: clarification
        }),
      });

      if (!response.ok) throw new Error('Backend desync');

      const data = await response.json();

      // Check for Clarity Loop
      if (data.status === 'CLARITY_REQUIRED') {
        setIsThinking(false);
        setClarityData({
          question: data.question,
          options: data.options,
          context: data.context
        });
        return;
      }

      setSteps(s => s.map(step => step.id === '2' ? { ...step, status: 'complete' as const } : step));

      // Step 3: Analysis
      setSteps(s => s.map(step => step.id === '3' ? { ...step, status: 'loading' as const } : step));
      await new Promise(r => setTimeout(r, 2000));
      setSteps(s => s.map(step => step.id === '3' ? { ...step, status: 'complete' as const } : step));

      // Step 4: Verification
      setSteps(s => s.map(step => step.id === '4' ? { ...step, status: 'loading' as const } : step));
      await new Promise(r => setTimeout(r, 1000));

      const reportId = Math.random().toString(36).substring(7);

      // Map new intelligence response to frontend format
      const intelligenceData = data.data || data.brief; // Support both formats

      const fullReport = {
        id: reportId,
        query,
        headline: intelligenceData.summary || intelligenceData.headline || `Analysis for ${query}`,
        signal: intelligenceData.verdict || intelligenceData.signal || 'Intelligence Complete',
        impact: intelligenceData.insights?.[0] || intelligenceData.impact || 'Market analysis complete',
        urgency: intelligenceData.verdict === 'OPPORTUNITY' ? 'ACT' as const : 'WATCH' as const,
        confidence: intelligenceData.confidence || 0.95,
        sources: intelligenceData.sources || [],
        strategy: data.strategy || 'GROWTH' as const,
        timestamp: Date.now(),
        forecast: intelligenceData.forecast ? [intelligenceData.forecast] : (intelligenceData.forecast || []),
        recommendations: intelligenceData.recommendations || []
      };

      setSteps(s => s.map(step => step.id === '4' ? { ...step, status: 'complete' as const } : step));

      // Store and Navigate
      addReport(fullReport);
      setActiveReport(fullReport);

      setTimeout(() => {
        setIsThinking(false);
        router.push(`/answer/${reportId}`);
      }, 800);

    } catch (error) {
      console.error(error);
      setIsThinking(false);
      alert("Intelligence Core Desync. Please check backend nodes.");
    }
  };

  const handleClarify = (choice: string) => {
    handleSearch(currentQueryLocal, { urgency: 'Standard' }, choice);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] py-12">
      {/* Search Header */}
      {!isThinking && !clarityData && (
        <div className="text-center space-y-4 mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-bizit-green/10 text-bizit-green text-[10px] font-bold uppercase tracking-widest border border-bizit-green/20">
            Sovereign Market Intelligence
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-bizit-dark">
            Bizit<span className="text-bizit-green">Pulse</span>
          </h1>
          <p className="text-bizit-gray max-w-lg mx-auto text-sm md:text-base">
            Africa's first deep-reasoning market engine. Real-time arbitrage, pricing forecasts, and verified trade signals.
          </p>
        </div>
      )}

      {/* Main Search Bar */}
      {!isThinking && !clarityData && (
        <SearchBar onSearch={handleSearch} isLoading={isThinking} />
      )}

      {/* Clarity Loop Overlay */}
      {clarityData && (
        <ClarityCard
          question={clarityData.question}
          options={clarityData.options}
          context={clarityData.context}
          onClarify={handleClarify}
        />
      )}

      {/* Recent Searches (Conditional) */}
      {!isThinking && !clarityData && (
        <RecentSearches onSelect={(q) => handleSearch(q, { urgency: 'Standard' })} />
      )}

      {/* Thinking Trace Overlay */}
      <ThinkingTrace
        isVisible={isThinking}
        steps={steps}
        currentQuery={currentQueryLocal}
      />

      {/* Trust Signifiers */}
      {!isThinking && !clarityData && (
        <div className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8 opacity-40 grayscale hover:grayscale-0 transition-all duration-500">
          <div className="flex flex-col items-center gap-1">
            <ShieldCheck size={20} />
            <span className="text-[10px] font-bold uppercase tracking-wider">Verified Sources</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <Zap size={20} />
            <span className="text-[10px] font-bold uppercase tracking-wider">Sub-second Sync</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <BrainCircuit size={20} />
            <span className="text-[10px] font-bold uppercase tracking-wider">Deep Reasoning</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <Search size={20} />
            <span className="text-[10px] font-bold uppercase tracking-wider">Market Arb</span>
          </div>
        </div>
      )}
    </div>
  );
}
