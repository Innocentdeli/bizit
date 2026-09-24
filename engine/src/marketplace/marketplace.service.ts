import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** Start-of-month Date, `monthsBack` months before now (0 = current month). */
function monthStart(monthsBack: number): Date {
  const d = new Date();
  d.setDate(1);
  d.setHours(0, 0, 0, 0);
  d.setMonth(d.getMonth() - monthsBack);
  return d;
}

function pctChange(current: number, previous: number): number {
  if (!previous) return current > 0 ? 100 : 0;
  return Math.round(((current - previous) / previous) * 1000) / 10;
}

@Injectable()
export class MarketplaceService {
  constructor(private prisma: PrismaService) {}

  /** Trailing-30-day window helper, plus the 30 days before that for deltas. */
  private windows() {
    const now = new Date();
    const d30 = new Date(now);
    d30.setDate(d30.getDate() - 30);
    const d60 = new Date(now);
    d60.setDate(d60.getDate() - 60);
    return { now, d30, d60 };
  }

  async getKpis() {
    const { now, d30, d60 } = this.windows();

    const [vendorsActiveNow, vendorsActive30dAgo, allVendors] = await Promise.all([
      this.prisma.vendor.count({ where: { status: { in: ['onboarded', 'listed', 'selling'] }, createdAt: { lte: now } } }),
      this.prisma.vendor.count({ where: { status: { in: ['onboarded', 'listed', 'selling'] }, createdAt: { lte: d30 } } }),
      this.prisma.vendor.count(),
    ]);

    const [ordersLast30, ordersPrev30] = await Promise.all([
      this.prisma.marketplaceOrder.findMany({ where: { createdAt: { gte: d30, lte: now } } }),
      this.prisma.marketplaceOrder.findMany({ where: { createdAt: { gte: d60, lt: d30 } } }),
    ]);

    const buyersLast30 = new Set(ordersLast30.map((o) => o.buyerId)).size;
    const buyersPrev30 = new Set(ordersPrev30.map((o) => o.buyerId)).size;
    const gmvLast30 = ordersLast30.reduce((s, o) => s + o.amount, 0);
    const gmvPrev30 = ordersPrev30.reduce((s, o) => s + o.amount, 0);

    const liquidityRatioNow = vendorsActiveNow > 0 ? Math.min(1, buyersLast30 / (vendorsActiveNow * 8)) : 0;
    const liquidityRatioPrev = vendorsActive30dAgo > 0 ? Math.min(1, buyersPrev30 / (vendorsActive30dAgo * 8)) : 0;

    // Repeat-purchase retention: of buyers active in the prior 30d window, what
    // share also placed an order in the current 30d window.
    const prevBuyerIds = new Set(ordersPrev30.map((o) => o.buyerId));
    const currentBuyerIds = new Set(ordersLast30.map((o) => o.buyerId));
    let retained = 0;
    prevBuyerIds.forEach((id) => {
      if (currentBuyerIds.has(id)) retained++;
    });
    const retentionRate = prevBuyerIds.size > 0 ? Math.round((retained / prevBuyerIds.size) * 1000) / 10 : 0;

    const referredLast30 = ordersLast30.filter((o) => o.referralCode).length;
    const referredPrev30 = ordersPrev30.filter((o) => o.referralCode).length;

    const trust = await this.getTrustMetrics();

    const healthScore = Math.round(
      Math.min(100, retentionRate) * 0.3 +
        liquidityRatioNow * 100 * 0.3 +
        Math.min(100, (trust.avgRating / 5) * 100) * 0.25 +
        Math.min(100, 50 + pctChange(gmvLast30, gmvPrev30)) * 0.15,
    );

    return {
      activeVendors: vendorsActiveNow,
      activeVendorsDelta: pctChange(vendorsActiveNow, vendorsActive30dAgo),
      activeBuyers: buyersLast30,
      activeBuyersDelta: pctChange(buyersLast30, buyersPrev30),
      gmv: Math.round(gmvLast30 * 100) / 100,
      gmvDelta: pctChange(gmvLast30, gmvPrev30),
      liquidityRatio: Math.round(liquidityRatioNow * 100) / 100,
      liquidityRatioDelta: pctChange(liquidityRatioNow, liquidityRatioPrev),
      retentionRate,
      referralGrowth: pctChange(referredLast30, referredPrev30),
      healthScore,
      totalVendors: allVendors,
    };
  }

