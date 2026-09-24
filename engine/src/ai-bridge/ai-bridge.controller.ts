import { Controller, Post, Get, Body, Param, Query } from '@nestjs/common';
import { AiBridgeService } from './ai-bridge.service';

@Controller('ai')
export class AiBridgeController {
  constructor(private readonly svc: AiBridgeService) {}

  // ── AI Copy ────────────────────────────────────────────────────────────────
  @Post('generate-copy')
  async generateCopy(@Body() body: { prompt: string; contextType: string }) {
    const response = await this.svc.generateMarketingCopy(body.prompt, body.contextType);
    return { success: true, data: response };
  }

  // ── Organism ───────────────────────────────────────────────────────────────
  @Get('organism/status')
  getOrganismStatus() { return this.svc.getOrganismStatus(); }

  @Get('organism/stats')
  getOrganismStats() { return this.svc.getOrganismStats(); }

  @Get('organism/activity')
  getOrganismActivity(
    @Query('limit') limit?: string,
    @Query('cycle') cycle?: string,
  ) { return this.svc.getOrganismActivity(limit ? +limit : 50, cycle); }

  @Get('organism/alerts/:businessId')
  getOrganismAlerts(@Param('businessId') businessId: string) {
    return this.svc.getOrganismAlerts(businessId);
  }

  @Post('organism/alerts/:alertId/read')
  markAlertRead(@Param('alertId') alertId: string) {
    return this.svc.markAlertRead(+alertId);
  }

  @Post('organism/trigger')
  triggerOrganismCycle() { return this.svc.triggerOrganismCycle(); }

  // ── Surge Pricing ──────────────────────────────────────────────────────────
  @Get('surges')
  getActiveSurges() { return this.svc.getActiveSurges(); }

  @Get('surges/history')
  getSurgeHistory() { return this.svc.getSurgeHistory(); }

  @Get('boosts')
  getBoostProducts(@Query('category') category?: string) {
    return this.svc.getBoostProducts(category);
  }

  // ── Market Intel ───────────────────────────────────────────────────────────
  @Get('market/snapshot')
  getMarketSnapshot(
    @Query('location') location = 'Lagos',
    @Query('category') category = 'Technology',
  ) { return this.svc.getMarketSnapshot(location, category); }

  @Get('market/supply-demand')
  getSupplyDemand(@Query('location') location = 'Lagos') {
    return this.svc.getSupplyDemand(location);
  }

  @Get('market/gaps')
  getMarketGaps(@Query('location') location = 'Lagos') {
    return this.svc.getMarketGaps(location);
  }

  // ── Analytics ──────────────────────────────────────────────────────────────
  @Get('analytics/:businessId')
  getAnalytics(@Param('businessId') businessId: string) {
    return this.svc.getAnalyticsOverview(businessId);
  }
}
