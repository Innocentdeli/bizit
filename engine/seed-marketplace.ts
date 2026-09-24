/**
 * Seeds realistic marketplace data so the new /marketplace/* endpoints
 * (see src/marketplace) return real, DB-backed numbers instead of the
 * hardcoded arrays the dima Marketplace portal used to ship with.
 *
 * Run with: npx ts-node seed-marketplace.ts
 */
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const CATEGORIES = ['Electronics', 'Fashion', 'Home & Living', 'Sports', 'Books', 'Beauty'];
const CITIES = [
  'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin',
];
const VENDOR_STATUSES = ['applied', 'verified', 'onboarded', 'listed', 'selling'];

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function monthsAgo(n: number, dayOfMonth = 1): Date {
  const d = new Date();
  d.setMonth(d.getMonth() - n, dayOfMonth);
  return d;
}

async function main() {
  const existingVendors = await prisma.vendor.count();
  if (existingVendors > 0) {
    console.log(`Marketplace already seeded (${existingVendors} vendors). Skipping.`);
    return;
  }

  // ─── Vendors ────────────────────────────────────────────────────────────────
  const vendors = [];
  for (let i = 0; i < 240; i++) {
    // Weight status distribution so the funnel below has a realistic shape.
    const roll = Math.random();
    const status =
      roll < 0.15 ? 'applied' :
      roll < 0.3 ? 'verified' :
      roll < 0.5 ? 'onboarded' :
      roll < 0.75 ? 'listed' : 'selling';

    const monthOffset = Math.floor(Math.random() * 12);
    const vendor = await prisma.vendor.create({
      data: {
        userId: `seed-vendor-${i}`,
        name: `Vendor ${i + 1}`,
        category: pick(CATEGORIES),
        city: pick(CITIES),
        status,
        verified: status !== 'applied',
        createdAt: monthsAgo(monthOffset, 1 + Math.floor(Math.random() * 27)),
      },
    });
    vendors.push(vendor);
  }
  console.log(`Seeded ${vendors.length} vendors.`);

  // ─── Referral links (reuses the existing ReferralLink model) ───────────────
  const referrers = [
    { name: 'Sarah K.', signups: 61, clicks: 84 },
    { name: 'Marcus T.', signups: 53, clicks: 72 },
    { name: 'Priya M.', signups: 49, clicks: 68 },
    { name: 'James O.', signups: 44, clicks: 61 },
    { name: 'Emily R.', signups: 38, clicks: 55 },
  ];
  const referralLinks = [];
  for (const [i, r] of referrers.entries()) {
    const link = await prisma.referralLink.upsert({
      where: { code: `SEED-REF-${i}` },
      update: {},
      create: {
        userId: `seed-referrer-${i}`,
        code: `SEED-REF-${i}`,
        clicks: r.clicks,
        signups: r.signups,
        rewardAmount: 25,
        status: 'active',
      },
    });
    referralLinks.push({ ...link, name: r.name });
  }
  console.log(`Seeded ${referralLinks.length} referral links.`);

  // ─── Orders (drives GMV, acquisition, liquidity, cohort, referral trend) ──
  const sellingVendors = vendors.filter((v) => v.status === 'selling' || v.status === 'listed');
  let orderCount = 0;
  for (let m = 11; m >= 0; m--) {
    // Grow order volume over the trailing 12 months.
    const ordersThisMonth = 120 + Math.round((11 - m) * 22 + Math.random() * 30);
    for (let j = 0; j < ordersThisMonth; j++) {
      const vendor = pick(sellingVendors.length > 0 ? sellingVendors : vendors);
      const day = 1 + Math.floor(Math.random() * 27);
      const useReferral = Math.random() < 0.28;
      await prisma.marketplaceOrder.create({
        data: {
          buyerId: `seed-buyer-${m}-${Math.floor(j / 3)}`, // a few repeat buyers per month for cohort math
          buyerCity: pick(CITIES),
          vendorId: vendor.id,
          category: vendor.category,
          amount: Math.round((30 + Math.random() * 300) * 100) / 100,
          referralCode: useReferral ? pick(referralLinks).code : null,
          createdAt: monthsAgo(m, day),
        },
      });
      orderCount++;
    }
  }
  console.log(`Seeded ${orderCount} marketplace orders.`);

  // ─── Reviews (drives trust metrics) ────────────────────────────────────────
  let reviewCount = 0;
  for (const vendor of vendors) {
    const n = Math.floor(Math.random() * 25);
    for (let k = 0; k < n; k++) {
      const roll = Math.random();
      const rating = roll < 0.64 ? 5 : roll < 0.85 ? 4 : roll < 0.93 ? 3 : roll < 0.97 ? 2 : 1;
      await prisma.review.create({
        data: {
          vendorId: vendor.id,
          rating,
          disputed: Math.random() < 0.012,
          responseTimeHours: Math.round((0.5 + Math.random() * 6) * 10) / 10,
          createdAt: monthsAgo(Math.floor(Math.random() * 12), 1 + Math.floor(Math.random() * 27)),
        },
      });
      reviewCount++;
    }
  }
  console.log(`Seeded ${reviewCount} reviews.`);

  // ─── Vendor onboarding funnel (reuses Funnel/FunnelStep models) ────────────
  const applied = vendors.length;
  const verified = vendors.filter((v) => v.status !== 'applied').length;
  const onboarded = vendors.filter((v) => ['onboarded', 'listed', 'selling'].includes(v.status)).length;
  const listed = vendors.filter((v) => ['listed', 'selling'].includes(v.status)).length;
  const selling = vendors.filter((v) => v.status === 'selling').length;

  const funnel = await prisma.funnel.create({
    data: {
      userId: 'system-marketplace',
      name: 'Vendor Onboarding',
      status: 'active',
      steps: {
        create: [
          { order: 1, name: 'Applied', type: 'opt_in', visitors: applied, conversions: verified },
          { order: 2, name: 'Verified', type: 'opt_in', visitors: verified, conversions: onboarded },
          { order: 3, name: 'Onboarded', type: 'page_view', visitors: onboarded, conversions: listed },
          { order: 4, name: 'First Listing', type: 'page_view', visitors: listed, conversions: selling },
          { order: 5, name: 'First Sale', type: 'checkout', visitors: selling, conversions: selling },
        ],
      },
    },
  });
  console.log(`Seeded vendor onboarding funnel: ${funnel.id}`);

  // ─── Settings (GMV target used by the GMV-vs-target chart) ────────────────
  await prisma.marketplaceSettings.create({
    data: { monthlyGmvTarget: 420000 },
  });
  console.log('Seeded marketplace settings.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
