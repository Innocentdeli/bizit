import { Controller, Get } from '@nestjs/common';
import { MarketplaceService } from './marketplace.service';

@Controller('marketplace')
export class MarketplaceController {
  constructor(private readonly marketplace: MarketplaceService) {}

  @Get('kpis')
  getKpis() {
    return this.marketplace.getKpis();
  }

  @Get('acquisition')
  getAcquisition() {
    return this.marketplace.getAcquisitionTrend();
  }

  @Get('gmv')
  getGmv() {
    return this.marketplace.getGmvTrend();
  }

  @Get('liquidity')
  getLiquidity() {
    return this.marketplace.getLiquidityByCategory();
  }

  @Get('geographic')
  getGeographic() {
    return this.marketplace.getGeographicSpread();
  }

  @Get('cohort')
  getCohort() {
    return this.marketplace.getCohortRetention();
  }

  @Get('referral')
  getReferral() {
    return this.marketplace.getReferralPerformance();
  }

  @Get('vendor-funnel')
  getVendorFunnel() {
    return this.marketplace.getVendorFunnel();
  }

  @Get('trust')
  getTrust() {
    return this.marketplace.getTrustMetrics();
  }
}
