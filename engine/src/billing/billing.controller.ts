import {
  Controller, Get, Post, Body, Param, Req, Headers,
  HttpCode, Logger,
} from '@nestjs/common';
import type { RawBodyRequest } from '@nestjs/common';
import type { Request } from 'express';
import { BillingService } from './billing.service';

@Controller('billing')
export class BillingController {
  private readonly logger = new Logger(BillingController.name);

  constructor(private readonly billingService: BillingService) {}

  // ─── Plans ────────────────────────────────────────────────────────────────────

  @Get('plans')
  getPlans() {
    return this.billingService.getPlans();
  }

  // ─── Subscription ─────────────────────────────────────────────────────────────

  @Get('subscription/:userId')
  getSubscription(@Param('userId') userId: string) {
    return this.billingService.getSubscription(userId);
  }

  // ─── Invoices ─────────────────────────────────────────────────────────────────

  @Get('invoices/:userId')
  getInvoices(@Param('userId') userId: string) {
    return this.billingService.getInvoices(userId);
  }

  // ─── Coupon Validation ────────────────────────────────────────────────────────

  @Post('coupon/validate')
  validateCoupon(@Body() body: { code: string }) {
    return this.billingService.validateCoupon(body.code);
  }

  // ─── Checkout ─────────────────────────────────────────────────────────────────

  @Post('checkout')
  createCheckout(
    @Body() body: {
      userId: string;
      userEmail: string;
      userName: string;
      planId: string;
      provider: 'stripe' | 'paystack' | 'flutterwave';
      couponCode?: string;
    },
  ) {
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    return this.billingService.createCheckout({
      ...body,
      successUrl: `${baseUrl}/portal/billing?success=1`,
      cancelUrl: `${baseUrl}/portal/billing?canceled=1`,
    });
  }

  // ─── Stripe Customer Portal ───────────────────────────────────────────────────

  @Post('portal/:userId')
  createPortalSession(@Param('userId') userId: string) {
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    return this.billingService.createStripePortalSession(userId, `${baseUrl}/portal/billing`);
  }

  // ─── Webhooks ─────────────────────────────────────────────────────────────────

  @Post('webhook/stripe')
  @HttpCode(200)
  async stripeWebhook(
    @Req() req: RawBodyRequest<Request>,
    @Headers('stripe-signature') sig: string,
  ) {
    const raw = req.rawBody || Buffer.from(JSON.stringify(req.body));
    return this.billingService.handleStripeWebhook(raw, sig);
  }

  @Post('webhook/paystack')
  @HttpCode(200)
  async paystackWebhook(
    @Req() req: RawBodyRequest<Request>,
    @Headers('x-paystack-signature') hash: string,
  ) {
    const raw = req.rawBody?.toString() || JSON.stringify(req.body);
    return this.billingService.handlePaystackWebhook(raw, hash);
  }

  @Post('webhook/flutterwave')
  @HttpCode(200)
  async flutterwaveWebhook(
    @Req() req: RawBodyRequest<Request>,
    @Headers('verif-hash') hash: string,
  ) {
    const raw = req.rawBody?.toString() || JSON.stringify(req.body);
    return this.billingService.handleFlutterwaveWebhook(raw, hash);
  }
}
