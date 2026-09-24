import { Injectable, UnauthorizedException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class AdminService {
  constructor(private prisma: PrismaService) {}

  async verifySuperAdmin(userId: string) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new UnauthorizedException('User not found');
    if (user.role !== 'SuperAdmin') throw new ForbiddenException('SuperAdmin privileges required');
    return user;
  }

  async getPlatformStats(adminId: string) {
    await this.verifySuperAdmin(adminId);

    const [totalUsers, activeSubscriptions, invoices, systemLogs] = await Promise.all([
      this.prisma.user.count(),
      this.prisma.subscription.count({ where: { status: 'active' } }),
      this.prisma.invoice.findMany({ where: { status: 'paid' }, select: { amount: true } }),
      this.prisma.systemLog.count({ where: { category: 'ai_usage' } }),
    ]);

    const mrr = invoices.reduce((sum, inv) => sum + inv.amount, 0) / 100; // Assuming amounts are in cents

    return {
      totalUsers,
      activeSubscriptions,
      mrr,
      aiOperations: systemLogs,
    };
  }

  async getUsers(adminId: string) {
    await this.verifySuperAdmin(adminId);
    return this.prisma.user.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100, // Limiting for dashboard view
    });
  }

  async updateUserRole(adminId: string, targetUserId: string, newRole: string) {
    await this.verifySuperAdmin(adminId);
    
    const user = await this.prisma.user.update({
      where: { id: targetUserId },
      data: { role: newRole },
    });

    await this.logSystemEvent('audit', 'system', `Admin ${adminId} changed user ${targetUserId} role to ${newRole}`);
    return user;
  }

  async getSubscriptions(adminId: string) {
    await this.verifySuperAdmin(adminId);
    return this.prisma.subscription.findMany({
      include: { user: { select: { email: true, firstName: true, lastName: true } } },
      orderBy: { createdAt: 'desc' },
      take: 100,
    });
  }

  async getSystemLogs(adminId: string, category?: string) {
    await this.verifySuperAdmin(adminId);
    return this.prisma.systemLog.findMany({
      where: category && category !== 'all' ? { category } : undefined,
      orderBy: { createdAt: 'desc' },
      take: 200,
    });
  }

  async logSystemEvent(level: string, category: string, message: string, metadata?: any) {
    const data: any = { level, category, message };
    if (metadata) {
      data.metadata = metadata;
    }

    return this.prisma.systemLog.create({ data });
  }
}
