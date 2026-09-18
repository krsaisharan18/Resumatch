# ResumeMatch — Resume Information Extraction & Candidate Matching

ResumeMatch is a **classical NLP-based resume analysis and candidate-job matching system** designed to extract structured information from unstructured resumes and evaluate their relevance against job descriptions.

Unlike LLM-based resume analysis systems, ResumeMatch uses **rule-based and classical NLP techniques** such as Named Entity Recognition (NER), POS tagging, regular expressions, TF-IDF, and cosine similarity. The approach focuses on being **lightweight, explainable, deterministic, and independent of external LLM APIs**.

---

## 🚀 Features

* 📄 Resume text extraction from **PDF and DOCX** files
* 👤 Candidate information extraction
* 📧 Email and phone number extraction using regular expressions
* 🔗 GitHub and LinkedIn profile extraction
* 🧠 Named Entity Recognition using spaCy
* 🏷️ Skill extraction using a curated skills database
* 🔄 Skill alias normalization
* 📊 TF-IDF based resume-job similarity
* 📐 Cosine similarity for candidate-job matching
* 🎯 Skill relevance analysis
* 🏆 Candidate ranking based on matching scores
* 📈 Interactive result visualizations
* 🗂️ Standardized JSON representation of extracted candidate information
* 🧪 Evaluation framework using Precision, Recall, and F1 for information extraction

---

## 🎯 Problem Statement

Recruiters may need to review a large number of resumes for a single job opening. Resumes also differ considerably in formatting, terminology, structure, and content.

Manual screening can therefore be time-consuming and inconsistent.

ResumeMatch addresses this problem through an automated pipeline that:

1. Extracts text from resumes
2. Identifies important candidate information
3. Converts unstructured resume content into structured data
4. Compares resumes against job descriptions
5. Calculates relevance scores
6. Ranks candidates based on their job relevance

---

## 🏗️ System Architecture

```text
                  ┌────────────────────┐
                  │  Resume Upload     │
                  │   PDF / DOCX       │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Document Parser    │
                  │ pdfplumber /       │
                  │ python-docx       │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Text Preprocessing │
                  │ Cleaning /         │
                  │ Normalization      │
                  └─────────┬──────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ Information Extraction       │
             │                              │
             │ • Regex                      │
             │ • spaCy NER                  │
             │ • POS Tagging                │
             │ • Pattern Matching           │
             │ • Skill Dictionary           │
             └──────────────┬───────────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Structured JSON    │
                  │ Candidate Profile │
                  └─────────┬──────────┘
                            │
                 ┌──────────┴───────────┐
                 │                      │
                 ▼                      ▼
        ┌────────────────┐     ┌────────────────┐
        │ Resume         │     │ Job Description│
        │ Representation │     │ Representation │
        └───────┬────────┘     └───────┬────────┘
                │                      │
                └──────────┬───────────┘
                           ▼
                  ┌────────────────────┐
                  │ TF-IDF             │
                  │ Vectorization      │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Cosine Similarity   │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Skill Matching     │
                  │ & Score Generation │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Candidate Ranking  │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Visualization      │
                  │ & Results          │
                  └────────────────────┘
```

---

## 🧰 Tech Stack

| Technology       | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| **Python**       | Core programming language                       |
| **Streamlit**    | Interactive application interface               |
| **spaCy**        | NLP pipeline, NER and POS tagging               |
| **NLTK**         | Classical NLP utilities                         |
| **Regex**        | Structured information extraction               |
| **pdfplumber**   | PDF text extraction                             |
| **python-docx**  | DOCX text extraction                            |
| **scikit-learn** | TF-IDF vectorization and similarity computation |
| **Plotly**       | Interactive visualizations                      |
| **JSON**         | Standardized candidate data representation      |

---

## 🔍 Information Extraction Pipeline

ResumeMatch combines multiple techniques instead of depending on a single NLP method.

### 1. Document Parsing

The system accepts resumes in supported document formats and converts them into machine-readable text.

```text
PDF / DOCX
    ↓
Raw Text
```

---

### 2. Text Preprocessing

Extracted text is normalized before being passed to downstream NLP components.

Typical preprocessing includes:

* whitespace normalization
* line-break normalization
* case normalization where appropriate
* removal of irrelevant formatting artifacts
* text standardization

---

### 3. Regular Expressions

Regex is used for structured entities that follow predictable patterns.