  async getAcquisitionTrend() {
    const months = Array.from({ length: 12 }, (_, i) => 11 - i);
    const result = [];
    for (const monthsBack of months) {
      const start = monthStart(monthsBack);
      const end = monthStart(monthsBack - 1);
      const [vendors, orders] = await Promise.all([
        this.prisma.vendor.count({ where: { createdAt: { gte: start, lt: end } } }),
        this.prisma.marketplaceOrder.findMany({ where: { createdAt: { gte: start, lt: end } }, select: { buyerId: true } }),
      ]);
      result.push({
        month: MONTH_LABELS[start.getMonth()],
        buyers: new Set(orders.map((o) => o.buyerId)).size,
        vendors,
      });
    }
    return result;
  }

  async getGmvTrend() {
    const settings = await this.prisma.marketplaceSettings.findFirst();
    const target = settings?.monthlyGmvTarget ?? 400000;

    const months = Array.from({ length: 12 }, (_, i) => 11 - i);
    const result = [];
    for (const monthsBack of months) {
      const start = monthStart(monthsBack);
      const end = monthStart(monthsBack - 1);
      const orders = await this.prisma.marketplaceOrder.findMany({
        where: { createdAt: { gte: start, lt: end } },
        select: { amount: true },
      });
      const gmv = Math.round(orders.reduce((s, o) => s + o.amount, 0) * 100) / 100;
      result.push({ month: MONTH_LABELS[start.getMonth()], gmv, target: Math.round(target) });
    }
    return result;
  }

  async getLiquidityByCategory() {
    const { d30, now } = this.windows();
    const [vendors, orders] = await Promise.all([
      this.prisma.vendor.findMany({ where: { status: { in: ['onboarded', 'listed', 'selling'] } }, select: { category: true } }),
      this.prisma.marketplaceOrder.findMany({ where: { createdAt: { gte: d30, lte: now } }, select: { category: true, buyerId: true } }),
    ]);

    const categories = Array.from(new Set([...vendors.map((v) => v.category), ...orders.map((o) => o.category)]));

    return categories.map((category) => {
      const supply = vendors.filter((v) => v.category === category).length;
      const demand = new Set(orders.filter((o) => o.category === category).map((o) => o.buyerId)).size;
      const ratio = supply > 0 ? Math.round(Math.min(1, demand / (supply * 3)) * 100) / 100 : 0;
      return { category, supply, demand, ratio };
    });
  }

  async getGeographicSpread() {
    const [vendors, orders] = await Promise.all([
      this.prisma.vendor.findMany({ select: { city: true } }),
      this.prisma.marketplaceOrder.findMany({ select: { buyerCity: true, buyerId: true, amount: true } }),
    ]);

    const cities = Array.from(new Set([...vendors.map((v) => v.city), ...orders.map((o) => o.buyerCity)]));

    return cities
      .map((city) => {
        const cityOrders = orders.filter((o) => o.buyerCity === city);
        return {
          city,
          vendors: vendors.filter((v) => v.city === city).length,
          buyers: new Set(cityOrders.map((o) => o.buyerId)).size,
          gmv: Math.round(cityOrders.reduce((s, o) => s + o.amount, 0) * 100) / 100,
        };
      })
      .sort((a, b) => b.gmv - a.gmv);
  }

  async getCohortRetention() {
    // Bucket every order by the buyer's *first ever* order month (their cohort),
    // then measure what % of that cohort placed an order in each subsequent month.
    const months = Array.from({ length: 6 }, (_, i) => 5 - i); // 6 most recent cohort months
    const allOrders = await this.prisma.marketplaceOrder.findMany({
      select: { buyerId: true, createdAt: true },
    });

    const firstOrderMonth = new Map<string, Date>();
    for (const o of allOrders) {
      const bucket = new Date(o.createdAt.getFullYear(), o.createdAt.getMonth(), 1);
      const existing = firstOrderMonth.get(o.buyerId);
      if (!existing || bucket < existing) firstOrderMonth.set(o.buyerId, bucket);
    }

    const buyerMonths = new Map<string, Set<string>>(); // buyerId -> set of "YYYY-M" they ordered in
    for (const o of allOrders) {
      const key = `${o.createdAt.getFullYear()}-${o.createdAt.getMonth()}`;
      if (!buyerMonths.has(o.buyerId)) buyerMonths.set(o.buyerId, new Set());
      buyerMonths.get(o.buyerId)!.add(key);
    }

    return months.map((monthsBack) => {
      const cohortStart = monthStart(monthsBack);
      const cohortLabel = MONTH_LABELS[cohortStart.getMonth()];
      const cohortBuyers = Array.from(firstOrderMonth.entries())
        .filter(([, d]) => d.getTime() === cohortStart.getTime())
        .map(([buyerId]) => buyerId);

      const row: Record<string, number | string | null> = { cohort: cohortLabel };
      for (let m = 0; m <= 5; m++) {
        const targetDate = new Date(cohortStart);
        targetDate.setMonth(targetDate.getMonth() + m);
        if (targetDate > new Date()) {
          row[`m${m}`] = null; // Not enough elapsed time yet for this cell.
          continue;
        }
        const key = `${targetDate.getFullYear()}-${targetDate.getMonth()}`;
        if (cohortBuyers.length === 0) {
          row[`m${m}`] = 0;
          continue;
        }
        const active = cohortBuyers.filter((b) => buyerMonths.get(b)?.has(key)).length;
        row[`m${m}`] = Math.round((active / cohortBuyers.length) * 1000) / 10;
      }
      return row;
    });
  }

