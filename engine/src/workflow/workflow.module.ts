import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { ScheduleModule } from '@nestjs/schedule';
import { WorkflowController } from './workflow.controller';
import { WorkflowService } from './workflow.service';
import { WorkflowProcessor } from './workflow.processor';
import { WorkflowScheduler } from './workflow.scheduler';
import { PrismaService } from '../prisma.service';

@Module({
  imports: [
    BullModule.registerQueue({ name: 'workflows' }),
    ScheduleModule.forRoot(),
  ],
  controllers: [WorkflowController],
  providers: [WorkflowService, WorkflowProcessor, WorkflowScheduler, PrismaService],
})
export class WorkflowModule {}
