def detect_domain(text):
    text = text.lower()

    domain_keywords = {
        "TEACHER": [
            "teacher", "teaching", "classroom", "lesson", "students",
            "curriculum", "school", "education", "biology", "ngss", "stem"
        ],
        "INFORMATION-TECHNOLOGY": [
            "python", "java", "software", "developer", "machine learning",
            "sql", "web", "cloud", "api", "javascript", "react", "git",
            "backend", "frontend", "database", "linux", "docker"
        ],
        "HEALTHCARE": [
            "nurse", "doctor", "hospital", "patient", "clinical",
            "medical", "diagnosis", "pharmacy", "health", "surgery",
            "lab", "dna", "pathology", "pcr"
        ],
        "FINANCE": [
            "accounting", "finance", "audit", "tax", "budget", "ledger",
            "investment", "banking", "financial", "balance sheet", "tally", "sap"
        ],
        "ENGINEERING": [
            "mechanical", "civil", "electrical", "autocad", "solidworks",
            "construction", "design", "manufacturing", "cad", "structural"
        ],
        "DESIGNER": [
            "design", "photoshop", "illustrator", "figma", "ui", "ux",
            "graphic", "branding", "creative", "adobe", "typography"
        ],
        "SALES": [
            "sales", "revenue", "target", "client", "crm", "b2b",
            "lead", "pipeline", "negotiation", "account management"
        ],
        "HR": [
            "recruitment", "hr", "human resources", "payroll", "onboarding",
            "talent", "hiring", "performance", "employee", "training"
        ],
        "MARKETING": [
            "marketing", "seo", "social media", "campaign", "brand",
            "digital marketing", "content", "analytics", "advertising"
        ],
        "CHEF": [
            "chef", "cooking", "culinary", "kitchen", "recipe", "food",
            "restaurant", "pastry", "menu", "catering"
        ],
        "FITNESS": [
            "fitness", "trainer", "gym", "nutrition", "workout", "health",
            "exercise", "coaching", "wellness", "sports"
        ],
        "CONSULTANT": [
            "consultant", "strategy", "advisory", "management consulting",
            "stakeholder", "recommendation", "analysis", "framework"
        ],
        "CONSTRUCTION": [
            "construction", "site", "project manager", "contractor",
            "blueprint", "concrete", "safety", "procurement", "scaffolding"
        ],
        "DIGITAL-MEDIA": [
            "video", "editing", "youtube", "content creation", "podcast",
            "media", "animation", "streaming", "premiere", "after effects"
        ],
        "PUBLIC-RELATIONS": [
            "pr", "public relations", "press release", "media relations",
            "communication", "journalist", "reputation", "events"
        ]
    }

    scores = {
        domain: sum(k in text for k in keywords)
        for domain, keywords in domain_keywords.items()
    }

    print(f"  [Domain Scores] { {k: v for k, v in sorted(scores.items(), key=lambda x: -x[1])[:5]} }")
    detected = max(scores, key=scores.get)
    return detected