import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';
import { PrismaService } from '../prisma.service';

@Injectable()
export class WorkflowService {
  constructor(
    @InjectQueue('workflows') private workflowsQueue: Queue,
    private prisma: PrismaService,
  ) {}

  async triggerWorkflow(workflowId: string, context?: any) {
    const workflow = await this.prisma.workflow.findUnique({ where: { id: workflowId } });
    if (!workflow) throw new Error('Workflow not found');
    if (!workflow.isActive) throw new Error('Workflow is inactive');

    const execution = await this.prisma.workflowExecution.create({
      data: {
        workflowId,
        status: 'pending',
        logs: JSON.stringify([`[${new Date().toISOString()}] Queued for execution...`]),
      },
    });

    // Add to BullMQ with retry + exponential backoff
    await this.workflowsQueue.add(
      'execute-workflow',
      { executionId: execution.id, workflowId: workflow.id, context },
      {
        attempts: 3,
        backoff: { type: 'exponential', delay: 2000 },
        removeOnComplete: { count: 100 },
        removeOnFail: { count: 50 },
      },
    );

    return { executionId: execution.id, status: 'pending' };
  }

  async getExecutions(workflowId: string) {
    return this.prisma.workflowExecution.findMany({
      where: { workflowId },
      orderBy: { startedAt: 'desc' },
      take: 20,
    });
  }
}
