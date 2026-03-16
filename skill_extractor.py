import re

SKILL_DICT = {
    "INFORMATION-TECHNOLOGY": [
        # Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "c language",
        "ruby", "php", "swift", "kotlin", "go", "golang", "rust", "scala",
        "perl", "r language", "matlab", "bash", "shell scripting", "powershell",
        # Web
        "react", "angular", "vue", "nextjs", "nodejs", "express", "html", "css",
        "html5", "css3", "bootstrap", "tailwind", "jquery", "redux", "graphql",
        "rest api", "restful", "soap", "webpack", "vite",
        # Data / ML / AI
        "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
        "nlp", "natural language processing", "computer vision", "data science",
        "data analysis", "data analytics", "data engineering", "big data",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
        "numpy", "matplotlib", "seaborn", "opencv", "huggingface", "langchain",
        "neural network", "random forest", "gradient boosting", "xgboost",
        "regression", "classification", "clustering", "reinforcement learning",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "sqlite", "oracle", "cassandra", "dynamodb", "firebase", "nosql",
        # Cloud / DevOps
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "ci/cd", "devops", "mlops",
        "linux", "ubuntu", "git", "github", "gitlab", "bitbucket",
        "microservices", "serverless", "lambda", "ec2", "s3",
        # Frameworks / Tools
        "flask", "django", "fastapi", "spring boot", "spring", "hibernate",
        "api", "postman", "swagger", "jira", "confluence", "agile", "scrum",
        "figma", "vs code", "jupyter", "colab", "hadoop", "spark", "kafka",
        # Security / Networking
        "cybersecurity", "network security", "ethical hacking", "penetration testing",
        "firewall", "vpn", "ssl", "encryption", "oauth", "jwt",
        # Other
        "blockchain", "web3", "solidity", "iot", "embedded systems",
        "computer networks", "operating systems", "data structures", "algorithms",
        "object oriented programming", "oop", "functional programming",
        "software development", "software engineering", "system design",
        "problem solving", "debugging", "testing", "unit testing", "selenium"
    ],

    "TEACHER": [
        # Core teaching
        "lesson planning", "lesson plan", "curriculum design", "curriculum development",
        "curriculum", "classroom management", "differentiated instruction",
        "teaching", "instruction", "pedagogy", "pedagogy methods",
        "assessment", "formative assessment", "summative assessment",
        "student engagement", "classroom", "students", "tutoring",
        # Standards / Methods
        "stem", "steam", "ngss", "common core", "iep", "504 plan",
        "special education", "inclusive education", "blended learning",
        "project based learning", "inquiry based learning", "flipped classroom",
        "cooperative learning", "experiential learning",
        # Technology in education
        "e-learning", "google classroom", "canvas", "blackboard", "moodle",
        "zoom teaching", "online teaching", "virtual classroom", "lms",
        "smartboard", "educational technology", "ed tech",
        # Subjects
        "mathematics", "science", "biology", "chemistry", "physics",
        "english", "literature", "history", "geography", "social studies",
        "art education", "music education", "physical education", "pe",
        # Admin / Development
        "parent communication", "report cards", "grading", "rubrics",
        "professional development", "mentoring", "coaching teachers",
        "school administration", "principal", "vice principal",
        "education policy", "accreditation", "teacher training",
        # Certifications
        "b.ed", "m.ed", "teaching certification", "ctet", "tet",
        "google certified educator", "microsoft educator"
    ],

    "HEALTHCARE": [
        # Clinical
        "patient care", "patient assessment", "clinical trials", "diagnosis",
        "treatment planning", "medical history", "clinical documentation",
        "vital signs", "triage", "emergency care", "icu", "ot",
        # Lab / Science
        "pcr", "dna extraction", "pathology", "laboratory procedures",
        "aseptic techniques", "electrophoresis", "microscopy", "biopsy",
        "blood tests", "urinalysis", "microbiology", "histology",
        "immunology", "genetics", "genomics", "clinical chemistry",
        "quality control lab", "lab management",
        # Pharmacy
        "pharmacology", "pharmacy", "drug administration", "medication management",
        "prescription", "dosage", "drug interaction", "pharmacokinetics",
        # Nursing / Allied
        "nursing", "registered nurse", "rn", "bsc nursing", "gnm",
        "patient monitoring", "wound care", "iv administration",
        "catheterization", "ecg", "ekg", "ventilator management",
        # Admin / Digital Health
        "ehr", "emr", "electronic health records", "medical coding",
        "icd-10", "cpt coding", "medical billing", "hipaa",
        "health informatics", "telemedicine",
        # Specialties
        "anatomy", "physiology", "surgery", "pediatrics", "gynecology",
        "cardiology", "neurology", "orthopedics", "oncology", "radiology",
        "dermatology", "psychiatry", "public health", "epidemiology",
        "nutrition", "dietetics", "occupational therapy", "physiotherapy"
    ],

    "FINANCE": [
        # Accounting
        "auditing", "taxation", "financial analysis", "budgeting", "accounting",
        "bookkeeping", "journal entries", "ledger", "trial balance",
        "balance sheet", "profit and loss", "cash flow", "financial statements",
        "accounts payable", "accounts receivable", "reconciliation",
        "cost accounting", "management accounting", "financial reporting",
        # Investment / Banking
        "investment", "portfolio management", "equity research", "valuation",
        "financial modeling", "dcf", "npv", "irr", "mergers", "acquisitions",
        "capital markets", "derivatives", "options", "futures", "forex",
        "mutual funds", "wealth management", "asset management",
        "investment banking", "commercial banking", "retail banking",
        # Risk / Compliance
        "risk management", "credit risk", "market risk", "compliance",
        "regulatory", "kyc", "aml", "internal audit", "external audit",
        "sox", "ifrs", "gaap", "ind as",
        # Tools
        "excel", "advanced excel", "vba", "sap", "tally", "quickbooks",
        "zoho books", "oracle financials", "bloomberg", "tableau",
        "power bi", "python finance", "sql finance",
        # Planning
        "forecasting", "financial planning", "fp&a", "variance analysis",
        "scenario analysis", "business valuation", "due diligence",
        # Certifications
        "ca", "cpa", "cfa", "acca", "frm", "cma", "mba finance"
    ],

    "ENGINEERING": [
        # Mechanical
        "autocad", "solidworks", "catia", "creo", "ansys", "fusion 360",
        "cad", "cam", "cae", "fea", "fem", "structural analysis",
        "mechanical design", "product design", "manufacturing",
        "cnc machining", "lean manufacturing", "six sigma", "kaizen",
        "thermodynamics", "fluid mechanics", "heat transfer",
        "machine design", "vibration analysis",
        # Civil
        "civil engineering", "structural design", "staad pro", "etabs",
        "revit", "primavera", "ms project", "construction management",
        "concrete design", "steel design", "geotechnical",
        "highway design", "surveying", "quantity estimation",
        # Electrical / Electronics
        "circuit design", "pcb design", "altium", "eagle", "kicad",
        "plc", "scada", "hmi", "electrical design", "power systems",
        "embedded systems", "arduino", "raspberry pi", "fpga",
        "signal processing", "control systems", "matlab simulink",
        # Common
        "project management", "quality control", "quality assurance",
        "iso standards", "safety compliance", "simulation",
        "testing and validation", "root cause analysis", "maintenance",
        "procurement", "vendor management", "technical documentation"
    ],

    "DESIGNER": [
        # Tools
        "photoshop", "illustrator", "figma", "adobe xd", "sketch",
        "indesign", "after effects", "premiere pro", "lightroom",
        "canva", "coreldraw", "blender", "cinema 4d", "maya 3d",
        "zbrush", "procreate", "affinity designer",
        # UI/UX
        "ui design", "ux design", "ui/ux", "user interface", "user experience",
        "wireframing", "prototyping", "user research", "usability testing",
        "information architecture", "interaction design", "design thinking",
        "design systems", "component library", "atomic design",
        "responsive design", "mobile design", "web design",
        # Visual
        "typography", "branding", "brand identity", "logo design",
        "graphic design", "visual design", "motion design",
        "illustration", "iconography", "color theory", "grid systems",
        "packaging design", "print design", "poster design",
        # Strategy
        "design strategy", "creative direction", "art direction",
        "storyboarding", "moodboarding", "style guide",
        "design research", "competitor analysis"
    ],

    "SALES": [
        "crm", "salesforce", "hubspot", "zoho crm", "pipedrive",
        "b2b sales", "b2c sales", "lead generation", "lead nurturing",
        "negotiation", "cold calling", "cold emailing", "prospecting",
        "account management", "key account management", "pipeline management",
        "revenue growth", "quota attainment", "sales forecasting",
        "territory management", "channel sales", "inside sales",
        "field sales", "enterprise sales", "saas sales",
        "business development", "bd", "client acquisition",
        "upselling", "cross selling", "customer retention",
        "sales presentation", "product demo", "rfp", "proposal writing",
        "contract negotiation", "closing deals", "objection handling",
        "market research", "competitive analysis", "go to market"
    ],

    "HR": [
        "recruitment", "talent acquisition", "sourcing", "headhunting",
        "payroll", "payroll processing", "hris", "hrms", "sap hr",
        "workday", "darwinbox", "greythr", "zoho people",
        "onboarding", "offboarding", "exit interviews",
        "performance management", "appraisal", "kpi", "okr",
        "employee relations", "grievance handling", "disciplinary",
        "training and development", "l&d", "learning development",
        "compensation", "benefits", "total rewards", "job evaluation",
        "talent management", "succession planning", "hr analytics",
        "employee engagement", "culture", "diversity", "inclusion",
        "labour law", "compliance hr", "statutory compliance",
        "pf", "esic", "gratuity", "contract staffing",
        "bulk hiring", "campus recruitment", "linkedin recruiter",
        "naukri recruiter", "job description", "competency mapping"
    ],

    "CHEF": [
        "culinary arts", "menu planning", "food safety", "haccp",
        "pastry", "baking", "confectionery", "bread making",
        "kitchen management", "catering", "recipe development",
        "food presentation", "plating", "garnishing",
        "inventory management kitchen", "food costing",
        "sous vide", "molecular gastronomy", "fermentation",
        "butchery", "seafood preparation", "vegetarian cooking",
        "continental cuisine", "indian cuisine", "italian cuisine",
        "french cuisine", "asian cuisine", "mediterranean",
        "banquet management", "buffet setup", "restaurant operations",
        "food hygiene", "fssai", "kitchen safety", "fire safety kitchen",
        "staff training kitchen", "procurement food", "vendor management food"
    ],

    "FITNESS": [
        "personal training", "group fitness", "fitness assessment",
        "nutrition", "sports nutrition", "meal planning",
        "workout planning", "exercise prescription", "periodization",
        "strength training", "resistance training", "weight training",
        "cardio training", "hiit", "functional training", "crossfit",
        "yoga", "pilates", "zumba", "aerobics", "spinning",
        "wellness coaching", "lifestyle coaching", "behaviour change",
        "sports medicine", "rehabilitation", "injury prevention",
        "physiotherapy assistant", "sports massage", "stretching",
        "bmi assessment", "body composition", "vo2 max",
        "gym management", "member retention", "class scheduling",
        "cpr certified", "first aid", "ace certified", "nasm", "issa"
    ],

    "CONSULTANT": [
        "strategy", "strategic planning", "business analysis",
        "stakeholder management", "project delivery", "change management",
        "advisory", "management consulting", "consulting",
        "process improvement", "business process", "bpm",
        "gap analysis", "feasibility study", "market entry",
        "digital transformation", "it consulting", "erp consulting",
        "sap consulting", "oracle consulting", "business intelligence",
        "data driven decision", "kpi dashboard", "executive reporting",
        "client management", "engagement management", "rfp response",
        "thought leadership", "whitepaper", "case study",
        "mckinsey", "bcg", "deloitte", "pwc", "ey", "kpmg",
        "six sigma", "lean", "agile transformation", "pmp", "prince2"
    ],

    "CONSTRUCTION": [
        "project management", "site management", "site supervision",
        "autocad", "revit", "staad pro", "ms project", "primavera",
        "quantity surveying", "quantity estimation", "boq",
        "procurement", "tendering", "contract management",
        "structural design", "safety compliance", "hse",
        "quality management", "iso 9001", "quality audit",
        "concrete work", "rcc", "steel fabrication", "masonry",
        "plumbing", "electrical installation", "hvac",
        "project scheduling", "baseline schedule", "delay analysis",
        "site inspection", "snag list", "as built drawings",
        "client coordination", "subcontractor management",
        "billing", "ra bills", "mbr", "pert", "cpm"
    ],

    "DIGITAL-MEDIA": [
        "video editing", "adobe premiere", "premiere pro", "after effects",
        "final cut pro", "davinci resolve", "capcut",
        "content creation", "content strategy", "storytelling",
        "social media", "social media management", "community management",
        "youtube", "youtube seo", "youtube channel", "vlogging",
        "animation", "2d animation", "3d animation", "motion graphics",
        "podcast production", "audio editing", "audacity", "adobe audition",
        "photography", "lightroom", "photo editing",
        "scriptwriting", "voiceover", "screen recording",
        "live streaming", "obs studio", "streaming",
        "instagram reels", "tiktok", "shorts",
        "content calendar", "brand content", "viral content",
        "influencer marketing", "creator economy"
    ],

    "PUBLIC-RELATIONS": [
        "press release", "media relations", "media outreach",
        "crisis communication", "crisis management", "reputation management",
        "brand reputation", "brand communication", "corporate communication",
        "event management", "event planning", "event coordination",
        "copywriting", "content writing", "press kit",
        "media monitoring", "clipping", "coverage report",
        "journalist relations", "editor relations", "pitching media",
        "social media pr", "digital pr", "influencer pr",
        "internal communication", "employee communication",
        "stakeholder communication", "csr", "corporate social responsibility",
        "speechwriting", "thought leadership", "editorial calendar",
        "press conference", "media briefing", "interview preparation"
    ],

    "MARKETING": [
        "seo", "search engine optimization", "on-page seo", "off-page seo",
        "sem", "ppc", "google ads", "meta ads", "facebook ads",
        "instagram ads", "linkedin ads", "programmatic advertising",
        "google analytics", "google analytics 4", "ga4",
        "social media marketing", "smm", "content marketing",
        "email marketing", "email campaigns", "mailchimp", "hubspot email",
        "marketing automation", "crm marketing", "lead generation marketing",
        "brand management", "brand strategy", "market research",
        "consumer insights", "competitor analysis", "swot",
        "product marketing", "go to market", "positioning",
        "growth hacking", "growth marketing", "a/b testing",
        "conversion rate optimization", "cro", "funnel optimization",
        "affiliate marketing", "performance marketing",
        "influencer marketing", "partnership marketing",
        "pr marketing", "event marketing", "trade shows",
        "marketing analytics", "power bi marketing", "tableau marketing",
        "roi analysis", "campaign management", "media planning"
    ]
}

