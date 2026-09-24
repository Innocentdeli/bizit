import { Controller, Get, Post, Param, Body, Query } from '@nestjs/common';
import { GrowthService } from './growth.service';

@Controller('growth')
export class GrowthController {
  constructor(private readonly growthService: GrowthService) {}

  @Get()
  getUserStrategies(@Query('userId') userId: string) {
    return this.growthService.getUserStrategies(userId);
  }

  @Get(':id')
  getStrategyById(@Param('id') id: string, @Query('userId') userId: string) {
    return this.growthService.getStrategyById(id, userId);
  }

  @Post('generate')
  generateStrategy(
    @Body() body: {
      userId: string;
      businessType: string;
      industry: string;
      revenueModel: string;
      audience: string;
      currentMetrics: string;
    }
  ) {
    return this.growthService.generateStrategy(body.userId, body);
  }
}
