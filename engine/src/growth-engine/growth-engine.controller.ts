import { Controller, Get, Post, Delete, Patch, Body, Query, Param } from '@nestjs/common';
import { GrowthEngineService } from './growth-engine.service';

@Controller('growth-engine')
export class GrowthEngineController {
  constructor(private readonly growthEngineService: GrowthEngineService) {}

  @Get('funnels')
  getFunnels(@Query('userId') userId: string) {
    return this.growthEngineService.getFunnels(userId);
  }

  @Post('funnels')
  createFunnel(@Body() body: any) {
    return this.growthEngineService.createFunnel(body.userId, body);
  }

  @Delete('funnels/:id')
  deleteFunnel(@Param('id') id: string) {
    return this.growthEngineService.deleteFunnel(id);
  }

  @Get('referrals')
  getReferrals(@Query('userId') userId: string) {
    return this.growthEngineService.getReferralLinks(userId);
  }

  @Post('referrals')
  createReferral(@Body('userId') userId: string) {
    return this.growthEngineService.createReferralLink(userId);
  }

  @Post('referrals/:code/click')
  trackReferralClick(@Param('code') code: string) {
    return this.growthEngineService.trackReferralClick(code);
  }

  @Get('sequences')
  getSequences(@Query('userId') userId: string) {
    return this.growthEngineService.getRetentionSequences(userId);
  }

  @Post('sequences')
  createSequence(@Body() body: any) {
    return this.growthEngineService.createRetentionSequence(body.userId, body);
  }

  @Delete('sequences/:id')
  deleteSequence(@Param('id') id: string) {
    return this.growthEngineService.deleteRetentionSequence(id);
  }

  @Post('sequences/:id/toggle')
  toggleSequence(@Param('id') id: string) {
    return this.growthEngineService.toggleRetentionSequence(id);
  }
}