Examples:

```text
Email
Phone Number
GitHub URL
LinkedIn URL
```

For example:

```text
candidate@example.com
```

can be identified using an email pattern.

Regex is particularly useful here because these entities have a relatively well-defined structure.

---

### 4. Named Entity Recognition

spaCy's NLP pipeline is used to identify entities such as:

```text
PERSON
ORG
GPE
DATE
```

NER is particularly useful for entities whose structure cannot reliably be described by a fixed regular expression.

---

### 5. POS Tagging

Part-of-speech information can be used as an additional linguistic signal during information extraction and text processing.

---

### 6. Skill Extraction

ResumeMatch maintains a curated skills database covering technical technologies and relevant professional skills.

Example:

```text
Python
Java
C++
React
MongoDB
SQL
Machine Learning
Docker
AWS
```

Extracted skills are normalized before matching.

---

## 🔄 Skill Alias Normalization

Candidates may represent the same technology in different ways.

For example:

```text
React
ReactJS
React.js
```

can refer to the same underlying technology.

ResumeMatch maps aliases to canonical skill names to reduce false mismatches.

```text
ReactJS
   ↓
React
```

This improves consistency during candidate-job matching.

---

# 📊 Candidate-Job Matching

ResumeMatch uses **TF-IDF and cosine similarity** to compare resume content with a job description.

---

## TF-IDF

TF-IDF stands for **Term Frequency–Inverse Document Frequency**.

It assigns higher importance to terms that are informative within a document while reducing the influence of very common terms.

Conceptually:

```text
TF-IDF = Term Frequency × Inverse Document Frequency
```

Technical terms that are more discriminative for a particular job can therefore contribute more strongly to the document representation.

---

## Cosine Similarity

After TF-IDF vectorization, the resume and job description are represented as numerical vectors.

Cosine similarity measures the similarity between these vectors.

```text
                  A · B
Cosine(A,B) = ─────────────
              ||A|| ||B||
```

The resulting similarity value is used as one component of the candidate-job relevance calculation.

### Why cosine similarity?

Resume lengths can vary significantly. Cosine similarity focuses on the orientation of the vectors rather than simply comparing their magnitude, making it appropriate for text similarity.

---

# 🎯 Skill Matching

In addition to overall textual similarity, explicit skills from the resume and job description can be compared.

Example:

### Resume

```text
Python
Java
SQL
React
MongoDB
```

### Job Description

```text
Python
SQL
Machine Learning
React
AWS
```

### Matched Skills

```text
Python
SQL
React
```

### Missing Skills

```text
Machine Learning
AWS
```

This provides an interpretable view of why a candidate may receive a particular relevance score.

---

# 🏆 Candidate Ranking

For multiple resumes, each candidate receives a matching score.

Conceptually:

```text
Resume A → Score
Resume B → Score
Resume C → Score
Resume D → Score
```

Candidates can then be ordered according to their calculated relevance.

The ranking is intended as a **screening aid**, not a replacement for human recruitment decisions.

---

# 📈 Evaluation

ResumeMatch separates evaluation into two different tasks:

## 1. Information Extraction Evaluation

For extracted entities such as skills, names, emails, and other candidate attributes, the appropriate evaluation metrics include:

* Precision
* Recall
* F1 Score

These require a **manually annotated ground-truth dataset**.

### Precision

Measures how many extracted entities are actually correct.

```text
Precision = TP / (TP + FP)
```

### Recall

Measures how many of the actual entities were successfully extracted.

```text
Recall = TP / (TP + FN)
```

### F1 Score

Balances Precision and Recall.

```text
F1 = 2 × Precision × Recall
          ─────────────────
          Precision + Recall
```

Where:

```text
TP = True Positive
FP = False Positive
FN = False Negative
```

> Numerical Precision, Recall and F1 results should only be reported after evaluating the system against a labeled ground-truth dataset.

---

## 2. Resume-Job Matching Evaluation

Matching is a ranking problem rather than simply an extraction problem.

For a labeled resume-job dataset, useful ranking metrics include:

* Precision@K
* Recall@K
* F1@K
* Mean Reciprocal Rank (MRR)
* Normalized Discounted Cumulative Gain (nDCG)
* Mean Average Precision (MAP)

These metrics evaluate whether relevant candidates are being placed near the top of the ranking.

---

# 🔬 Classical NLP vs LLM-Based Approaches

