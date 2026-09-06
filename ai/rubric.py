RUBRIC = {
    "technical_skills": {
        "max_score": 20,
        "description": (
            "Evaluate the candidate's demonstrated technical skills "
            "relevant to the opportunity."
        ),
        "subcriteria": {
            "skill_match": {
                "max_score": 8,
                "description": (
                    "Evaluate how well the candidate's demonstrated skills "
                    "match the relevant technical requirements."
                ),
                "scoring_bands": {
                    "0": "No relevant technical skills demonstrated.",
                    "1-2": (
                        "Very limited relevance; only a few relevant skills "
                        "or weak evidence."
                    ),
                    "3-4": (
                        "Some relevant skills demonstrated, but important "
                        "requirements are missing."
                    ),
                    "5-6": (
                        "Good coverage of the important technical requirements."
                    ),
                    "7": (
                        "Strong coverage of nearly all important technical "
                        "requirements."
                    ),
                    "8": (
                        "Excellent coverage of the relevant requirements "
                        "with strong supporting evidence."
                    ),
                },
            },

            "proficiency_evidence": {
                "max_score": 7,
                "description": (
                    "Evaluate the strength of evidence that the candidate "
                    "has practically used the claimed technical skills."
                ),
                "scoring_bands": {
                    "0": (
                        "No evidence that the candidate has practically "
                        "used the claimed technical skills."
                    ),
                    "1": (
                        "Skills are mostly listed without meaningful "
                        "supporting evidence."
                    ),
                    "2": (
                        "Limited practical evidence; skills appear in "
                        "basic coursework or simple tasks."
                    ),
                    "3": (
                        "Some practical evidence through projects, "
                        "coursework, or other technical work."
                    ),
                    "4": (
                        "Clear practical use of several relevant skills "
                        "in meaningful work."
                    ),
                    "5": (
                        "Strong practical evidence with repeated or "
                        "substantial use of relevant skills."
                    ),
                    "6": (
                        "Very strong evidence demonstrating independent "
                        "and meaningful application of relevant skills."
                    ),
                    "7": (
                        "Exceptional practical evidence demonstrating "
                        "substantial, independent, and technically "
                        "meaningful use of relevant skills."
                    ),
                },
            },

            "technical_depth": {
                "max_score": 5,
                "description": (
                    "Evaluate the depth of the candidate's technical work, "
                    "including architecture, optimization, debugging, "
                    "testing, or advanced implementation."
                ),
                "scoring_bands": {
                    "0": "No meaningful evidence of technical depth.",
                    "1": (
                        "Mostly basic implementations with little evidence "
                        "of deeper technical work."
                    ),
                    "2": (
                        "Some evidence of technical depth through "
                        "non-trivial implementation or problem solving."
                    ),
                    "3": (
                        "Good technical depth demonstrated through "
                        "meaningful design, debugging, testing, or "
                        "implementation decisions."
                    ),
                    "4": (
                        "Strong technical depth demonstrated through "
                        "advanced implementation, architecture, "
                        "optimization, or complex problem solving."
                    ),
                    "5": (
                        "Exceptional technical depth demonstrated through "
                        "sophisticated architecture, optimization, "
                        "engineering decisions, or technically complex work."
                    ),
                },
            },
        },
    },

    "competitive_achievement": {
        "max_score": 15,
        "description": (
            "Evaluate the quality and strength of the candidate's "
            "demonstrated competitive achievements, considering the "
            "level of competition, result achieved, selectivity, "
            "technical relevance, and strength of evidence."
        ),
        "scoring_bands": {
            "0": "No competitive achievement demonstrated.",
            "1-3": (
                "Participation or very limited recognition with little "
                "evidence of competitive success."
            ),
            "4-6": (
                "Meaningful competitive achievement such as a placement, "
                "finalist status, or comparable recognition."
            ),
            "7-9": (
                "Strong competitive achievement such as a notable "
                "placement, finalist or top-ranked result, or multiple "
                "meaningful achievements."
            ),
            "10-12": (
                "Exceptional achievement such as a major competition win "
                "or highly selective finalist or top placement."
            ),
            "13-15": (
                "Outstanding achievement in a highly selective or "
                "prestigious competition, supported by strong evidence."
            ),
        },
    },

    "relevant_experience": {
        "max_score": 15,
        "description": (
            "Evaluate the candidate's relevant professional, research, "
            "freelance, or other substantial technical experience."
        ),
        "subcriteria": {
            "relevance_and_responsibility": {
                "max_score": 6,
                "description": (
                    "Evaluate how relevant the experience is to the role "
                    "and the level of responsibility held by the candidate."
                ),
                "scoring_bands": {
                    "0": "No relevant experience demonstrated.",
                    "1-2": (
                        "Limited or weakly relevant experience with "
                        "low responsibility."
                    ),
                    "3-4": (
                        "Relevant experience with meaningful responsibilities."
                    ),
                    "5": (
                        "Highly relevant experience with substantial "
                        "responsibility."
                    ),
                    "6": (
                        "Exceptional relevance and responsibility across "
                        "substantial technical work."
                    ),
                },
            },

            "technical_depth": {
                "max_score": 5,
                "description": (
                    "Evaluate the technical complexity and depth of the "
                    "candidate's work within their experience."
                ),
                "scoring_bands": {
                    "0": "No meaningful technical depth demonstrated.",
                    "1": "Mostly basic or routine technical work.",
                    "2": "Some non-trivial technical work demonstrated.",
                    "3": "Good technical depth in meaningful work.",
                    "4": (
                        "Strong technical depth involving complex "
                        "technical problems or systems."
                    ),
                    "5": (
                        "Exceptional technical depth involving "
                        "sophisticated technical work."
                    ),
                },
            },

            "evidence_and_impact": {
                "max_score": 4,
                "description": (
                    "Evaluate the strength of evidence describing the "
                    "candidate's contributions and measurable or "
                    "demonstrated impact."
                ),
                "scoring_bands": {
                    "0": (
                        "No meaningful evidence of contribution or impact."
                    ),
                    "1": (
                        "Responsibilities are mentioned but contribution "
                        "is unclear."
                    ),
                    "2": (
                        "Clear contribution with some evidence of "
                        "outcome or impact."
                    ),
                    "3": (
                        "Strong evidence of meaningful contribution "
                        "and impact."
                    ),
                    "4": (
                        "Exceptional evidence with specific, credible, "
                        "and measurable impact."
                    ),
                },
            },
        },
    },

    "projects": {
        "max_score": 25,
        "description": (
            "Evaluate the quality, technical depth, ownership, relevance, "
            "and demonstrated outcomes of the candidate's projects."
        ),
        "subcriteria": {
            "technical_complexity_and_depth": {
                "max_score": 10,
                "description": (
                    "Evaluate the technical complexity, architecture, "
                    "and depth of the candidate's projects."
                ),
                "scoring_bands": {
                    "0-2": "Little or no meaningful technical complexity.",
                    "3-4": (
                        "Basic projects with limited technical depth."
                    ),
                    "5-6": (
                        "Solid projects involving meaningful technical "
                        "implementation."
                    ),
                    "7-8": (
                        "Strong projects with substantial technical "
                        "complexity or depth."
                    ),
                    "9": (
                        "Very strong technical projects demonstrating "
                        "advanced engineering."
                    ),
                    "10": "Exceptional technical complexity and depth.",
                },
            },

            "ownership_and_implementation": {
                "max_score": 7,
                "description": (
                    "Evaluate how clearly the candidate demonstrates "
                    "ownership and meaningful implementation of the project."
                ),
                "scoring_bands": {
                    "0-1": "Little evidence of personal contribution.",
                    "2-3": (
                        "Some implementation contribution demonstrated."
                    ),
                    "4-5": (
                        "Clear ownership of meaningful implementation."
                    ),
                    "6": (
                        "Strong ownership across substantial project "
                        "components."
                    ),
                    "7": (
                        "Exceptional ownership and implementation depth."
                    ),
                },
            },

            "relevance_and_problem_solving": {
                "max_score": 5,
                "description": (
                    "Evaluate the relevance of the project and the quality "
                    "of the technical problems addressed."
                ),
                "scoring_bands": {
                    "0": (
                        "No meaningful relevance or problem-solving evidence."
                    ),
                    "1-2": (
                        "Limited relevance or relatively simple problem."
                    ),
                    "3": (
                        "Meaningful relevant problem with reasonable "
                        "technical solution."
                    ),
                    "4": (
                        "Strong relevance and problem-solving complexity."
                    ),
                    "5": (
                        "Exceptional relevance and sophisticated "
                        "problem solving."
                    ),
                },
            },

            "evidence_of_outcomes": {
                "max_score": 3,
                "description": (
                    "Evaluate evidence of measurable outcomes, usage, "
                    "deployment, adoption, or demonstrated results."
                ),
                "scoring_bands": {
                    "0": "No outcome or result evidence.",
                    "1": "Some outcome or completion evidence.",
                    "2": (
                        "Clear evidence of deployment, usage, "
                        "or meaningful results."
                    ),
                    "3": (
                        "Strong measurable or independently "
                        "verifiable outcomes."
                    ),
                },
            },
        },
    },

    "demonstrated_potential": {
        "max_score": 15,
        "description": (
            "Evaluate evidence of the candidate's ability to learn, grow, "
            "take initiative, and progress technically based only on "
            "observable evidence in the candidate information."
        ),
        "subcriteria": {
            "learning_and_growth": {
                "max_score": 5,
                "description": (
                    "Evaluate demonstrated technical learning, progression, "
                    "and ability to acquire new skills."
                ),
                "scoring_bands": {
                    "0": "No evidence of technical growth.",
                    "1": (
                        "Limited evidence of learning or progression."
                    ),
                    "2": (
                        "Some evidence of developing technical capability."
                    ),
                    "3": "Clear and sustained technical growth.",
                    "4": (
                        "Strong evidence of rapid or substantial "
                        "technical growth."
                    ),
                    "5": (
                        "Exceptional demonstrated learning trajectory."
                    ),
                },
            },

            "initiative_and_ownership": {
                "max_score": 5,
                "description": (
                    "Evaluate evidence of self-directed technical initiative, "
                    "ownership, experimentation, or problem solving."
                ),
                "scoring_bands": {
                    "0": "No evidence of initiative.",
                    "1": "Limited initiative demonstrated.",
                    "2": "Some self-directed technical work.",
                    "3": (
                        "Clear evidence of initiative and ownership."
                    ),
                    "4": (
                        "Strong independent technical initiative."
                    ),
                    "5": (
                        "Exceptional evidence of self-directed "
                        "technical initiative."
                    ),
                },
            },

            "evidence_of_trajectory": {
                "max_score": 5,
                "description": (
                    "Evaluate evidence suggesting continued technical "
                    "growth based on the candidate's demonstrated progression."
                ),
                "scoring_bands": {
                    "0": (
                        "No evidence supporting future technical growth."
                    ),
                    "1": (
                        "Very limited evidence of progression."
                    ),
                    "2": (
                        "Some evidence of positive technical trajectory."
                    ),
                    "3": (
                        "Clear positive technical trajectory."
                    ),
                    "4": (
                        "Strong trajectory supported by multiple "
                        "concrete indicators."
                    ),
                    "5": (
                        "Exceptional trajectory supported by strong "
                        "and consistent evidence."
                    ),
                },
            },
        },
    },

    "domain_relevance": {
        "max_score": 10,
        "description": (
            "Evaluate how closely the candidate's demonstrated skills, "
            "experience, projects, and technical work align with the "
            "specific domain and requirements of the opportunity."
        ),
        "subcriteria": {
            "domain_alignment": {
                "max_score": 10,
                "description": (
                    "Evaluate how closely the candidate's demonstrated "
                    "technical profile aligns with the specific domain "
                    "and requirements of the opportunity."
                ),
                "scoring_bands": {
                    "0": (
                        "No meaningful alignment with the relevant domain."
                    ),
                    "1-2": "Very limited domain alignment.",
                    "3-4": "Some relevant skills or experience.",
                    "5-6": (
                        "Good alignment across multiple relevant areas."
                    ),
                    "7-8": (
                        "Strong alignment with substantial relevant evidence."
                    ),
                    "9": (
                        "Very strong domain alignment across skills, "
                        "projects, or experience."
                    ),
                    "10": (
                        "Exceptional alignment with extensive, "
                        "directly relevant evidence."
                    ),
                },
            },
        },
    },
}