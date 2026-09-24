import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { BillingService } from './billing/billing.service';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { rawBody: true });
  app.enableCors(); // Allow Next.js to call it
  await app.listen(process.env.PORT ?? 3001);

  // Seed default subscription plans on startup
  const billingService = app.get(BillingService);
  await billingService.seedDefaultPlans();
}
bootstrap();
