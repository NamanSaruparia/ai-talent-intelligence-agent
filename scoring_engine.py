# =====================================
# AI Talent Intelligence Scoring Engine
# =====================================

# -------------------------------------
# Weighted Skill Matrix
# -------------------------------------
skill_weights = {
    "Excel": 10,
    "SQL": 15,
    "HR Analytics": 20,
    "Power BI": 10,
    "Python": 10,
    "Communication": 10,
    "Problem Solving": 15
}


# -------------------------------------
# Calculate Weighted Score
# -------------------------------------
def calculate_score(resume_text):
    """
    Calculates weighted score based on matched skills.
    Returns:
        score (int)
        matched_skills (list)
    """

    score = 0
    matched_skills = []

    for skill, weight in skill_weights.items():
        if skill.lower() in resume_text.lower():
            score += weight
            matched_skills.append(skill)

    return score, matched_skills


# -------------------------------------
# Risk Detection Logic
# -------------------------------------
def detect_risk(resume_text):
    """
    Detects potential risk indicators in resume.
    Returns:
        risks (list)
    """

    risks = []

    # Frequent internships
    if resume_text.lower().count("intern") > 3:
        risks.append("Frequent internships - possible retention risk")

    # Claims analytics but no SQL
    if "analytics" in resume_text.lower() and "sql" not in resume_text.lower():
        risks.append("Claims analytics but lacks SQL")

    # Multiple short roles (simple heuristic)
    if resume_text.lower().count("months") > 4:
        risks.append("Multiple short-duration roles detected")

    return risks


# -------------------------------------
# Skill Gap & Coverage Calculation
# -------------------------------------
def calculate_skill_gap(matched_skills):
    """
    Calculates missing critical skills and coverage percentage.
    Returns:
        missing_skills (list)
        coverage (int)
    """

    required_skills = [
        "Excel",
        "SQL",
        "HR Analytics",
        "Power BI",
        "Communication",
        "Problem Solving"
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in matched_skills
    ]

    coverage = round(
        (len(matched_skills) / len(required_skills)) * 100
    )

    return missing_skills, coverage


# -------------------------------------
# Extract JD Skills
# -------------------------------------
def extract_jd_skills(jd_text):
    """
    Extracts required skills from Job Description
    using predefined skill dictionary.
    Returns:
        jd_skills (list)
    """

    jd_skills = []

    for skill in skill_weights.keys():
        if skill.lower() in jd_text.lower():
            jd_skills.append(skill)

    return jd_skills
