import { Injectable, Logger, HttpException, HttpStatus } from '@nestjs/common';

@Injectable()
export class AiBridgeService {
  private readonly logger = new Logger(AiBridgeService.name);
  private readonly BASE = 'http://127.0.0.1:8002';

  // ─── AI Copy Generation ────────────────────────────────────────────────────

  async generateMarketingCopy(prompt: string, contextType: string): Promise<string> {
    this.logger.log(`AI generation for context: ${contextType}`);
    const data = await this.post('/ai/chat/completion', {
      query: prompt,
      context: { type: contextType, platform: 'bizit_marketing_hub' },
    });
    return data.response || 'AI generation returned no content.';
  }

  // ─── Organism ──────────────────────────────────────────────────────────────

  getOrganismStatus()                         { return this.get('/organism/status'); }
  getOrganismStats()                          { return this.get('/organism/stats'); }
  getOrganismActivity(limit = 50, cycle?: string) {
    const p = new URLSearchParams({ limit: String(limit) });
    if (cycle) p.set('cycle', cycle);
    return this.get(`/organism/activity?${p}`);
  }
  getOrganismAlerts(businessId: string)       { return this.get(`/organism/alerts/${businessId}`); }
  markAlertRead(alertId: number)              { return this.post(`/organism/alerts/${alertId}/read`, {}); }
  triggerOrganismCycle()                      { return this.post('/organism/trigger', {}); }

  // ─── Monetization / Surge Pricing ─────────────────────────────────────────

  getActiveSurges()                           { return this.get('/billing/surges'); }
  getSurgeHistory()                           { return this.get('/billing/surges/history'); }
  getBoostProducts(category?: string) {
    const p = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.get(`/billing/boosts${p}`);
  }

  // ─── Market Intelligence ───────────────────────────────────────────────────

  getMarketSnapshot(location: string, category: string) {
    return this.get(`/market/snapshot?location=${encodeURIComponent(location)}&category=${encodeURIComponent(category)}`);
  }
  getSupplyDemand(location: string) {
    return this.get(`/market/supply-demand?location=${encodeURIComponent(location)}`);
  }
  getMarketGaps(location: string) {
    return this.get(`/market/gaps?location=${encodeURIComponent(location)}`);
  }

  // ─── Analytics ────────────────────────────────────────────────────────────

  getAnalyticsOverview(businessId: string) {
    return this.get(`/analytics/overview?business_id=${businessId}`);
  }

  // ─── HTTP helpers ──────────────────────────────────────────────────────────

  private async get(path: string): Promise<any> {
    try {
      const res = await fetch(`${this.BASE}${path}`);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      return res.json();
    } catch (err) {
      this.logger.error(`GET ${path} failed: ${err}`);
      throw new HttpException(`Organism unreachable: ${path}`, HttpStatus.SERVICE_UNAVAILABLE);
    }
  }

  private async post(path: string, body: any): Promise<any> {
    try {
      const res = await fetch(`${this.BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      return res.json();
    } catch (err) {
      this.logger.error(`POST ${path} failed: ${err}`);
      throw new HttpException(`Organism unreachable: ${path}`, HttpStatus.SERVICE_UNAVAILABLE);
    }
  }
}
