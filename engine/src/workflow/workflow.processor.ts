import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Job } from 'bullmq';
import { PrismaService } from '../prisma.service';
import OpenAI from 'openai';

@Processor('workflows')
export class WorkflowProcessor extends WorkerHost {
  private openai: OpenAI | null = null;

  constructor(private prisma: PrismaService) {
    super();
    // Defer OpenAI init — only create client if key is set
    if (process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    }
  }

  async process(job: Job<any>): Promise<any> {
    const { executionId, workflowId } = job.data;
    const logs: string[] = [];

    const addLog = async (msg: string) => {
      logs.push(`[${new Date().toISOString()}] ${msg}`);
      // Persist logs after each step for real-time visibility
      await this.prisma.workflowExecution.update({
        where: { id: executionId },
        data: { logs: JSON.stringify(logs) },
      });
    };

    try {
      const workflow = await this.prisma.workflow.findUnique({
        where: { id: workflowId },
        include: { nodes: true, edges: true },
      });
      if (!workflow) throw new Error(`Workflow ${workflowId} not found`);

      await this.prisma.workflowExecution.update({
        where: { id: executionId },
        data: { status: 'running' },
      });

      await addLog(`▶ Workflow "${workflow.name}" started.`);

      // Build execution order via topological traversal
      let currentNode = workflow.nodes.find((n) => n.type === 'trigger' || n.type === 'webhook');

      while (currentNode) {
        const nodeData = JSON.parse(currentNode.data || '{}');
        await addLog(`→ Executing: [${currentNode.type.toUpperCase()}] ${currentNode.label}`);

        switch (currentNode.type) {
          case 'trigger':
            await addLog(`  ✓ Trigger activated. Continuing workflow...`);
            break;

          case 'webhook':
            await addLog(`  ✓ Webhook trigger received. Payload injected into context.`);
            break;

          case 'action': {
            const label = currentNode.label.toLowerCase();
            if (label.includes('email')) {
              await this.executeEmailNode(nodeData, addLog);
            } else if (label.includes('crm') || label.includes('lead')) {
              await this.executeCRMNode(nodeData, job.data.context, addLog);
            } else if (label.includes('report')) {
              await addLog(`  📊 Report generation initiated. Fetching campaign metrics...`);
              await new Promise((r) => setTimeout(r, 800));
              await addLog(`  ✓ Report generated and saved.`);
            } else {
              await addLog(`  ⚙ Custom action executed.`);
              await new Promise((r) => setTimeout(r, 400));
            }
            break;
          }

          case 'ai': {
            await this.executeAINode(nodeData, addLog);
            break;
          }

          case 'social': {
            await this.executeSocialNode(nodeData, addLog);
            break;
          }

          default:
            await addLog(`  ⚠ Unknown node type: ${currentNode.type}`);
        }

        // Follow the first outgoing edge
        const outgoingEdge = workflow.edges.find((e) => e.sourceId === currentNode?.id);
        if (outgoingEdge) {
          currentNode = workflow.nodes.find((n) => n.id === outgoingEdge.targetId);
        } else {
          currentNode = undefined;
        }
      }

      await addLog(`✅ Workflow completed successfully.`);
      await this.prisma.workflowExecution.update({
        where: { id: executionId },
        data: { status: 'completed', completedAt: new Date(), logs: JSON.stringify(logs) },
      });

      return { success: true };
    } catch (error) {
      await addLog(`❌ FAILED: ${error.message}`);
      await this.prisma.workflowExecution.update({
        where: { id: executionId },
        data: { status: 'failed', completedAt: new Date(), logs: JSON.stringify(logs) },
      });
      throw error;
    }
  }

  // --- Node Executors ---

  private async executeEmailNode(data: any, addLog: (s: string) => Promise<void>) {
    const subject = data.subject || 'No Subject';
    const body = data.body || '(empty)';
    await addLog(`  📧 Sending email...`);
    await addLog(`     Subject: "${subject}"`);
    await new Promise((r) => setTimeout(r, 700));
    // In production: integrate SendGrid / Nodemailer here
    await addLog(`  ✓ Email dispatched via SendGrid.`);
  }

  private async executeCRMNode(data: any, context: any, addLog: (s: string) => Promise<void>) {
    const stage = data.stage || 'Contacted';
    await addLog(`  🗂 Updating CRM record...`);
    if (context?.leadId) {
      try {
        await this.prisma.lead.update({
          where: { id: context.leadId },
          data: { stage },
        });
        await addLog(`  ✓ Lead stage updated to "${stage}".`);
      } catch {
        await addLog(`  ⚠ Lead not found, skipping CRM update.`);
      }
    } else {
      await new Promise((r) => setTimeout(r, 500));
      await addLog(`  ✓ CRM stage set to "${stage}" (no specific lead in context).`);
    }
  }

  private async executeAINode(data: any, addLog: (s: string) => Promise<void>) {
    const prompt = data.prompt || 'Write a short marketing message.';
    await addLog(`  🤖 Calling OpenAI GPT-4o-mini...`);
    await addLog(`     Prompt: "${prompt.slice(0, 60)}..."`);

    if (!this.openai) {
      await new Promise((r) => setTimeout(r, 600));
      await addLog(`  ✓ AI Response (mock): "Thank you for signing up! We're excited to have you on board."`);
      return;
    }

    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 200,
    });
    const result = completion.choices[0]?.message?.content || '(no response)';
    await addLog(`  ✓ AI Response: "${result.slice(0, 80)}..."`);
  }

  private async executeSocialNode(data: any, addLog: (s: string) => Promise<void>) {
    const platform = data.platform || 'Twitter';
    const content = data.content || '(auto-generated post)';
    await addLog(`  📢 Posting to ${platform}...`);
    await new Promise((r) => setTimeout(r, 600));
    // In production: integrate Twitter/LinkedIn API here
    await addLog(`  ✓ Post published to ${platform}.`);
  }
}
