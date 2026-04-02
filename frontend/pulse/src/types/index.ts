// Core Types
export type UrgencyLevel = 'WATCH' | 'ACT';
export type ThoughtLevel = 'TACTICAL' | 'STRATEGIC' | 'SOVEREIGN';
export type Strategy = 'PRESERVE' | 'GROWTH' | 'ARBITRAGE';

export interface Source {
  title: string;
  trust: number;
  reason: string;
  url?: string;
}

export interface Forecast {
  scenario: string;
  trajectory: string;
  triggers: string;
}

export interface Recommendation {
  id: number;
  action: string;
  detail: string;
}

export interface IntelligenceReport {
  id: string;
  query: string;
  headline: string;
  signal: string;
  impact: string;
  urgency: UrgencyLevel;
  confidence: number;
  sources: Source[];
  strategy: Strategy;
  timestamp: number;
  forecast?: Forecast[];
  recommendations?: Recommendation[];
  thought_signature?: {
    level: ThoughtLevel;
    model: string;
    trace_id: string;
  };
}

export interface PersonalizationData {
  objective: string;
  region: string;
  strategy: Strategy;
  riskProfile?: string;
}

export type ThinkingStatus = 'pending' | 'loading' | 'complete';

export interface ThinkingStep {
  id: string;
  label: string;
  status: ThinkingStatus;
  icon: any;
}

export interface PulseState {
  // Data
  history: IntelligenceReport[];
  activeReport: IntelligenceReport | null;

  // UI State
  isThinking: boolean;
  thinkingProgress: number;
  currentQuery: string;

  // User Context
  personalization: PersonalizationData;
  isLoading: boolean;

  // Actions
  setHistory: (history: IntelligenceReport[]) => void;
  addReport: (report: IntelligenceReport) => void;
  setActiveReport: (report: IntelligenceReport | null) => void;
  setIsThinking: (isThinking: boolean) => void;
  setThinkingProgress: (progress: number) => void;
  setCurrentQuery: (query: string) => void;
  setPersonalization: (data: PersonalizationData) => void;
  setIsLoading: (loading: boolean) => void;
}
