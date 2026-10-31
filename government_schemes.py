"""
government_schemes.py
Database of Indian Government agricultural schemes that farmers can apply to.
"""

GOVERNMENT_SCHEMES = [
    {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Comprehensive crop insurance scheme providing financial support to farmers suffering crop loss/damage due to natural calamities, pests, and diseases.",
        "benefits": [
            "Insurance coverage for all food & oilseed crops and annual commercial/horticultural crops",
            "Very low premium: 2% for Kharif, 1.5% for Rabi, 5% for commercial crops",
            "Full insured sum payout for crop loss > 75%",
            "Post-harvest losses covered for up to 14 days",
            "Add-on coverage for localized calamities and mid-season adversities",
        ],
        "eligibility": [
            "All farmers including sharecroppers and tenant farmers",
            "Both loanee and non-loanee farmers (voluntary for non-loanee since 2020)",
            "Must have insurable interest in the crop",
        ],
        "how_to_apply": [
            "Visit nearest bank branch or Common Service Centre (CSC)",
            "Apply online at https://pmfby.gov.in",
            "Through authorized insurance company agents",
            "Documents: Aadhaar, bank passbook, land records, sowing certificate",
        ],
        "website": "https://pmfby.gov.in",
        "category": "Crop Insurance",
        "icon": "🛡️",
    },
    {
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Direct income support of ₹6,000 per year to all land-holding farmer families, paid in three equal installments.",
        "benefits": [
            "₹6,000 per year (₹2,000 every 4 months) directly to bank account",
            "Covers all farmer families with cultivable landholding",
            "No intermediaries — Direct Benefit Transfer (DBT)",
        ],
        "eligibility": [
            "All land-holding farmer families (subject to exclusion criteria)",
            "Exclusions: institutional landholders, income tax payees, government employees, professionals",
        ],
        "how_to_apply": [
            "Register online at https://pmkisan.gov.in",
            "Visit local revenue office or Common Service Centre",
            "Documents: Aadhaar, bank account details, land ownership records",
        ],
        "website": "https://pmkisan.gov.in",
        "category": "Income Support",
        "icon": "💰",
    },
    {
        "name": "Soil Health Card Scheme",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Provides soil health cards to farmers with crop-wise nutrient recommendations to improve productivity through balanced fertilization.",
        "benefits": [
            "Free soil testing and analysis",
            "Crop-wise fertilizer recommendations based on soil nutrient status",
            "Helps reduce input costs by avoiding excess fertilizer use",
            "Issued every 2 years for each farm holding",
        ],
        "eligibility": [
            "All farmers across India",
            "Priority for small and marginal farmers",
        ],
        "how_to_apply": [
            "Visit nearest Soil Testing Laboratory or Krishi Vigyan Kendra",
            "Apply online at https://soilhealth.dac.gov.in",
            "Through state agriculture department",
        ],
        "website": "https://soilhealth.dac.gov.in",
        "category": "Soil & Inputs",
        "icon": "🌱",
    },
    {
        "name": "Kisan Credit Card (KCC)",
        "ministry": "Ministry of Finance / NABARD",
        "description": "Provides farmers with timely and adequate credit for agricultural operations, purchase of inputs, and other needs.",
        "benefits": [
            "Credit limit based on land holding and crop pattern",
            "Interest rate of 7% p.a. (further subvention of 3% for timely repayment = effective 4%)",
            "Coverage for crop production, post-harvest, maintenance of farm assets, and consumption needs",
            "Personal accident insurance of ₹50,000 (death) and ₹25,000 (disability)",
            "Flexible repayment based on cropping pattern",
        ],
        "eligibility": [
            "All farmers — individual/joint, owner cultivators, tenant farmers, sharecroppers",
            "Also available for fisheries and animal husbandry activities",
        ],
        "how_to_apply": [
            "Apply at any commercial bank, cooperative bank, or Regional Rural Bank",
            "Documents: identity proof, land documents, passport photos",
            "Can also apply through PM-KISAN portal",
        ],
        "website": "https://www.nabard.org",
        "category": "Credit & Finance",
        "icon": "🏦",
    },
    {
        "name": "National Mission on Sustainable Agriculture (NMSA)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Promotes sustainable agriculture through climate change adaptation strategies, integrated farming, and resource conservation.",
        "benefits": [
            "Subsidy up to 50% on micro-irrigation systems (drip and sprinkler)",
            "Support for organic farming and certification",
            "Assistance for rainwater harvesting and soil health management",
            "Training on climate-resilient farming practices",
        ],
        "eligibility": [
            "All farmers, with priority for rainfed and resource-poor regions",
            "SC/ST/small & marginal farmers get higher subsidy",
        ],
        "how_to_apply": [
            "Apply through District Agriculture Officer",
            "Online through state agriculture department portal",
            "Through Krishi Vigyan Kendras",
        ],
        "website": "https://nmsa.dac.gov.in",
        "category": "Sustainable Agriculture",
        "icon": "♻️",
    },
    {
        "name": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)",
        "ministry": "Ministry of Agriculture & Ministry of Jal Shakti",
        "description": "Ensures access to protective irrigation ('Har Khet Ko Paani') and improves water use efficiency ('Per Drop More Crop').",
        "benefits": [
            "55% subsidy for small & marginal farmers on micro-irrigation",
            "45% subsidy for other farmers",
            "Support for bore wells, farm ponds, and water harvesting structures",
            "Development of irrigation infrastructure in water-stressed areas",
        ],
        "eligibility": [
            "All farmers with agricultural landholding",
            "Priority for drought-prone and water-scarce regions",
        ],
        "how_to_apply": [
            "Apply through District Agriculture Office or Horticulture Department",
            "Online portals vary by state",
        ],
        "website": "https://pmksy.gov.in",
        "category": "Irrigation",
        "icon": "💧",
    },
    {
        "name": "e-NAM (National Agriculture Market)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Online trading platform for agricultural commodities providing better price discovery and transparency.",
        "benefits": [
            "Access to multiple markets and buyers online",
            "Transparent price discovery through bidding",
            "Reduction in intermediary costs",
            "Online payment directly to farmer's bank account",
            "Quality assaying at the mandi gate",
        ],
        "eligibility": [
            "All farmers, traders, and buyers",
            "Must be registered at an e-NAM mandi",
        ],
        "how_to_apply": [
            "Register at https://enam.gov.in or mobile app",
            "Visit nearest e-NAM enabled mandi",
            "Documents: Aadhaar, bank account, mobile number",
        ],
        "website": "https://enam.gov.in",
        "category": "Market Access",
        "icon": "🏪",
    },
    {
        "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Provides subsidies on purchase of agricultural machinery and equipment to boost farm productivity.",
        "benefits": [
            "Subsidy of 40-50% on farm machinery (tractors, harvesters, tillers, etc.)",
            "Up to 80% subsidy for SC/ST/small & marginal farmers on select equipment",
            "Support for Custom Hiring Centres and Farm Machinery Banks",
            "Training on operation and maintenance of machinery",
        ],
        "eligibility": [
            "Individual farmers, farmer groups (FPOs/SHGs), entrepreneurs",
            "Priority for small and marginal farmers",
        ],
        "how_to_apply": [
            "Apply online at https://agrimachinery.nic.in",
            "Through District Agriculture Office",
            "Documents: Aadhaar, land records, bank details, quotation from dealer",
        ],
        "website": "https://agrimachinery.nic.in",
        "category": "Farm Mechanization",
        "icon": "🚜",
    },
    {
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "Promotes organic farming through adoption of organic village clusters. Supports certification and marketing of organic produce.",
        "benefits": [
            "₹50,000 per hectare over 3 years for organic farming inputs and certification",
            "Includes support for organic inputs, seeds, and bio-fertilizers",
            "Third-party organic certification (PGS-India)",
            "Market linkage support for organic produce",
        ],
        "eligibility": [
            "Groups of 50+ farmers forming a cluster of 50 acres",
            "All farmers willing to adopt organic farming",
        ],
        "how_to_apply": [
            "Through District Agriculture Office or State Agriculture Department",
            "Register at https://pgsindia-ncof.gov.in for PGS certification",
        ],
        "website": "https://pgsindia-ncof.gov.in",
        "category": "Organic Farming",
        "icon": "🌿",
    },
    {
        "name": "Agriculture Infrastructure Fund (AIF)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": "₹1 lakh crore financing facility for post-harvest management infrastructure and community farming assets.",
        "benefits": [
            "Interest subvention of 3% per annum on loans up to ₹2 crore",
            "Credit guarantee coverage under CGTMSE for loans up to ₹2 crore",
            "For building cold storage, warehouses, grading/sorting units, processing plants",
            "Available for 10 years from 2020-21 to 2029-30",
        ],
        "eligibility": [
            "Farmers, FPOs, PACS, Marketing Cooperative Societies, SHGs",
            "Agri-entrepreneurs, startups, and aggregation infrastructure providers",
        ],
        "how_to_apply": [
            "Apply online at https://agriinfra.dac.gov.in",
            "Through any scheduled bank or financial institution",
        ],
        "website": "https://agriinfra.dac.gov.in",
        "category": "Infrastructure",
        "icon": "🏗️",
    },
]