# Aliases — shorthand / abbreviations that map to full skill names
ALIASES = {
    "ml":          "machine learning",
    "ai":          "artificial intelligence",
    "nlp":         "natural language processing",
    "dl":          "deep learning",
    "cv":          "computer vision",
    "js":          "javascript",
    "ts":          "typescript",
    "k8s":         "kubernetes",
    "oop":         "object oriented programming",
    "db":          "database",
    "ui":          "ui design",
    "ux":          "ux design",
    "rpa":         "robotic process automation",
    "bi":          "business intelligence",
    "erp":         "enterprise resource planning",
    "bd":          "business development",
    "b2b":         "b2b sales",
    "b2c":         "b2c sales",
    "l&d":         "learning development",
    "pmp":         "project management",
    "hse":         "safety compliance",
    "bsc nursing": "nursing",
    "gnm":         "nursing",
    "ca":          "accounting",
    "cpa":         "accounting",
    "cfa":         "investment",
    "mba":         "business analysis",
    "haccp":       "food safety",
    "hiit":        "fitness training",
    "csr":         "corporate social responsibility",
    "smm":         "social media marketing",
    "ppc":         "google ads",
    "seo":         "search engine optimization",
    "sem":         "search engine marketing",
    "cro":         "conversion rate optimization",
    "ga4":         "google analytics",
    "cad":         "autocad",
    "plc":         "programmable logic controller",
    "ehr":         "electronic health records",
    "emr":         "electronic health records",
    "icd":         "medical coding",
    "rn":          "nursing",
    "icu":         "patient care",
    "okr":         "performance management",
    "kpi":         "performance management",
}


