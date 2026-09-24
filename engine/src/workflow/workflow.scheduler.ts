import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { WorkflowService } from './workflow.service';
import { PrismaService } from '../prisma.service';

@Injectable()
export class WorkflowScheduler {
  private readonly logger = new Logger(WorkflowScheduler.name);

  constructor(
    private workflowService: WorkflowService,
    private prisma: PrismaService,
  ) {}

  // Runs every hour to check workflows that need scheduled execution
  @Cron(CronExpression.EVERY_HOUR)
  async runScheduledWorkflows() {
    this.logger.log('Checking scheduled workflows...');

    // Find active workflows that have a "schedule" trigger node
    const workflows = await this.prisma.workflow.findMany({
      where: { isActive: true },
      include: { nodes: true },
    });

    const scheduledWorkflows = workflows.filter((w) =>
      w.nodes.some((n) => {
        const data = JSON.parse(n.data || '{}');
        return n.type === 'trigger' && data.scheduleType === 'hourly';
      }),
    );

    for (const workflow of scheduledWorkflows) {
      this.logger.log(`Triggering scheduled workflow: ${workflow.name}`);
      try {
        await this.workflowService.triggerWorkflow(workflow.id);
      } catch (err) {
        this.logger.error(`Failed to schedule workflow ${workflow.id}: ${err.message}`);
      }
    }
  }

  // Runs every day at 9am to trigger daily workflows
  @Cron('0 9 * * *')
  async runDailyWorkflows() {
    this.logger.log('Triggering daily scheduled workflows...');

    const workflows = await this.prisma.workflow.findMany({
      where: { isActive: true },
      include: { nodes: true },
    });

    const dailyWorkflows = workflows.filter((w) =>
      w.nodes.some((n) => {
        const data = JSON.parse(n.data || '{}');
        return n.type === 'trigger' && data.scheduleType === 'daily';
      }),
    );

    for (const workflow of dailyWorkflows) {
      await this.workflowService.triggerWorkflow(workflow.id);
    }
  }
}