  async getReferralPerformance() {
    const links = await this.prisma.referralLink.findMany({ orderBy: { signups: 'desc' } });
    const codes = links.map((l) => l.code);

    const referredOrders = await this.prisma.marketplaceOrder.findMany({
      where: { referralCode: { in: codes } },
      select: { referralCode: true, amount: true, createdAt: true },
    });

    const totalReferrals = links.reduce((s, l) => s + l.clicks, 0);
    const converted = links.reduce((s, l) => s + l.signups, 0);
    const revenueByCode = new Map<string, number>();
    for (const o of referredOrders) {
      revenueByCode.set(o.referralCode!, (revenueByCode.get(o.referralCode!) || 0) + o.amount);
    }

    const topReferrers = links.slice(0, 5).map((l) => ({
      code: l.code,
      referrals: l.clicks,
      converted: l.signups,
      revenue: Math.round((revenueByCode.get(l.code) || 0) * 100) / 100,
    }));

    const months = Array.from({ length: 6 }, (_, i) => 5 - i);
    const trend = months.map((monthsBack) => {
      const start = monthStart(monthsBack);
      const end = monthStart(monthsBack - 1);
      const inMonth = referredOrders.filter((o) => o.createdAt >= start && o.createdAt < end);
      return {
        month: MONTH_LABELS[start.getMonth()],
        referrals: inMonth.length,
        converted: inMonth.length, // every seeded referral-tagged order is a converted referral
      };
    });

    return {
      totalReferrals,
      converted,
      conversionRate: totalReferrals > 0 ? Math.round((converted / totalReferrals) * 1000) / 10 : 0,
      avgOrderValue:
        referredOrders.length > 0
          ? Math.round((referredOrders.reduce((s, o) => s + o.amount, 0) / referredOrders.length) * 100) / 100
          : 0,
      topReferrers,
      trend,
    };
  }

  async getVendorFunnel() {
    const funnel = await this.prisma.funnel.findFirst({
      where: { name: 'Vendor Onboarding' },
      include: { steps: { orderBy: { order: 'asc' } } },
    });

    if (!funnel) return [];

    return funnel.steps.map((s) => ({ stage: s.name, count: s.visitors }));
  }

  async getTrustMetrics() {
    const reviews = await this.prisma.review.findMany();
    const vendors = await this.prisma.vendor.findMany({ select: { verified: true } });

    const reviewCount = reviews.length;
    const avgRating = reviewCount > 0 ? reviews.reduce((s, r) => s + r.rating, 0) / reviewCount : 0;
    const disputeRate = reviewCount > 0 ? (reviews.filter((r) => r.disputed).length / reviewCount) * 100 : 0;
    const avgResponseTime = reviewCount > 0 ? reviews.reduce((s, r) => s + r.responseTimeHours, 0) / reviewCount : 0;
    const verifiedPct = vendors.length > 0 ? (vendors.filter((v) => v.verified).length / vendors.length) * 100 : 0;

    const breakdown = [5, 4, 3, 2, 1].map((star) => ({
      label: `${star} ★`,
      pct: reviewCount > 0 ? Math.round((reviews.filter((r) => r.rating === star).length / reviewCount) * 1000) / 10 : 0,
    }));

    return {
      avgRating: Math.round(avgRating * 100) / 100,
      disputeRate: Math.round(disputeRate * 10) / 10,
      completionRate: Math.round((100 - disputeRate) * 10) / 10,
      responseTime: Math.round(avgResponseTime * 10) / 10,
      verifiedVendors: Math.round(verifiedPct * 10) / 10,
      reviewCount,
      breakdown,
    };
  }
}
