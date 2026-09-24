import { Module } from '@nestjs/common';
import { BillingService } from './billing.service';
import { BillingController } from './billing.controller';
import { PrismaService } from '../prisma.service';
import { StripeService } from './providers/stripe.service';
import { PaystackService } from './providers/paystack.service';
import { FlutterwaveService } from './providers/flutterwave.service';

@Module({
  controllers: [BillingController],
  providers: [BillingService, PrismaService, StripeService, PaystackService, FlutterwaveService],
  exports: [BillingService],
})
export class BillingModule {}

