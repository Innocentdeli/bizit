import { Module } from '@nestjs/common';
import { MarketingService } from './marketing.service';
import { MarketingController } from './marketing.controller';
import { PrismaService } from '../prisma.service';

@Module({
  controllers: [MarketingController],
  providers: [MarketingService, PrismaService],
  exports: [MarketingService],
})
export class MarketingModule {}