ResumeMatch intentionally focuses on a **non-LLM classical NLP pipeline**.

### Classical NLP

```text
Regex
+
NER
+
Skill Rules
+
TF-IDF
+
Cosine Similarity
```

### LLM-based approach

```text
Resume
   ↓
LLM / Embedding Model
   ↓
Semantic Representation
   ↓
Matching / Extraction
```

### Classical NLP Advantages

* Explainable processing pipeline
* Low computational requirements
* No external LLM API dependency
* Lower operating cost
* Deterministic behavior
* Easier debugging
* Suitable for structured entities and keyword-oriented matching

### Limitations

* Limited semantic understanding
* Requires maintenance of skill dictionaries and aliases
* Sensitive to document structure and extraction quality
* May miss new or uncommon terminology
* Less capable of understanding implicit skills and contextual meaning

### Possible LLM/Embedding Improvements

Future versions can investigate:

* Sentence-BERT embeddings
* Transformer-based NER
* LLM-assisted information extraction
* Semantic skill matching
* OCR for scanned resumes
* Hybrid classical NLP + embedding architecture

The performance of these alternatives should be compared experimentally on the same dataset rather than assuming that one approach is universally superior.

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/krsaisharan18/Resumatch.git
cd Resumatch
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the required spaCy model if it is not already installed:

```bash
python -m spacy download en_core_web_sm
```

---

# ▶️ Running the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 📂 Project Structure

```text
Resumatch/
│
├── app.py
│
├── src/
│   ├── resume_parser.py
│   ├── matcher.py
│   ├── visualizations.py
│   └── ...
│
├── requirements.txt
│
└── README.md
```

---

# 🔐 Design Considerations

Resume data can contain personally identifiable information such as:

* Names
* Email addresses
* Phone numbers
* Professional profiles
* Employment history

A production implementation should therefore incorporate appropriate:

* access control
* encryption
* secure storage
* data retention policies
* authentication
* audit logging

The current project is primarily an academic prototype demonstrating the NLP and matching pipeline.

---

# ⚠️ Current Limitations

1. Rule-based skill extraction depends on the coverage of the skills database.
2. TF-IDF does not fully capture semantic relationships between different phrases.
3. Complex multi-column or heavily designed resumes may affect text extraction.
4. Scanned/image-based resumes require OCR.
5. Information-extraction metrics require manually annotated ground truth.
6. Matching metrics require relevance-labeled resume-job pairs.
7. The system should be treated as a recruitment-assistance tool rather than an autonomous hiring system.

---

# 🚀 Future Scope

Potential extensions include:

* Sentence-BERT based semantic matching
* Transformer-based NER
* OCR support
* Multilingual resume processing
* Automated experience extraction
* Better education and employment timeline extraction
* Hybrid TF-IDF + embedding matching
* REST API for ATS integration
* Candidate search and filtering
* Database-backed candidate management
* Recruiter authentication
* Large-scale asynchronous resume processing
* Vector database integration
* Experimentation with LLM-based extraction and matching

---

# 📚 Research Direction

The project can be evaluated against multiple approaches:

```text
                 Resume Analysis
                       │
          ┌────────────┴────────────┐
          │                         │
      Non-LLM                    LLM-based
          │                         │
   ┌──────┴──────┐          ┌───────┴──────┐
   │             │          │              │
Keyword       TF-IDF      SBERT           LLM
Matching      + Cosine                   APIs
   │             │          │              │
   └─────────────┴──────────┴──────────────┘
                       │
                       ▼
                  Evaluation
                       │
             ┌─────────┴─────────┐
             │                   │
       Extraction             Matching
             │                   │
        P / R / F1       P@K / R@K / nDCG
```

The goal is to compare approaches using the **same evaluation dataset and ground truth**, considering not only accuracy but also computational cost, latency, explainability, and robustness.

---

# 👨‍💻 Author

**K R Sai Sharan**

B.Tech — Computer Science & Engineering
B M S College of Engineering, Bengaluru

GitHub: [krsaisharan18](https://github.com/krsaisharan18)

---

## ⭐ Project Objective

ResumeMatch was developed to explore how far **classical NLP techniques can be used for resume information extraction and candidate-job matching without depending on Large Language Models**.

The project focuses on building a transparent pipeline where each stage—from document parsing to information extraction and candidate matching—can be inspected, evaluated, and improved independently.
