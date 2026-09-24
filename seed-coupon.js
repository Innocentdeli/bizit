// Seed a demo coupon into the DB via Prisma
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient({
  datasources: { db: { url: process.env.DATABASE_URL } },
});

async function main() {
  const existing = await prisma.coupon.findUnique({ where: { code: 'LAUNCH20' } });
  if (existing) { console.log('Coupon LAUNCH20 already exists.'); return; }
  const coupon = await prisma.coupon.create({
    data: {
      code: 'LAUNCH20',
      percentOff: 20,
      maxUses: 100,
      isActive: true,
    },
  });
  console.log('Created coupon:', coupon);
}
main().catch(console.error).finally(() => prisma.$disconnect());
