import { Injectable, Logger } from '@nestjs/common';
import * as https from 'https';
import * as crypto from 'crypto';

@Injectable()
export class PaystackService {
  private readonly logger = new Logger(PaystackService.name);
  private secretKey: string | null;

  constructor() {
    this.secretKey = process.env.PAYSTACK_SECRET_KEY || null;
    if (this.secretKey) {
      this.logger.log('Paystack initialized with API key.');
    } else {
      this.logger.warn('PAYSTACK_SECRET_KEY not set — running in mock mode.');
    }
  }

  isMock() { return !this.secretKey; }

  async initializeTransaction(opts: {
    email: string;
    amount: number; // in kobo/pesewas (smallest unit)
    currency: string;
    callbackUrl: string;
    userId: string;
    planName: string;
  }): Promise<{ url: string; reference: string }> {
    if (this.isMock()) {
      const ref = 'mock_ps_' + Date.now();
      return { url: opts.callbackUrl + `?mock=1&provider=paystack&reference=${ref}`, reference: ref };
    }

    const data = JSON.stringify({
      email: opts.email,
      amount: Math.round(opts.amount * 100),
      currency: opts.currency.toUpperCase(),
      callback_url: opts.callbackUrl,
      metadata: { userId: opts.userId, planName: opts.planName },
    });

    return new Promise((resolve, reject) => {
      const req = https.request({
        hostname: 'api.paystack.co',
        port: 443,
        path: '/transaction/initialize',
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.secretKey}`,
          'Content-Type': 'application/json',
        },
      }, (res) => {
        let body = '';
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
          const parsed = JSON.parse(body);
          if (parsed.status) {
            resolve({ url: parsed.data.authorization_url, reference: parsed.data.reference });
          } else {
            reject(new Error(parsed.message));
          }
        });
      });
      req.on('error', reject);
      req.write(data);
      req.end();
    });
  }

  verifyWebhookSignature(payload: string, hash: string): boolean {
    if (!this.secretKey) return false;
    const computed = crypto.createHmac('sha512', this.secretKey).update(payload).digest('hex');
    return computed === hash;
  }
}
