import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from resume_parser import extract_text_from_pdf
from scoring_engine import (
    calculate_score,
    detect_risk,
    calculate_skill_gap,
    extract_jd_skills
)

st.title("🤖 AI Talent Intelligence Agent")
st.write("Campus Hiring AI Screening & JD Matching System")

# Initialize memory
if "candidates" not in st.session_state:
    st.session_state.candidates = []

# Clear button
if st.button("🔄 Clear Previous Evaluations"):
    st.session_state.candidates = []
    st.success("Memory Cleared")

# ===============================
# JD Upload Section
# ===============================
st.subheader("📌 Upload Job Description")

jd_file = st.file_uploader(
    "Upload Job Description (PDF)",
    type="pdf"
)

jd_text = None
jd_skills = []

if jd_file:
    jd_text = extract_text_from_pdf(jd_file)
    jd_skills = extract_jd_skills(jd_text)
    st.write("📋 JD Skills Identified:", jd_skills if jd_skills else "None detected")

# ===============================
# Resume Upload Section
# ===============================
st.subheader("📂 Upload Candidate Resumes")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF)",
    type="pdf",
    accept_multiple_files=True
)

# PDF generator
def generate_pdf_report(name, score, coverage, jd_match, missing_skills, risks, decision):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Candidate Evaluation Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>Name:</b> {name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Score:</b> {score}/100", styles["Normal"]))
    elements.append(Paragraph(f"<b>Skill Coverage:</b> {coverage}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>JD Match:</b> {jd_match if jd_match is not None else 'N/A'}%", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Missing Skills:</b>", styles["Heading3"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(skill, styles["Normal"])) for skill in missing_skills]
        if missing_skills else
        [ListItem(Paragraph("None", styles["Normal"]))]
    ))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Risk Flags:</b>", styles["Heading3"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(risk, styles["Normal"])) for risk in risks]
        if risks else
        [ListItem(Paragraph("None", styles["Normal"]))]
    ))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Final Decision:</b>", styles["Heading3"]))
    elements.append(Paragraph(decision, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ===============================
# Resume Processing
# ===============================
if uploaded_files:

    for uploaded_file in uploaded_files:

        resume_text = extract_text_from_pdf(uploaded_file)

        score, matched_skills = calculate_score(resume_text)
        risks = detect_risk(resume_text)
        missing_skills, coverage = calculate_skill_gap(matched_skills)

        # JD Match Calculation
        if jd_skills:
            jd_match = round(
                (len(set(matched_skills) & set(jd_skills)) / len(jd_skills)) * 100
            )
            missing_from_jd = list(set(jd_skills) - set(matched_skills))
        else:
            jd_match = None
            missing_from_jd = []

        # Decision Logic
        if score >= 80 and not risks:
            decision = "Strong Hire"
        elif score >= 60:
            decision = "Proceed to Round 1"
        else:
            decision = "Reject"

        # Display
        st.subheader(f"📄 {uploaded_file.name}")
        st.write(f"📊 Score: {score}/100")
        st.write(f"📈 Skill Coverage: {coverage}%")

        if jd_match is not None:
            st.write(f"🎯 JD Match: {jd_match}%")
            st.write("📉 Missing JD Skills:", missing_from_jd if missing_from_jd else "None")

        st.write("⚠ Risk Flags:", risks if risks else "None")
        st.write("🧠 Decision:", decision)

        # Generate PDF
        pdf_file = generate_pdf_report(
            uploaded_file.name,
            score,
            coverage,
            jd_match,
            missing_skills,
            risks,
            decision
        )

        st.download_button(
            label="📥 Download Evaluation Report (PDF)",
            data=pdf_file,
            file_name=f"{uploaded_file.name}_evaluation_report.pdf",
            mime="application/pdf"
        )

        # Store candidate
        st.session_state.candidates.append({
            "name": uploaded_file.name,
            "score": score,
            "decision": decision
        })

# ===============================
# Ranking & Dashboard
# ===============================
if st.session_state.candidates:

    st.subheader("🏆 Candidate Ranking")

    ranked = sorted(
        st.session_state.candidates,
        key=lambda x: x["score"],
        reverse=True
    )

    for i, candidate in enumerate(ranked):
        st.write(
            f"Rank {i+1} - {candidate['name']} "
            f"(Score: {candidate['score']}, Decision: {candidate['decision']})"
        )

    df = pd.DataFrame(st.session_state.candidates)
    st.bar_chart(df.set_index("name")["score"])