def normalize(text):
    """Lowercase, collapse whitespace, remove special chars except spaces."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9/\+\# ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_skills(text, domain):
    """
    Extract skills for a specific domain.
    Uses substring matching + alias expansion + partial word matching.
    Returns sorted list by skill length (longer/more specific first).
    """
    text_norm = normalize(text)
    domain_key = domain.upper()
    skill_list = SKILL_DICT.get(domain_key, [])

    found = set()

    for skill in skill_list:
        skill_norm = normalize(skill)
        # Direct substring match
        if skill_norm in text_norm:
            found.add(skill)
            continue
        # Word boundary match for short skills (avoid false positives)
        if len(skill_norm) <= 4:
            pattern = r'\b' + re.escape(skill_norm) + r'\b'
            if re.search(pattern, text_norm):
                found.add(skill)

    # Alias expansion
    for alias, full_skill in ALIASES.items():
        alias_norm = normalize(alias)
        pattern = r'\b' + re.escape(alias_norm) + r'\b'
        if re.search(pattern, text_norm):
            # Add alias as display if it's in domain skills
            if full_skill in [normalize(s) for s in skill_list]:
                found.add(full_skill)
            # Also add raw alias if meaningful
            if alias.upper() in [normalize(s).upper() for s in skill_list]:
                found.add(alias)

    if not found:
        return ["No specific skills detected"]

    # Sort: longer/more specific skills first
    return sorted(found, key=lambda x: -len(x))


def extract_all_skills(text):
    """
    Extract skills across ALL domains.
    Returns dict of {domain: [skills]} sorted by skill count descending.
    """
    text_norm = normalize(text)
    all_found = {}

    for domain, skills in SKILL_DICT.items():
        found = set()
        for skill in skills:
            skill_norm = normalize(skill)
            if skill_norm in text_norm:
                found.add(skill)
                continue
            if len(skill_norm) <= 4:
                pattern = r'\b' + re.escape(skill_norm) + r'\b'
                if re.search(pattern, text_norm):
                    found.add(skill)

        # Alias expansion
        for alias, full_skill in ALIASES.items():
            alias_norm = normalize(alias)
            pattern = r'\b' + re.escape(alias_norm) + r'\b'
            if re.search(pattern, text_norm):
                if full_skill in [normalize(s) for s in skills]:
                    found.add(full_skill)

        if found:
            all_found[domain] = sorted(found, key=lambda x: -len(x))

    # Sort domains by number of skills found
    return dict(sorted(all_found.items(), key=lambda x: -len(x[1])))


def get_skill_score(text, domain):
    """
    Returns a numeric score (0-100) of how well resume matches domain.
    Used for boosting prediction confidence display.
    """
    skills = extract_skills(text, domain)
    if skills == ["No specific skills detected"]:
        return 0
    total = len(SKILL_DICT.get(domain.upper(), []))
    if total == 0:
        return 0
    return round((len(skills) / total) * 100, 1)