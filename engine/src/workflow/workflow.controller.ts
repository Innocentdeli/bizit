import { Controller, Post, Get, Param } from '@nestjs/common';
import { WorkflowService } from './workflow.service';

@Controller('workflows')
export class WorkflowController {
  constructor(private readonly workflowService: WorkflowService) {}

  @Post(':id/trigger')
  async trigger(@Param('id') id: string) {
    return this.workflowService.triggerWorkflow(id);
  }

  @Get(':id/executions')
  async executions(@Param('id') id: string) {
    return this.workflowService.getExecutions(id);
  }
}
