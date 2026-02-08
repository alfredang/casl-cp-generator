# WSQ CASL CP Generator

A web application for preparing and submitting WSQ Course Proposal (CP) documents. Uses AI (Claude Agent SDK) to generate professional course content and extracts structured data from Excel files to produce Word and PDF documents.

Built for training providers working with the CASL (Course Accreditation and Standards for Learning) framework.

## Features

### Prepare CP (AI-Powered Content Generation)

Enter a course title and topics, then generate professional content for each CP section:

- **About This Course** -- Professional course description (80-120 words)
- **What You'll Learn** -- Bullet-point learning outcomes
- **Background Part A** -- Targeted sectors, audience, and training needs
- **Background Part B** -- Performance gaps, identification methods, and learner benefits
- **Instruction Methods** -- Elaboration on appropriateness of each selected method
- **Assessment Methods** -- Elaboration on appropriateness of each selected assessment

### Submit CP

- **Entry Requirement** -- Minimum entry requirements (knowledge, skills, attitude, experience)
- **Job Roles** -- 10 relevant job roles following SSG Skills Framework naming
- **Course Outline** -- Topics, instructional methods, and duration per topic
- **Lesson Plan** -- Upload Excel to generate Course Document (.docx), Lesson Plan (.docx), and Lesson Plan (.pdf)

### Course Details

Configure course parameters used across all sections:

- Course duration, number of topics, instructional/assessment hours
- Select instruction methods (19 options) and assessment methods (11 options)
- Auto-calculated duration per topic, per method

## Tech Stack

- **Python 3.13** with **uv** for package management
- **Streamlit** -- Interactive web UI with sidebar navigation
- **Claude Agent SDK** -- AI-powered content generation
- **openpyxl** -- Excel file parsing
- **python-docx** -- Word document generation
- **fpdf2** -- PDF document generation

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install & Run

```bash
# Clone the repo
git clone https://github.com/alfredang/wsq-casl-cp-generator.git
cd wsq-casl-cp-generator

# Install dependencies
uv sync

# Run the app
uv run streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser.

## Project Structure

```
wsq-casl-cp-generator/
├── streamlit_app.py                  # Streamlit web UI with sidebar navigation
├── app/
│   ├── ai_generator.py              # AI prompt templates & generation functions
│   ├── config.py                    # Excel cell reference mappings
│   ├── models.py                    # Pydantic data models
│   ├── extractor.py                 # Excel data extraction
│   ├── generator_docx.py            # Course Document generation (.docx)
│   ├── generator_lesson_plan.py     # Lesson Plan generation (.docx)
│   └── generator_lesson_plan_pdf.py # Lesson Plan generation (.pdf)
├── pyproject.toml                   # Project config & dependencies
└── uv.lock                         # Locked dependencies
```

## License

MIT
