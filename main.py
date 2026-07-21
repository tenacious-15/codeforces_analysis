import argparse
import sys
import logging
from config import DEFAULT_HANDLE, CHARTS_DIR, REPORTS_DIR
from fetcher import CodeforcesFetcher
from database import DatabaseEngine
from analytics import CodeforcesAnalytics
from visualizer import CodeforcesVisualizer
from exporter import ExcelReportExporter

# Ensure stdout supports UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline(handle: str):
    print("\n" + "="*60)
    print(f"Starting Codeforces Analytics Pipeline for handle: '{handle}'")
    print("="*60 + "\n")

    # Step 1: Ingestion
    fetcher = CodeforcesFetcher(handle)
    user_info = fetcher.fetch_user_info()
    if not user_info:
        print(f"Error: User '{handle}' not found on Codeforces or API error.")
        sys.exit(1)

    rating_history = fetcher.fetch_user_rating()
    submissions = fetcher.fetch_user_submissions(count=10000)

    # Step 2: Database Ingestion
    db = DatabaseEngine()
    db.save_user_info(user_info)
    db.save_rating_history(handle, rating_history)
    db.save_submissions(handle, submissions)

    # Step 3: Analytics Engine
    analytics = CodeforcesAnalytics()
    summary = analytics.get_user_summary(handle)
    rating_df = analytics.get_rating_progression(handle)
    topic_df = analytics.get_topic_strength_matrix(handle)
    diff_df = analytics.get_difficulty_distribution(handle)
    time_data = analytics.get_time_patterns(handle)
    practice_df = analytics.get_practice_vs_contest(handle)

    # Print Terminal Dashboard Summary
    print("\n" + "PERFORMANCE KPI SUMMARY".center(60, "-"))
    print(f" Handle:                {summary.get('handle')}")
    print(f" Current Rating:        {summary.get('rating', 'N/A')} ({summary.get('rank', 'N/A')})")
    print(f" Peak Rating:           {summary.get('max_rating', 'N/A')} ({summary.get('max_rank', 'N/A')})")
    print(f" Contests Played:       {summary.get('total_contests', 0)}")
    print(f" Submissions Processed: {summary.get('total_submissions', 0)}")
    print(f" Unique Solved:         {summary.get('unique_solved', 0)}")
    print(f" Accuracy Rate:         {summary.get('overall_accuracy', 0)}%")
    print("-" * 60)

    if not topic_df.empty:
        print("\nTOP 3 STRONGEST TOPICS (By Solved Count):")
        for idx, row in topic_df.head(3).iterrows():
            print(f"  * {row['tag']:<20}: {row['unique_solved']} solved | {row['accuracy_pct']}% accuracy")

        print("\nTOP 3 WEAKEST TOPICS (By Accuracy %):")
        for idx, row in topic_df.sort_values('accuracy_pct').head(3).iterrows():
            print(f"  * {row['tag']:<20}: {row['unique_solved']} solved | {row['accuracy_pct']}% accuracy")
    print("-" * 60 + "\n")

    # Step 4: Visualization
    visualizer = CodeforcesVisualizer(output_dir=CHARTS_DIR)
    r_path = visualizer.plot_rating_progression(handle, rating_df)
    t_path = visualizer.plot_topic_strength(handle, topic_df)
    d_path = visualizer.plot_difficulty_vs_success(handle, diff_df)
    a_path = visualizer.plot_activity_time_pattern(handle, time_data)

    print("Generated Visualizations:")
    print(f"  - {r_path}")
    print(f"  - {t_path}")
    print(f"  - {d_path}")
    print(f"  - {a_path}")

    # Step 5: Excel Report Export
    exporter = ExcelReportExporter(output_dir=REPORTS_DIR)
    excel_path = exporter.export_report(handle, summary, topic_df, rating_df, diff_df)

    print("\n" + "="*60)
    print(f"Pipeline Completed Successfully!")
    print(f"Excel Report saved to: {excel_path}")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Codeforces Analytics Pipeline")
    parser.add_argument("--handle", type=str, default=DEFAULT_HANDLE, help="Codeforces handle to analyze (default: tourist)")
    args = parser.parse_args()
    
    run_pipeline(args.handle)
