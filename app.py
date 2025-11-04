# app.py
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.file_handler import extract_text_from_file
from utils.metadata_extractor import extract_email_phone_location
from utils.similarity_checker import analyze_candidate, calculate_similarity_score
import matplotlib.pyplot as plt
import numpy as np
import os

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(page_title="Resume Screening Bot", layout="centered", page_icon="📑")

st.title("📑 Resume Screening AI Bot")
st.markdown("### Job Description")

# ----------------------------
# Job Description Input
# ----------------------------
jd_input = st.text_area("📝 Job Description (Max 1000 words)", height=250)
word_count = len(jd_input.split())

if word_count > 1000:
    st.warning(f"❗ Word limit exceeded ({word_count}/1000). Please reduce your job description.")
    jd_input = ""  # Clear input if limit exceeded

# ----------------------------
# Resume Upload
# ----------------------------
resume_files = st.file_uploader("📎 Upload Resume Files", type=["pdf", "docx"], accept_multiple_files=True)

# ----------------------------
# Chart Helper Functions
# ----------------------------
def plot_bar_chart(candidate):
    """Draws a clean horizontal bar chart for Skill, Experience, Education fit."""
    categories = ['Skill Fit', 'Experience Fit', 'Education Fit']
    values = [
        float(candidate.get("SkillFit", 0)),
        float(candidate.get("ExperienceFit", 0)),
        float(candidate.get("EducationFit", 0))
    ]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.barh(categories, values, color=['#4CAF50', '#2196F3', '#FFC107'])

    # Label values on bars
    for bar, val in zip(bars, values):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}%", va='center', fontsize=10)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Fit Percentage")
    ax.set_title("Fit Breakdown", fontsize=12, weight='bold')
    plt.tight_layout()
    return fig


