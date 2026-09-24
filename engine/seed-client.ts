import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  await prisma.client.create({
    data: {
      name: 'Acme Corp Marketing',
      companyName: 'Acme Corp',
      logoUrl: 'https://logo.clearbit.com/acme.com',
      primaryColor: '#8b5cf6', // Violet
    },
  });
  console.log('Seeded Acme Corp client');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
