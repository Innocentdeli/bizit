import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { Cron, CronExpression } from '@nestjs/schedule';
import OpenAI from 'openai';

@Injectable()
export class ReportingService {
  private readonly logger = new Logger(ReportingService.name);
  private openai: OpenAI;

  constructor(private prisma: PrismaService) {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY || 'sk-mock-key-for-dev',
    });
  }

  async getClients() {
    return this.prisma.client.findMany({ orderBy: { createdAt: 'desc' } });
  }

  async createClient(data: { name: string; companyName: string; logoUrl?: string; primaryColor?: string }) {
    return this.prisma.client.create({ data });
  }

  async getReportHistory(clientId: string) {
    return this.prisma.report.findMany({
      where: { clientId },
      orderBy: { date: 'desc' },
    });
  }

  async getSchedule(clientId: string) {
    let schedule = await this.prisma.reportSchedule.findFirst({
      where: { clientId },
    });
    if (!schedule) {
      // Create a default inactive schedule if none exists
      schedule = await this.prisma.reportSchedule.create({
        data: {
          clientId,
          frequency: 'weekly',
          emailTo: '',
          isActive: false,
        },
      });
    }
    return schedule;
  }

  async updateSchedule(clientId: string, data: { frequency: string; emailTo: string; isActive: boolean }) {
    const schedule = await this.getSchedule(clientId);
    return this.prisma.reportSchedule.update({
      where: { id: schedule.id },
      data,
    });
  }

  async generateReport(clientId: string) {
    this.logger.log(`Generating manual report for client: ${clientId}`);
    
    // 1. Gather mocked/aggregated data
    // In a real app, we'd query CampaignMetric and summarize it.
    const metricsData = {
      spend: 12500,
      impressions: 450000,
      clicks: 12500,
      conversions: 850,
      revenue: 45000,
      funnel: [
        { stage: 'Impressions', value: 450000 },
        { stage: 'Clicks', value: 12500 },
        { stage: 'Leads', value: 2500 },
        { stage: 'Conversions', value: 850 },
      ]
    };

    // 2. Generate AI Insights
    let aiInsights;
    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'You are an expert marketing analyst. Generate a JSON object containing "executiveSummary", "recommendations", "growthInsights", and "nextActions" based on the provided metrics. Each field should be a short paragraph or bullet points.'
          },
          {
            role: 'user',
            content: JSON.stringify(metricsData)
          }
        ],
        response_format: { type: "json_object" }
      });
      aiInsights = JSON.parse(response.choices[0].message.content || '{}');
    } catch (e) {
      this.logger.warn(`Failed to generate AI insights: ${e.message}. Using fallback data.`);
      aiInsights = {
        executiveSummary: "Campaigns performed well this period with a strong ROAS.",
        recommendations: "Scale budget on top performing ad sets.",
        growthInsights: "CPC decreased by 15% WoW.",
        nextActions: "Launch retargeting campaign next week."
      };
    }

    // 3. Save Report
    const report = await this.prisma.report.create({
      data: {
        clientId,
        metricsData: JSON.stringify(metricsData),
        aiInsights: JSON.stringify(aiInsights),
        status: 'generated'
      }
    });

    return report;
  }

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async handleScheduledReports() {
    this.logger.log('Checking for scheduled reports...');
    const schedules = await this.prisma.reportSchedule.findMany({
      where: { isActive: true },
    });

    for (const schedule of schedules) {
      // Basic check: if weekly, only run on Mondays (day 1)
      const today = new Date();
      if (schedule.frequency === 'weekly' && today.getDay() !== 1) {
        continue;
      }
      // If monthly, only run on the 1st
      if (schedule.frequency === 'monthly' && today.getDate() !== 1) {
        continue;
      }

      try {
        const report = await this.generateReport(schedule.clientId);
        
        // Update status to sent
        await this.prisma.report.update({
          where: { id: report.id },
          data: { status: 'sent' }
        });

        // Mock Email Delivery
        this.logger.log(`[EMAIL] Sending report to ${schedule.emailTo} for client ${schedule.clientId}. Link: /portal/reporting?client=${schedule.clientId}&report=${report.id}`);
      } catch (e) {
        this.logger.error(`Error generating scheduled report for client ${schedule.clientId}: ${e.message}`);
      }
    }
  }
}
