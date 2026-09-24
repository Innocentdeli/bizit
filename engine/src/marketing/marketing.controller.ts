import { Controller, Get, Post, Patch, Delete, Param, Body, Query } from '@nestjs/common';
import { MarketingService } from './marketing.service';

@Controller('marketing')
export class MarketingController {
  constructor(private readonly marketingService: MarketingService) {}

  // ─── Ad Campaigns ──────────────────────────────────────────────────────────
  @Get('ads')
  getAdCampaigns(@Query('userId') userId: string) {
    return this.marketingService.getAdCampaigns(userId);
  }

  @Post('ads')
  createAdCampaign(@Body() body: { userId: string } & any) {
    const { userId, ...data } = body;
    return this.marketingService.createAdCampaign(userId, data);
  }

  @Patch('ads/:id')
  updateAdCampaign(@Param('id') id: string, @Body() data: any) {
    return this.marketingService.updateAdCampaign(id, data);
  }

  @Delete('ads/:id')
  deleteAdCampaign(@Param('id') id: string) {
    return this.marketingService.deleteAdCampaign(id);
  }

  // ─── Email Campaigns ───────────────────────────────────────────────────────
  @Get('email')
  getEmailCampaigns(@Query('userId') userId: string) {
    return this.marketingService.getEmailCampaigns(userId);
  }

  @Post('email')
  createEmailCampaign(@Body() body: { userId: string } & any) {
    const { userId, ...data } = body;
    return this.marketingService.createEmailCampaign(userId, data);
  }

  @Post('email/:id/send')
  sendEmailCampaign(@Param('id') id: string) {
    return this.marketingService.sendEmailCampaign(id);
  }

  // ─── Social Posts ──────────────────────────────────────────────────────────
  @Get('social')
  getSocialPosts(@Query('userId') userId: string) {
    return this.marketingService.getSocialPosts(userId);
  }

  @Post('social')
  createSocialPost(@Body() body: { userId: string } & any) {
    const { userId, ...data } = body;
    return this.marketingService.createSocialPost(userId, data);
  }

  @Post('social/:id/publish')
  publishSocialPost(@Param('id') id: string) {
    return this.marketingService.publishSocialPost(id);
  }

  @Delete('social/:id')
  deleteSocialPost(@Param('id') id: string) {
    return this.marketingService.deleteSocialPost(id);
  }
}
