# 🤖 Resume Screening AI Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-ff4b4b)
![Gemini](https://img.shields.io/badge/Powered%20By-Gemini%20AI-4285F4)

An intelligent **AI-powered Resume Screening Bot** built with **Streamlit** and **Gemini AI** 🧠.  
It automatically extracts candidate information from resumes, compares them against a given **Job Description (JD)**, and generates detailed insights such as **fit score**, **skill match**, **experience match**, and **education match**.  
The app also visualizes each candidate’s fit with clean bar charts and allows exporting results to Excel.

---

## 🚀 Features

✅ Upload multiple resumes in **PDF or DOCX** format  
✅ Paste a **Job Description (JD)** (up to 1000 words)  
✅ Extract and display key candidate data:
   - 📧 Email  
   - 📞 Phone number  
   - 📍 Location  
✅ AI-generated evaluation using **Gemini 2.5 Flash**:
   - Fit Score (0–100)
   - Skill Fit
   - Experience Fit
   - Education Fit
   - Strengths & Weakness Summary
✅ Sort results by top candidates automatically  
✅ Download all results as an Excel file (`.xlsx`)  
✅ Visual comparison with interactive **bar charts**  
✅ Optional “Top 5 Comparison” overview chart  

---

## 🧠 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | Streamlit |
| **Backend** | Python |
| **AI Model** | Google Gemini 2.5 Flash |
| **PDF Handling** | PyPDF2 / python-docx |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Export** | Openpyxl |
| **Environment Management** | python-dotenv |

---

## 🛠️ Libraries Used

| Library | Purpose |
|----------|----------|
| `streamlit` | Web app interface |
| `pandas` | Data handling, tabular output |
| `numpy` | Numerical operations for charts |
| `matplotlib` | Graphical visualization (bar charts) |
| `PyPDF2`, `python-docx` | Extract text from resumes |
| `openpyxl` | Excel export functionality |
| `python-dotenv` | Load API keys from `.env` file |
| `google-genai` | Access Gemini API |
| `io` | In-memory file operations |

---

## ⚙️ How It Works

1. User enters the **Job Description (JD)**.  
2. Uploads multiple **PDF or DOCX resumes**.  
3. Each resume is processed:
   - Text is extracted.
   - AI analyzes the match against JD (single Gemini API call).
   - Generates structured JSON:
     ```json
     {
       "fit_score": 87,
       "skill_fit": 90,
       "experience_fit": 80,
       "education_fit": 85,
       "summary": "Excellent Python and ML skills; limited cloud exposure.",
       "keywords_matched": ["Python", "Machine Learning", "Pandas"],
       "keywords_missing": ["AWS", "Docker"]
     }
     ```
4. Results are displayed, sorted by highest score.  
5. The app generates detailed bar charts for top 5 candidates.  
6. The user can download the full report as an Excel file.  

---

## 🧪 Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/resume-screening-ai-bot.git
cd resume-screening-ai-bot
