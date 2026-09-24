import { Controller, Get, Post, Patch, Param, Body, Query } from '@nestjs/common';
import { TeamService } from './team.service';

@Controller('team')
export class TeamController {
  constructor(private readonly teamService: TeamService) {}

  @Get()
  getUserTeams(@Query('userId') userId: string) {
    return this.teamService.getUserTeams(userId);
  }

  @Post()
  createTeam(@Body() body: { userId: string; name: string; description?: string }) {
    return this.teamService.createTeam(body.userId, body.name, body.description);
  }

  @Get(':id/dashboard')
  getTeamDashboard(@Param('id') teamId: string, @Query('userId') userId: string) {
    return this.teamService.getTeamDashboard(teamId, userId);
  }

  @Post(':id/members')
  addMember(
    @Param('id') teamId: string,
    @Body() body: { adminId: string; email: string; role?: string }
  ) {
    return this.teamService.addMember(teamId, body.adminId, body.email, body.role);
  }

  @Post(':id/projects')
  createProject(
    @Param('id') teamId: string,
    @Body() body: { userId: string; name: string; description?: string }
  ) {
    return this.teamService.createProject(teamId, body.userId, body.name, body.description);
  }

  @Post(':id/tasks')
  createTask(
    @Param('id') teamId: string,
    @Body() body: { userId: string; projectId: string; title: string; description?: string; assigneeId?: string; priority?: string; dueDate?: string }
  ) {
    return this.teamService.createTask(
      teamId,
      body.userId,
      body.projectId,
      body.title,
      body.description,
      body.assigneeId,
      body.priority,
      body.dueDate ? new Date(body.dueDate) : undefined
    );
  }

  @Patch(':id/tasks/:taskId')
  updateTaskStatus(
    @Param('id') teamId: string,
    @Param('taskId') taskId: string,
    @Body() body: { userId: string; status: string }
  ) {
    return this.teamService.updateTaskStatus(teamId, body.userId, taskId, body.status);
  }

  @Post(':id/messages')
  sendMessage(
    @Param('id') teamId: string,
    @Body() body: { userId: string; content: string }
  ) {
    return this.teamService.sendMessage(teamId, body.userId, body.content);
  }
}
