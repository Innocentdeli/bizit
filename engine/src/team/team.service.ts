import { Injectable, Logger, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class TeamService {
  private readonly logger = new Logger(TeamService.name);

  constructor(private prisma: PrismaService) {}

  // ─── Team CRUD ──────────────────────────────────────────────────────────────

  async getUserTeams(userId: string) {
    return this.prisma.team.findMany({
      where: { members: { some: { userId } } },
      include: {
        members: { include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } } },
      },
    });
  }

  async getTeamDashboard(teamId: string, userId: string) {
    await this.verifyMember(teamId, userId);
    return this.prisma.team.findUnique({
      where: { id: teamId },
      include: {
        projects: { include: { tasks: { include: { assignee: { select: { id: true, firstName: true, lastName: true } } } } } },
        members: { include: { user: { select: { id: true, firstName: true, lastName: true, email: true } } } },
        messages: { include: { author: { select: { id: true, firstName: true, lastName: true } } }, orderBy: { createdAt: 'desc' }, take: 50 },
        activities: { include: { user: { select: { id: true, firstName: true, lastName: true } } }, orderBy: { createdAt: 'desc' }, take: 20 },
      },
    });
  }

  async createTeam(userId: string, name: string, description?: string) {
    const team = await this.prisma.team.create({
      data: {
        name,
        description,
        members: {
          create: { userId, role: 'admin' },
        },
      },
    });
    await this.logActivity(team.id, userId, `Created team "${name}"`, team.id);
    return team;
  }

  // ─── Team Members ───────────────────────────────────────────────────────────

  async addMember(teamId: string, adminId: string, email: string, role: string = 'member') {
    await this.verifyAdmin(teamId, adminId);
    
    // Lookup user by email
    const userToInvite = await this.prisma.user.findUnique({ where: { email } });
    if (!userToInvite) throw new NotFoundException('User with this email not found.');

    const member = await this.prisma.teamMember.create({
      data: { teamId, userId: userToInvite.id, role },
    });
    await this.logActivity(teamId, adminId, `Invited ${userToInvite.firstName} as ${role}`, userToInvite.id);
    return member;
  }

  // ─── Projects & Tasks ───────────────────────────────────────────────────────

  async createProject(teamId: string, userId: string, name: string, description?: string) {
    await this.verifyMember(teamId, userId); // Or verifyManager if stricter
    const project = await this.prisma.project.create({
      data: { teamId, name, description },
    });
    await this.logActivity(teamId, userId, `Created project "${name}"`, project.id);
    return project;
  }

  async createTask(teamId: string, userId: string, projectId: string, title: string, description?: string, assigneeId?: string, priority: string = 'medium', dueDate?: Date) {
    await this.verifyMember(teamId, userId);
    const task = await this.prisma.teamTask.create({
      data: { projectId, title, description, assigneeId, priority, dueDate },
    });
    await this.logActivity(teamId, userId, `Created task "${title}"`, task.id);
    return task;
  }

  async updateTaskStatus(teamId: string, userId: string, taskId: string, status: string) {
    await this.verifyMember(teamId, userId);
    const task = await this.prisma.teamTask.update({
      where: { id: taskId },
      data: { status },
    });
    await this.logActivity(teamId, userId, `Updated task "${task.title}" to ${status}`, task.id);
    return task;
  }

  // ─── Messaging ──────────────────────────────────────────────────────────────

  async sendMessage(teamId: string, userId: string, content: string) {
    await this.verifyMember(teamId, userId);
    return this.prisma.teamMessage.create({
      data: { teamId, authorId: userId, content },
    });
  }

  // ─── Helpers ────────────────────────────────────────────────────────────────

  private async verifyMember(teamId: string, userId: string) {
    const member = await this.prisma.teamMember.findUnique({
      where: { teamId_userId: { teamId, userId } },
    });
    if (!member) throw new ForbiddenException('You are not a member of this team.');
    return member;
  }

  private async verifyAdmin(teamId: string, userId: string) {
    const member = await this.verifyMember(teamId, userId);
    if (member.role !== 'admin' && member.role !== 'manager') {
      throw new ForbiddenException('Admin or manager privileges required.');
    }
    return member;
  }

  private async logActivity(teamId: string, userId: string, action: string, entityId?: string) {
    await this.prisma.teamActivity.create({
      data: { teamId, userId, action, entityId },
    });
  }
}
