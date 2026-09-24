import { Injectable, Logger, InternalServerErrorException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import OpenAI from 'openai';

@Injectable()
export class GrowthService {
  private readonly logger = new Logger(GrowthService.name);
  private openai: OpenAI | null = null;

  constructor(private prisma: PrismaService) {
    if (process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    } else {
      this.logger.warn('OPENAI_API_KEY is not set. Growth Service will run in mock mode.');
    }
  }

  async getUserStrategies(userId: string) {
    return this.prisma.growthStrategy.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getStrategyById(id: string, userId: string) {
    return this.prisma.growthStrategy.findFirst({
      where: { id, userId },
    });
  }

  async generateStrategy(
    userId: string,
    payload: {
      businessType: string;
      industry: string;
      revenueModel: string;
      audience: string;
      currentMetrics: string;
    }
  ) {
    let aiResponse;

    if (!this.openai) {
      // Mock mode fallback
      aiResponse = {
        actionPlan: [
          { title: 'Launch MVP', description: 'Deploy core features to gather feedback.', impact: 'High', effort: 'Medium' },
          { title: 'Setup Analytics', description: 'Implement Mixpanel and GA4.', impact: 'High', effort: 'Low' }
        ],
        funnelImprovements: [
          { stage: 'Acquisition', recommendation: 'A/B test landing page headlines.' },
          { stage: 'Activation', recommendation: 'Simplify onboarding flow by removing 2 steps.' }
        ],
        viralLoops: [
          { idea: 'Referral Program', mechanism: 'Give $10 credit for every friend invited.' }
        ],
        acquisitionChannels: [
          { channel: 'Content SEO', priority: 1, strategy: 'Publish "How-To" guides for your niche.' },
          { channel: 'LinkedIn Outreach', priority: 2, strategy: 'Target decision-makers with cold DMs.' }
        ]
      };
      
      // Artificial delay for UX
      await new Promise(resolve => setTimeout(resolve, 2000));
    } else {
      try {
        const prompt = `You are an elite, world-class startup growth consultant and strategist.
Your task is to analyze the following business profile and generate a comprehensive, highly actionable growth strategy.

Business Profile:
- Business Type: ${payload.businessType}
- Industry: ${payload.industry}
- Revenue Model: ${payload.revenueModel}
- Target Audience: ${payload.audience}
- Current Metrics: ${payload.currentMetrics}

Respond ONLY with a valid JSON object matching this exact schema:
{
  "actionPlan": [ { "title": "string", "description": "string", "impact": "High/Medium/Low", "effort": "High/Medium/Low" } ],
  "funnelImprovements": [ { "stage": "string", "recommendation": "string" } ],
  "viralLoops": [ { "idea": "string", "mechanism": "string" } ],
  "acquisitionChannels": [ { "channel": "string", "priority": number, "strategy": "string" } ]
}`;

        const response = await this.openai.chat.completions.create({
          model: 'gpt-4o',
          messages: [{ role: 'user', content: prompt }],
          response_format: { type: 'json_object' },
        });

        const content = response.choices[0].message.content;
        aiResponse = JSON.parse(content || '{}');
      } catch (error) {
        this.logger.error('Failed to generate growth strategy with OpenAI', error);
        throw new InternalServerErrorException('Failed to generate growth strategy.');
      }
    }

    // Save to database
    const strategy = await this.prisma.growthStrategy.create({
      data: {
        userId,
        businessType: payload.businessType,
        industry: payload.industry,
        revenueModel: payload.revenueModel,
        audience: payload.audience,
        currentMetrics: payload.currentMetrics,
        actionPlan: aiResponse.actionPlan || [],
        funnelImprovements: aiResponse.funnelImprovements || [],
        viralLoops: aiResponse.viralLoops || [],
        acquisitionChannels: aiResponse.acquisitionChannels || [],
      },
    });

    // Log AI Usage
    await this.prisma.systemLog.create({
      data: {
        level: 'info',
        category: 'ai_usage',
        message: `Generated growth strategy for ${payload.businessType}`,
        metadata: JSON.stringify({ userId, feature: 'growth_strategist' }),
      }
    });

    return strategy;
  }
}
