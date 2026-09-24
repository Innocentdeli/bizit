import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class FlutterwaveService {
  private readonly logger = new Logger(FlutterwaveService.name);
  private secretKey: string | null;

  constructor() {
    this.secretKey = process.env.FLUTTERWAVE_SECRET_KEY || null;
    if (this.secretKey) {
      this.logger.log('Flutterwave initialized with API key.');
    } else {
      this.logger.warn('FLUTTERWAVE_SECRET_KEY not set — running in mock mode.');
    }
  }

  isMock() { return !this.secretKey; }

  async createPaymentLink(opts: {
    amount: number;
    currency: string;
    email: string;
    name: string;
    userId: string;
    planName: string;
    redirectUrl: string;
  }): Promise<{ url: string; txRef: string }> {
    const txRef = 'flw_' + Date.now() + '_' + opts.userId.slice(0, 8);
    if (this.isMock()) {
      return {
        url: opts.redirectUrl + `?mock=1&provider=flutterwave&tx_ref=${txRef}`,
        txRef,
      };
    }

    const response = await fetch('https://api.flutterwave.com/v3/payments', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.secretKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tx_ref: txRef,
        amount: opts.amount,
        currency: opts.currency.toUpperCase(),
        redirect_url: opts.redirectUrl,
        customer: { email: opts.email, name: opts.name },
        meta: { userId: opts.userId, planName: opts.planName },
        customizations: { title: 'BizIT Subscription', description: opts.planName },
      }),
    });
    const data = await response.json();
    if (data.status !== 'success') throw new Error(data.message);
    return { url: data.data.link, txRef };
  }

  verifyWebhookSignature(hash: string): boolean {
    if (!this.secretKey) return false;
    return hash === this.secretKey;
  }
}