def plot_top5_comparison(df):
    """Bar chart comparing top 5 overall scores."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["Resume"], df["ScoreNumeric"], color="#673AB7")
    ax.set_xlabel("Candidate")
    ax.set_ylabel("Overall Fit (%)")
    ax.set_title("Top 5 Overall Fit Scores", fontsize=12, weight="bold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig


# ----------------------------
# Processing and Displaying Results
# ----------------------------
if jd_input and resume_files:
    st.markdown("## 📊 Match Scores")

    results = []
    progress_bar = st.progress(0)
    total = len(resume_files)

    with st.spinner("🤖 Evaluating resumes... Please wait while the AI calculates match scores."):
        for idx, file in enumerate(resume_files):
            try:
                resume_text = extract_text_from_file(file)

                # AI evaluation (single prompt JSON)
                analysis = analyze_candidate(jd_input, resume_text)

                if analysis is None:
                    # fallback to simple numeric score
                    score = calculate_similarity_score(jd_input, resume_text)
                    analysis = {
                        "fit_score": score,
                        "skill_fit": 0.0,
                        "experience_fit": 0.0,
                        "education_fit": 0.0,
                        "summary": "",
                        "keywords_matched": [],
                        "keywords_missing": []
                    }

                email, phone, location = extract_email_phone_location(resume_text)

                results.append({
                    "Resume": file.name,
                    "Score": f"{round(analysis.get('fit_score', 0), 2)}%",
                    "Email": email or "-",
                    "Contact Number": phone or "-",
                    "Location": location or "-",
                    "Summary": analysis.get("summary", ""),
                    "SkillFit": round(analysis.get("skill_fit", 0), 2),
                    "ExperienceFit": round(analysis.get("experience_fit", 0), 2),
                    "EducationFit": round(analysis.get("education_fit", 0), 2),
                    "KeywordsMatched": analysis.get("keywords_matched", []),
                    "KeywordsMissing": analysis.get("keywords_missing", [])
                })

            except Exception as e:
                print(f"Error processing {file.name}: {e}")
                results.append({
                    "Resume": file.name,
                    "Score": "0%",
                    "Email": "-",
                    "Contact Number": "-",
                    "Location": "-",
                    "Summary": "Error processing resume.",
                    "SkillFit": 0.0,
                    "ExperienceFit": 0.0,
                    "EducationFit": 0.0,
                    "KeywordsMatched": [],
                    "KeywordsMissing": []
                })

            # Update progress bar
            progress_bar.progress((idx + 1) / total)

    st.success("✅ Evaluation complete! Here are the results:")

    # Build dataframe and sort by score
    df_results = pd.DataFrame(results)
    df_results['ScoreNumeric'] = df_results['Score'].str.replace('%', '').astype(float)
    df_results = df_results.sort_values(by='ScoreNumeric', ascending=False).reset_index(drop=True)
    df_results['Score'] = df_results['ScoreNumeric'].astype(str) + '%'
    df_results.drop(columns=['ScoreNumeric'], inplace=True)

    # Display table
    st.table(df_results[['Resume', 'Score', 'Email', 'Contact Number', 'Location']])

    # ----------------------------
    # Excel Download
    # ----------------------------
    output = io.BytesIO()
    export_df = df_results.copy()
    export_df['KeywordsMatched'] = export_df['KeywordsMatched'].apply(
        lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else str(x))
    export_df['KeywordsMissing'] = export_df['KeywordsMissing'].apply(
        lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else str(x))

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Results')
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"resume_scores_{timestamp}.xlsx"

    st.download_button(
        label="📥 Download Results as Excel",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ----------------------------
    # Top 5 Visualization Section
    # ----------------------------
    st.markdown("## ⭐ Top 5 Candidates")
    top5 = df_results.head(5)

    for i, row in top5.iterrows():
        # Add top spacing between candidates
        st.markdown("<br>", unsafe_allow_html=True)

        # Alternate layout
        if i % 2 == 0:
            col_details, col_chart = st.columns([3, 2])
        else:
            col_chart, col_details = st.columns([2, 3])

        with col_details:
            st.markdown(
                f"<h4>👤 {row['Resume']} — <b>{row['Score']}</b></h4>",
                unsafe_allow_html=True
            )
            st.markdown(f"📧 <b>Email:</b> {row['Email']}", unsafe_allow_html=True)
            st.markdown(f"📞 <b>Contact:</b> {row['Contact Number']}", unsafe_allow_html=True)
            st.markdown(f"📍 <b>Location:</b> {row['Location']}", unsafe_allow_html=True)

            st.markdown(
                f"<p style='margin-top:10px;'><b>🧾 Summary:</b> {row['Summary'] if row['Summary'] else 'No summary available.'}</p>",
                unsafe_allow_html=True
            )

            matched = row['KeywordsMatched'] if isinstance(row['KeywordsMatched'], list) else str(row['KeywordsMatched']).split(',')
            missing = row['KeywordsMissing'] if isinstance(row['KeywordsMissing'], list) else str(row['KeywordsMissing']).split(',')

            st.markdown(
                f"<p style='color:#00b050;'><b>✅ Matched Skills:</b> {', '.join([m.strip() for m in matched if m.strip()]) or '-'}</p>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='color:#ff4d4d;'><b>❌ Missing Skills:</b> {', '.join([m.strip() for m in missing if m.strip()]) or '-'}</p>",
                unsafe_allow_html=True
            )

        with col_chart:
            candidate_data = {
                "SkillFit": row.get("SkillFit", 0),
                "ExperienceFit": row.get("ExperienceFit", 0),
                "EducationFit": row.get("EducationFit", 0)
            }
            fig = plot_bar_chart(candidate_data)
            st.pyplot(fig)
            plt.close(fig)

        # Add margin + divider between candidates
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)

    # ----------------------------
    # Optional Overall Comparison Chart
    # ----------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📈 Top 5 Overall Comparison")
    top5_numeric = top5.copy()
    top5_numeric['ScoreNumeric'] = top5_numeric['Score'].str.replace('%', '').astype(float)
    fig_compare = plot_top5_comparison(top5_numeric)
    st.pyplot(fig_compare)
    plt.close(fig_compare)

elif jd_input and not resume_files:
    st.info("📂 Please upload at least one resume file (PDF/DOCX) to continue.")
elif resume_files and not jd_input:
    st.info("📝 Please paste the job description above to begin evaluation.")
else:
    st.info("🧠 Enter a job description and upload resumes to start the AI evaluation.")
