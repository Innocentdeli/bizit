fetch('http://localhost:3001/reporting/clients', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Acme Corp Marketing',
    companyName: 'Acme Corp',
    logoUrl: 'https://logo.clearbit.com/acme.com',
    primaryColor: '#8b5cf6'
  })
}).then(res => res.json()).then(console.log).catch(console.error);
