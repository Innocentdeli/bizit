import { Injectable, Logger, BadRequestException, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { StripeService } from './providers/stripe.service';
import { PaystackService } from './providers/paystack.service';
import { FlutterwaveService } from './providers/flutterwave.service';

@Injectable()
export class BillingService {
  private readonly logger = new Logger(BillingService.name);

  constructor(
    private prisma: PrismaService,
    private stripeService: StripeService,
    private paystackService: PaystackService,
    private flutterwaveService: FlutterwaveService,
  ) {}

  // ─── Plans ──────────────────────────────────────────────────────────────────

  async getPlans() {
    const plans = await this.prisma.subscriptionPlan.findMany({ orderBy: { price: 'asc' } });
    return plans.map(p => ({ ...p, features: JSON.parse(p.features) }));
  }

  async seedDefaultPlans() {
    const count = await this.prisma.subscriptionPlan.count();
    if (count > 0) return;
    await this.prisma.subscriptionPlan.createMany({
      data: [
        {
          name: 'Starter', price: 0, currency: 'usd', interval: 'month',
          description: 'Perfect for individuals and small teams.',
          features: JSON.stringify(['5 Campaigns', '10 Reports/month', 'Community Access', '1GB Storage']),
        },
        {
          name: 'Growth', price: 49, currency: 'usd', interval: 'month',
          description: 'For growing marketing teams.',
          features: JSON.stringify(['Unlimited Campaigns', '100 Reports/month', 'AI Insights', '10GB Storage', 'Priority Support', 'White-label Reports']),
        },
        {
          name: 'Scale', price: 149, currency: 'usd', interval: 'month',
          description: 'For agencies and large teams.',
          features: JSON.stringify(['Everything in Growth', 'Unlimited Reports', 'Custom Integrations', 'Dedicated Account Manager', 'SLA Guarantee', 'Multi-workspace']),
        },
        {
          name: 'Growth Annual', price: 470, currency: 'usd', interval: 'year',
          description: 'Growth plan — billed annually (save 20%).',
          features: JSON.stringify(['Everything in Growth', 'Annual billing discount', 'Priority onboarding']),
        },
      ],
    });
    this.logger.log('Seeded default subscription plans.');
  }

  // ─── Subscription ────────────────────────────────────────────────────────────

  async getSubscription(userId: string) {
    return this.prisma.subscription.findFirst({
      where: { userId, status: { in: ['active', 'past_due', 'incomplete'] } },
      include: { plan: true },
      orderBy: { createdAt: 'desc' },
    });
  }

  // ─── Coupons ─────────────────────────────────────────────────────────────────

  async validateCoupon(code: string) {
    const coupon = await this.prisma.coupon.findUnique({ where: { code } });
    if (!coupon || !coupon.isActive) throw new BadRequestException('Invalid or expired coupon code.');
    if (coupon.maxUses && coupon.timesUsed >= coupon.maxUses) throw new BadRequestException('Coupon has reached its usage limit.');
    return coupon;
  }

  applyDiscount(price: number, coupon: { percentOff?: number | null; amountOff?: number | null }): number {
    if (coupon.percentOff) return price * (1 - coupon.percentOff / 100);
    if (coupon.amountOff) return Math.max(0, price - coupon.amountOff);
    return price;
  }

  // ─── Checkout ────────────────────────────────────────────────────────────────

  async createCheckout(opts: {
    userId: string;
    userEmail: string;
    userName: string;
    planId: string;
    provider: 'stripe' | 'paystack' | 'flutterwave';
    couponCode?: string;
    successUrl: string;
    cancelUrl: string;
  }) {
    const plan = await this.prisma.subscriptionPlan.findUnique({ where: { id: opts.planId } });
    if (!plan) throw new NotFoundException('Plan not found.');

    let finalPrice = plan.price;
    let coupon: any = null;
    if (opts.couponCode) {
      coupon = await this.validateCoupon(opts.couponCode);
      finalPrice = this.applyDiscount(finalPrice, coupon);
    }

    // For free plan — auto-subscribe
    if (finalPrice === 0) {
      const sub = await this.prisma.subscription.create({
        data: {
          userId: opts.userId, planId: opts.planId,
          status: 'active', provider: 'none',
          currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        },
      });
      if (coupon) await this.prisma.coupon.update({ where: { id: coupon.id }, data: { timesUsed: { increment: 1 } } });
      return { type: 'free', subscriptionId: sub.id };
    }

    if (opts.provider === 'stripe') {
      const { url, sessionId } = await this.stripeService.createCheckoutSession({
        planName: plan.name, priceUnitAmount: finalPrice,
        currency: plan.currency, interval: plan.interval as 'month' | 'year',
        userId: opts.userId, successUrl: opts.successUrl, cancelUrl: opts.cancelUrl,
      });
      return { type: 'redirect', url, sessionId, provider: 'stripe' };
    }

    if (opts.provider === 'paystack') {
      const { url, reference } = await this.paystackService.initializeTransaction({
        email: opts.userEmail, amount: finalPrice,
        currency: plan.currency, callbackUrl: opts.successUrl,
        userId: opts.userId, planName: plan.name,
      });
      return { type: 'redirect', url, reference, provider: 'paystack' };
    }

    if (opts.provider === 'flutterwave') {
      const { url, txRef } = await this.flutterwaveService.createPaymentLink({
        amount: finalPrice, currency: plan.currency,
        email: opts.userEmail, name: opts.userName,
        userId: opts.userId, planName: plan.name,
        redirectUrl: opts.successUrl,
      });
      return { type: 'redirect', url, txRef, provider: 'flutterwave' };
    }

    throw new BadRequestException('Invalid payment provider.');
  }

  // ─── Invoices ────────────────────────────────────────────────────────────────

  async getInvoices(userId: string) {
    return this.prisma.invoice.findMany({
      where: { userId },
      include: { payments: true, subscription: { include: { plan: true } } },
      orderBy: { createdAt: 'desc' },
    });
  }

  // ─── Webhook Handlers ────────────────────────────────────────────────────────

  async handleStripeWebhook(payload: Buffer, sig: string) {
    const event = this.stripeService.constructEvent(payload, sig);
    if (!event) {
      this.logger.warn('Received invalid Stripe webhook.');
      return { ok: false };
    }

    this.logger.log(`Stripe event received: ${event.type}`);

    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as any;
        const userId = session.client_reference_id;
        if (!userId) break;

        await this.prisma.subscription.updateMany({
          where: { userId, status: 'incomplete' },
          data: { status: 'active', providerSubscriptionId: session.subscription },
        });
        break;
      }
      case 'invoice.payment_succeeded': {
        const inv = event.data.object as any;
        const userId = inv.client_reference_id || inv.customer_email;
        if (!userId) break;

        const sub = await this.prisma.subscription.findFirst({ where: { providerSubscriptionId: inv.subscription } });
        if (sub) {
          const dbInvoice = await this.prisma.invoice.create({
            data: {
              userId: sub.userId,
              subscriptionId: sub.id,
              amount: inv.amount_paid / 100,
              currency: inv.currency,
              status: 'paid',
              pdfUrl: inv.invoice_pdf,
            },
          });
          await this.prisma.payment.create({
            data: {
              invoiceId: dbInvoice.id,
              amount: inv.amount_paid / 100,
              provider: 'stripe',
              status: 'succeeded',
              transactionId: inv.id,
            },
          });
        }
        break;
      }
      case 'invoice.payment_failed': {
        const inv = event.data.object as any;
        const sub = await this.prisma.subscription.findFirst({ where: { providerSubscriptionId: inv.subscription } });
        if (sub) {
          await this.prisma.subscription.update({ where: { id: sub.id }, data: { status: 'past_due' } });
          this.logger.warn(`Subscription ${sub.id} set to past_due after failed payment.`);
        }
        break;
      }
      case 'customer.subscription.deleted': {
        const stripeSub = event.data.object as any;
        await this.prisma.subscription.updateMany({
          where: { providerSubscriptionId: stripeSub.id },
          data: { status: 'canceled' },
        });
        break;
      }
    }
    return { ok: true };
  }

  async handlePaystackWebhook(payload: string, hash: string) {
    if (!this.paystackService.verifyWebhookSignature(payload, hash)) {
      this.logger.warn('Invalid Paystack webhook signature.');
      return { ok: false };
    }
    const event = JSON.parse(payload);
    this.logger.log(`Paystack event: ${event.event}`);

    if (event.event === 'charge.success') {
      const { reference, amount, currency, metadata } = event.data;
      const userId = metadata?.userId;
      if (!userId) return { ok: false };

      const sub = await this.prisma.subscription.findFirst({ where: { userId, status: 'incomplete' } });
      if (sub) {
        await this.prisma.subscription.update({ where: { id: sub.id }, data: { status: 'active', providerSubscriptionId: reference } });
        const dbInvoice = await this.prisma.invoice.create({
          data: { userId, subscriptionId: sub.id, amount: amount / 100, currency, status: 'paid' },
        });
        await this.prisma.payment.create({
          data: { invoiceId: dbInvoice.id, amount: amount / 100, provider: 'paystack', status: 'succeeded', transactionId: reference },
        });
      }
    }
    return { ok: true };
  }

  async handleFlutterwaveWebhook(payload: string, hash: string) {
    if (!this.flutterwaveService.verifyWebhookSignature(hash)) {
      this.logger.warn('Invalid Flutterwave webhook signature.');
      return { ok: false };
    }
    const event = JSON.parse(payload);
    this.logger.log(`Flutterwave event: ${event.event}`);

    if (event.event === 'charge.completed' && event.data.status === 'successful') {
      const { id, amount, currency, meta } = event.data;
      const userId = meta?.userId;
      if (!userId) return { ok: false };

      const sub = await this.prisma.subscription.findFirst({ where: { userId, status: 'incomplete' } });
      if (sub) {
        await this.prisma.subscription.update({ where: { id: sub.id }, data: { status: 'active', providerSubscriptionId: String(id) } });
        const dbInvoice = await this.prisma.invoice.create({
          data: { userId, subscriptionId: sub.id, amount, currency, status: 'paid' },
        });
        await this.prisma.payment.create({
          data: { invoiceId: dbInvoice.id, amount, provider: 'flutterwave', status: 'succeeded', transactionId: String(id) },
        });
      }
    }
    return { ok: true };
  }

  // ─── Stripe Portal ────────────────────────────────────────────────────────────

  async createStripePortalSession(userId: string, returnUrl: string) {
    const sub = await this.prisma.subscription.findFirst({
      where: { userId, provider: 'stripe' },
      orderBy: { createdAt: 'desc' },
    });
    const customerId = sub?.providerSubscriptionId || 'mock_customer';
    return this.stripeService.createPortalSession(customerId, returnUrl);
  }
}
