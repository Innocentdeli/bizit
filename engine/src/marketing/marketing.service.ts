import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class MarketingService {
  constructor(private prisma: PrismaService) {}

  // ─── Ad Campaigns ─────────────────────────────────────────────────────────
  async getAdCampaigns(userId: string) {
    return this.prisma.adCampaign.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async createAdCampaign(userId: string, data: any) {
    return this.prisma.adCampaign.create({
      data: {
        userId,
        name: data.name,
        platform: data.platform,
        budget: parseFloat(data.budget) || 0,
        status: data.status || 'draft',
        startDate: data.startDate ? new Date(data.startDate) : null,
        endDate: data.endDate ? new Date(data.endDate) : null,
        // Seed realistic mock metrics for demonstration
        impressions: Math.floor(Math.random() * 50000),
        clicks: Math.floor(Math.random() * 2000),
        conversions: Math.floor(Math.random() * 200),
        spent: parseFloat(data.budget) * (Math.random() * 0.7),
        revenue: parseFloat(data.budget) * (Math.random() * 3 + 1),
      },
    });
  }

  async updateAdCampaign(id: string, data: any) {
    return this.prisma.adCampaign.update({ where: { id }, data });
  }

  async deleteAdCampaign(id: string) {
    return this.prisma.adCampaign.delete({ where: { id } });
  }

  // ─── Email Campaigns ──────────────────────────────────────────────────────
  async getEmailCampaigns(userId: string) {
    return this.prisma.emailCampaign.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async createEmailCampaign(userId: string, data: any) {
    return this.prisma.emailCampaign.create({
      data: {
        userId,
        subject: data.subject,
        body: data.body,
        audience: data.audience || 'all',
        status: 'draft',
      },
    });
  }

  async sendEmailCampaign(id: string) {
    // In production: integrate with SendGrid/Mailchimp
    return this.prisma.emailCampaign.update({
      where: { id },
      data: {
        status: 'sent',
        sentAt: new Date(),
        opens: Math.floor(Math.random() * 800),
        clicks: Math.floor(Math.random() * 200),
      },
    });
  }

  // ─── Social Posts ─────────────────────────────────────────────────────────
  async getSocialPosts(userId: string) {
    return this.prisma.socialPost.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async createSocialPost(userId: string, data: any) {
    return this.prisma.socialPost.create({
      data: {
        userId,
        content: data.content,
        platforms: data.platforms,
        scheduledAt: data.scheduledAt ? new Date(data.scheduledAt) : null,
        status: data.scheduledAt ? 'scheduled' : 'draft',
        imageUrl: data.imageUrl || null,
      },
    });
  }

  async publishSocialPost(id: string) {
    return this.prisma.socialPost.update({
      where: { id },
      data: {
        status: 'published',
        publishedAt: new Date(),
        likes: Math.floor(Math.random() * 500),
        shares: Math.floor(Math.random() * 100),
      },
    });
  }

  async deleteSocialPost(id: string) {
    return this.prisma.socialPost.delete({ where: { id } });
  }
}
