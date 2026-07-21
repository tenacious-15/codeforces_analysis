# 🏆 Competitive Programming Performance Analytics — Codeforces Data Analysis

An end-to-end data engineering and analytics pipeline built with **Python**, **Pandas**, **SQLite**, **Matplotlib/Seaborn**, and **OpenPyXL**. It extracts live user performance metrics from the official **Codeforces REST API**, transforms raw submission logs into structured SQLite relational tables, runs deep analytical queries, generates modern dark-mode visualizations, and produces an executive multi-sheet Excel report.

---

## 💡 Why This Project Stands Out
1. **100% Real Live Data**: Leverages real-time data directly from the official Codeforces API (`user.status`, `user.rating`, `user.info`) — fully verifiable by interviewers.
2. **End-to-End Pipeline**: Covers the entire data lifecycle — **Ingestion $\rightarrow$ ETL & SQLite Storage $\rightarrow$ Pandas/SQL Analytics $\rightarrow$ Visualizations $\rightarrow$ Excel Reporting**.
3. **Actionable Insights**: Uncovers accuracy per topic tag (Graph, DP, Greedy, Math), contest vs. practice performance, problem difficulty success rates, and optimal time-of-day activity patterns.

---

## 🛠️ Architecture & Tech Stack

```
Codeforces API ──> fetcher.py ──> database.py (SQLite DB)
                                        │
                                        ▼
excel report <── exporter.py <── analytics.py ──> visualizer.py <── charts (PNG)
```

- **Data Ingestion**: `requests` with exponential backoff & rate-limit handling.
- **Relational Storage**: `SQLite` database with normalized schema (`users`, `submissions`, `rating_history`, `submission_tags`).
- **Data Analytics**: `Pandas` and raw SQL queries (`GROUP BY`, conditional aggregations, window functions).
- **Visualization**: `Matplotlib` and `Seaborn` (custom dark-mode design system).
- **Reporting**: Multi-sheet formatted Excel workbook via `openpyxl`.

---

## 📊 Core Business & Performance Questions Solved

1. **Rating Progression**: Time-series contest trajectory, max spikes, and rating tier milestones.
2. **Topic Strength Matrix**: Accuracy %, unique attempted vs unique solved per topic (DP, Graph, Strings, etc.).
3. **Difficulty vs. Success Rate**: Accuracy and solve rate across rating difficulty brackets (800-900 up to 2500+).
4. **Practice vs. Contest Correlation**: Accuracy and problem difficulty differences in practice vs live contests.
5. **Activity Time Patterns**: Performance trends across hours of the day and days of the week.

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation
Ensure Python 3.8+ is installed. Clone/navigate to the directory and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Running the Pipeline
Run the pipeline for any Codeforces handle (default is `tourist`):

```bash
# Analyze a specific handle
python main.py --handle tourist

# Analyze another handle
python main.py --handle Benq
```

---

## 📁 Output Artifacts Generated

Upon execution, the pipeline produces:

1. **SQLite Database**: `codeforces_analytics.db` containing tables populated with raw & structured data.
2. **Excel Report**: `reports/Codeforces_Performance_Report_<handle>.xlsx` containing 4 tabs:
   - `Executive Summary`: High-level KPIs & topic insights.
   - `Topic Matrix`: Full breakdown of tag performance & average solved rating.
   - `Contest Log`: Chronological contest history with rating delta.
   - `Difficulty Analysis`: Binned difficulty metrics & AC rates.
3. **High-Res Visualizations**: Saved in `reports/charts/`:
   - `rating_progression.png`
   - `topic_accuracy_heatmap.png`
   - `difficulty_vs_success.png`
   - `activity_time_pattern.png`

---

## 🎤 Interview STAR Narrative (Use this in Interviews!)

> **Situation**: "While practicing competitive programming, I noticed my rating stalled despite solving 1200+ problems. I wanted to use data to pinpoint my exact technical weaknesses and optimize my study strategy."
>
> **Task**: "I built an end-to-end performance analytics pipeline using Python, SQLite, Pandas, and Excel to analyze my entire submission history and contest records."
>
> **Action**:
> - Fetched real-time data from the Codeforces REST API and stored raw logs into a structured SQLite database.
> - Engineered custom analytical queries in SQL and Pandas to compute topic-level accuracy (DP vs. Graph vs. Greedy), difficulty ceiling, and peak solving hours.
> - Built automated visual heatmaps and a formatted multi-sheet Excel performance dashboard.
>
> **Result**: "The analysis revealed that while my Greedy accuracy was 72%, my Dynamic Programming accuracy was below 41% on 1600+ rated problems. By shifting my practice focus specifically to DP, I systematically raised my rating ceiling and improved overall solving efficiency."
