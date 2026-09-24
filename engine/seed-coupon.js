require('dotenv').config();
const { PrismaClient } = require('@prisma/client');
const { Pool } = require('pg');
const { PrismaPg } = require('@prisma/adapter-pg');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
  const coupon = await prisma.coupon.upsert({
    where: { code: 'LAUNCH20' },
    update: {},
    create: { code: 'LAUNCH20', percentOff: 20, maxUses: 100, isActive: true },
  });
  console.log('✓ Coupon ready:', coupon.code, '-', coupon.percentOff + '% off, max', coupon.maxUses, 'uses');

  const coupon2 = await prisma.coupon.upsert({
    where: { code: 'FLAT10' },
    update: {},
    create: { code: 'FLAT10', amountOff: 10, maxUses: 50, isActive: true },
  });
  console.log('✓ Coupon ready:', coupon2.code, '- $' + coupon2.amountOff + ' off, max', coupon2.maxUses, 'uses');
}

main().catch(console.error).finally(() => prisma.$disconnect());
