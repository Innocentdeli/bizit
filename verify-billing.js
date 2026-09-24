// Seed a test coupon via the database directly
fetch('http://localhost:3001/billing/plans')
  .then(r => r.json())
  .then(plans => {
    console.log('=== Available Plans ===');
    plans.forEach(p => console.log(`[${p.id}] ${p.name} - $${p.price}/${p.interval}`));
  });
