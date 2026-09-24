import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { ScheduleModule } from '@nestjs/schedule';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { WorkflowModule } from './workflow/workflow.module';
import { CommunityModule } from './community/community.module';
import { ReportingModule } from './reporting/reporting.module';
import { BillingModule } from './billing/billing.module';
import { TeamModule } from './team/team.module';
import { GrowthModule } from './growth/growth.module';
import { AdminModule } from './admin/admin.module';
import { MarketingModule } from './marketing/marketing.module';
import { GrowthEngineModule } from './growth-engine/growth-engine.module';
import { AiBridgeModule } from './ai-bridge/ai-bridge.module';
import { MarketplaceModule } from './marketplace/marketplace.module';

@Module({
  imports: [
    ScheduleModule.forRoot(),
    BullModule.forRoot({
      connection: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
      },
    }),
    WorkflowModule,
    CommunityModule,
    ReportingModule,
    BillingModule,
    TeamModule,
    GrowthModule,
    AdminModule,
    MarketingModule,
    GrowthEngineModule,
    AiBridgeModule,
    MarketplaceModule,
  ],


  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
