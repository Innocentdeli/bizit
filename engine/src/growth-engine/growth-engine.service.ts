import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class GrowthEngineService {
  constructor(private prisma: PrismaService) {}

  // ─── FUNNELS ─────────────────────────────────────────────
  async getFunnels(userId: string) {
    return this.prisma.funnel.findMany({
      where: { userId },
      include: { steps: { orderBy: { order: 'asc' } } },
    });
  }

  async createFunnel(userId: string, data: any) {
    const funnel = await this.prisma.funnel.create({
      data: {
        userId,
        name: data.name,
      },
    });

    if (data.steps && data.steps.length > 0) {
      await Promise.all(
        data.steps.map((step: any, index: number) =>
          this.prisma.funnelStep.create({
            data: {
              funnelId: funnel.id,
              order: index + 1,
              name: step.name,
              type: step.type,
              url: step.url,
            },
          }),
        ),
      );
    }
    return this.getFunnels(userId);
  }

  async deleteFunnel(id: string) {
    return this.prisma.funnel.delete({ where: { id } });
  }

  // ─── REFERRALS ───────────────────────────────────────────
  async getReferralLinks(userId: string) {
    return this.prisma.referralLink.findMany({ where: { userId } });
  }

  async createReferralLink(userId: string) {
    const code = Math.random().toString(36).substring(2, 10).toUpperCase();
    return this.prisma.referralLink.create({
      data: {
        userId,
        code,
        rewardAmount: 25.0, // Default reward
      },
    });
  }

  async trackReferralClick(code: string) {
    return this.prisma.referralLink.update({
      where: { code },
      data: { clicks: { increment: 1 } },
    });
  }

  // ─── RETENTION ───────────────────────────────────────────
  async getRetentionSequences(userId: string) {
    return this.prisma.retentionSequence.findMany({ where: { userId } });
  }

  async createRetentionSequence(userId: string, data: any) {
    return this.prisma.retentionSequence.create({
      data: {
        userId,
        name: data.name,
        trigger: data.trigger,
      },
    });
  }

  async deleteRetentionSequence(id: string) {
    return this.prisma.retentionSequence.delete({ where: { id } });
  }

  async toggleRetentionSequence(id: string) {
    const seq = await this.prisma.retentionSequence.findUnique({ where: { id } });
    if (!seq) return null;
    return this.prisma.retentionSequence.update({
      where: { id },
      data: { isActive: !seq.isActive },
    });
  }
}
