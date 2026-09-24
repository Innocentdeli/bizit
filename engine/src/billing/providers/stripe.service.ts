import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class StripeService {
  private readonly logger = new Logger(StripeService.name);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private stripe: any = null;

  constructor() {
    const key = process.env.STRIPE_SECRET_KEY;
    if (key) {
      // Dynamic require to avoid TS namespace issues with newer Stripe package
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const Stripe = require('stripe');
      this.stripe = new Stripe(key);
      this.logger.log('Stripe initialized with live API key.');
    } else {
      this.logger.warn('STRIPE_SECRET_KEY not set — running in mock mode.');
    }
  }

  isMock() {
    return !this.stripe;
  }

  async createCheckoutSession(opts: {
    planName: string;
    priceUnitAmount: number;
    currency: string;
    interval: 'month' | 'year';
    userId: string;
    successUrl: string;
    cancelUrl: string;
  }): Promise<{ url: string; sessionId: string }> {
    if (this.isMock()) {
      return {
        url: opts.successUrl + '?mock=1&provider=stripe',
        sessionId: 'mock_session_' + Date.now(),
      };
    }
    const session = await this.stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: opts.currency,
            product_data: { name: opts.planName },
            unit_amount: Math.round(opts.priceUnitAmount * 100),
            recurring: { interval: opts.interval },
          },
          quantity: 1,
        },
      ],
      client_reference_id: opts.userId,
      success_url: opts.successUrl,
      cancel_url: opts.cancelUrl,
    });
    return { url: session.url, sessionId: session.id };
  }

  async createPortalSession(customerId: string, returnUrl: string): Promise<string> {
    if (this.isMock()) return returnUrl;
    const session = await this.stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl,
    });
    return session.url;
  }

  constructEvent(payload: Buffer, sig: string): any | null {
    const secret = process.env.STRIPE_WEBHOOK_SECRET;
    if (!this.stripe || !secret) return null;
    try {
      return this.stripe.webhooks.constructEvent(payload, sig, secret);
    } catch (e) {
      this.logger.error(`Stripe webhook verification failed: ${e.message}`);
      return null;
    }
  }
}
