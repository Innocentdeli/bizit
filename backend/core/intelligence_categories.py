from typing import Dict, List

INTELLIGENCE_CATEGORIES = {
    "MACRO": {
        "name": "Macro & Economic Intelligence",
        "subcategories": [
            "Foreign Exchange (FX)", "Inflation & Cost of Living", "Interest Rates", 
            "Monetary Policy (CBN, Fed, etc.)", "Fiscal Policy (Taxes, Subsidies)", 
            "GDP & Economic Growth", "Trade Balance & Imports/Exports", 
            "Public Debt & Reserves", "Global Economic Events"
        ],
        "directive": "Analyze macro forces like FX (Official vs Parallel), inflation, and policy shocks. Evaluate national vs global influences on prices."
    },
    "FINANCIAL": {
        "name": "Financial Markets & Investments",
        "subcategories": [
            "Stocks & Equities", "Bonds & Treasury Bills", "Cryptocurrencies", 
            "Commodities (oil, gold, cocoa)", "Real Estate Investment", 
            "Private Equity & Startups", "Forex Trading", "Mutual Funds & ETFs"
        ],
        "directive": "Evaluate capital movement and asset risks. Provide ROI expectations and compare different asset classes (e.g., Real Estate vs Stocks)."
    },
    "PRODUCT": {
        "name": "Product & Price Intelligence",
        "subcategories": [
            "Consumer Electronics", "Phones & Gadgets", "Laptops & Accessories", 
            "Home Appliances", "Fashion & Lifestyle", "Automotive & Spare Parts", 
            "Building Materials", "FMCG Products"
        ],
        "directive": "Power 'cheapest' and 'where to buy' queries. Signals: Wholesale vs retail pricing, Regional price differences, Supply chain pressure, Import cost exposure, Seller credibility."
    },
    "MARKETPLACE": {
        "name": "Marketplaces & Distribution Channels",
        "subcategories": [
            "Online Marketplaces", "Offline Wholesale Markets", "Retail Chains", 
            "Direct Importers", "Manufacturers", "Grey Markets", "Cross-border Platforms"
        ],
        "directive": "Rank seller reliability and distribution channels. Identify market clusters (e.g., Computer Village) and compare with digital platforms."
    },
    "BUSINESS_MODEL": {
        "name": "Business Models & Operations",
        "subcategories": [
            "Retail", "Service", "POS & Agency Banking", "E-commerce", 
            "Import/Export", "Manufacturing", "Logistics & Delivery", 
            "Digital Products", "Subscription Businesses"
        ],
        "directive": "Audit profitability and operational structures. Analyze if a specific business model is still viable in the current environment."
    },
    "SME": {
        "name": "Entrepreneurship & SME Intelligence",
        "subcategories": [
            "Business Startup Costs", "Profit Margins", "Customer Demand", 
            "Competition Density", "Scaling Challenges", "Hiring & Staffing", 
            "Cash Flow Management", "Failure Risks"
        ],
        "directive": "Provide practical startup paths, capital allocation, and margin analysis for SMEs. Highlight growth probability vs failure risks."
    },
    "INDUSTRY": {
        "name": "Industry & Sector Analysis",
        "subcategories": [
            "Telecommunications", "Energy & Power", "Agriculture & Agro-processing", 
            "Healthcare", "Education", "Transportation", "Construction", 
            "Fintech", "Retail & FMCG", "Media & Advertising"
        ],
        "directive": "Map sector-wide movements, supply chain pressures, and competitive density. Analyze how policy shifts affect the entire industry."
    },
    "POLICY": {
        "name": "Policy, Regulation & Compliance",
        "subcategories": [
            "CBN Regulations", "Import & Export Rules", "Customs & Duties", 
            "Taxation (VAT, PAYE, CIT)", "Licensing & Permits", 
            "Consumer Protection", "Trade Restrictions", "Government Interventions"
        ],
        "directive": "Summarize regulatory hurdles, customs duties, and compliance risks. Critical for trust and legal accuracy."
    },
    "LOCATION": {
        "name": "Location & Regional Markets",
        "subcategories": [
            "Country", "State", "City", "Market Cluster (e.g. Computer Village)", 
            "Border Trade Zones", "Industrial Hubs", "Free Trade Zones"
        ],
        "directive": "Localize accuracy to specific clusters and regions. Consider logistics costs and regional trade dynamics (Africa-First)."
    },
    "RISK": {
        "name": "Credibility & Risk Intelligence",
        "subcategories": [
            "Source Credibility Score", "Data Freshness", "Conflict of Interest", 
            "Market Manipulation Risk", "Fraud & Scam Signals", 
            "Price Volatility Risk", "Policy Shock Risk"
        ],
        "directive": "SILENT LAYER: Must be applied to every answer. Flag fraud, data decay, and volatility. Provide a risk-adjusted confidence score."
    },
    "FORECAST": {
        "name": "Forecasting & Trend Intelligence",
        "subcategories": [
            "Short-term Market Trends", "Seasonal Effects", "Demand Cycles", 
            "Price Volatility", "Policy Impact Forecasts", "Risk Scenarios (best/worst case)"
        ],
        "directive": "Project Primary vs Secondary scenarios. Consider seasonal effects and policy impact trajectories."
    },
    "CONTEXT": {
        "name": "Decision Context",
        "subcategories": [
            "Buyer vs Seller", "Short-term vs Long-term", "Risk Tolerance", 
            "Budget Range", "Location Constraints", "Time Sensitivity"
        ],
        "directive": "Personalize the response without bias. Tailor advice based on user's role, budget, and time sensitivity."
    }
}
