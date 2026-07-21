import sqlite3
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from pathlib import Path
from config import DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CodeforcesAnalytics:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def get_user_summary(self, handle: str) -> Dict[str, Any]:
        """Fetch general profile summary KPIs."""
        with self.get_connection() as conn:
            user_df = pd.read_sql_query("SELECT * FROM users WHERE handle = ?", conn, params=(handle,))
            if user_df.empty:
                return {}
            
            user = user_df.iloc[0].to_dict()

            # Submissions stats
            subs_df = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total_submissions,
                    COUNT(DISTINCT contest_id || problem_index) as unique_attempted,
                    COUNT(DISTINCT CASE WHEN verdict = 'OK' THEN contest_id || problem_index END) as unique_solved,
                    SUM(CASE WHEN verdict = 'OK' THEN 1 ELSE 0 END) as ac_submissions
                FROM submissions
                WHERE handle = ?
            """, conn, params=(handle,))

            # Contest stats
            contest_df = pd.read_sql_query("""
                SELECT COUNT(*) as total_contests, MAX(new_rating) as peak_rating, MIN(new_rating) as lowest_rating
                FROM rating_history WHERE handle = ?
            """, conn, params=(handle,))

            summary = {**user, **subs_df.iloc[0].to_dict(), **contest_df.iloc[0].to_dict()}
            
            total_subs = summary.get("total_submissions", 0)
            ac_subs = summary.get("ac_submissions", 0)
            summary["overall_accuracy"] = round((ac_subs / total_subs * 100), 2) if total_subs > 0 else 0.0

            return summary

    def get_rating_progression(self, handle: str) -> pd.DataFrame:
        """Fetch contest rating progression over time."""
        with self.get_connection() as conn:
            query = """
                SELECT contest_id, contest_name, rank, old_rating, new_rating, rating_change, rating_update_time
                FROM rating_history
                WHERE handle = ?
                ORDER BY rating_update_epoch ASC
            """
            df = pd.read_sql_query(query, conn, params=(handle,))
            if not df.empty:
                df['contest_num'] = range(1, len(df) + 1)
            return df

    def get_topic_strength_matrix(self, handle: str) -> pd.DataFrame:
        """Analyze accuracy and problem-solving stats grouped by topic tag."""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    st.tag,
                    COUNT(s.submission_id) as total_submissions,
                    COUNT(DISTINCT s.contest_id || s.problem_index) as unique_attempted,
                    COUNT(DISTINCT CASE WHEN s.verdict = 'OK' THEN s.contest_id || s.problem_index END) as unique_solved,
                    SUM(CASE WHEN s.verdict = 'OK' THEN 1 ELSE 0 END) as ac_submissions,
                    AVG(CASE WHEN s.verdict = 'OK' AND s.problem_rating IS NOT NULL THEN s.problem_rating END) as avg_solved_rating
                FROM submission_tags st
                JOIN submissions s ON st.submission_id = s.submission_id
                WHERE st.handle = ?
                GROUP BY st.tag
                HAVING unique_attempted >= 3
                ORDER BY unique_solved DESC
            """
            df = pd.read_sql_query(query, conn, params=(handle,))
            if not df.empty:
                df['accuracy_pct'] = round((df['ac_submissions'] / df['total_submissions']) * 100, 2)
                df['solve_rate_pct'] = round((df['unique_solved'] / df['unique_attempted']) * 100, 2)
                df['avg_solved_rating'] = df['avg_solved_rating'].fillna(0).round(0).astype(int)
            return df

    def get_difficulty_distribution(self, handle: str) -> pd.DataFrame:
        """Analyze success rate across problem difficulty rating bins."""
        with self.get_connection() as conn:
            query = """
                SELECT problem_rating, verdict, contest_id || problem_index as problem_id
                FROM submissions
                WHERE handle = ? AND problem_rating IS NOT NULL
            """
            df = pd.read_sql_query(query, conn, params=(handle,))
            if df.empty:
                return pd.DataFrame()

            # Binning ratings
            bins = [0, 900, 1100, 1300, 1500, 1700, 1900, 2100, 2400, 3500]
            labels = ['800-900', '1000-1100', '1200-1300', '1400-1500', '1600-1700', '1800-1900', '2000-2100', '2200-2400', '2500+']
            
            df['rating_bin'] = pd.cut(df['problem_rating'], bins=bins, labels=labels, right=True)
            
            grouped = df.groupby('rating_bin', observed=False).agg(
                total_submissions=('verdict', 'count'),
                unique_problems=('problem_id', 'nunique'),
                unique_solved=('problem_id', lambda x: df.loc[x.index][df.loc[x.index, 'verdict'] == 'OK']['problem_id'].nunique()),
                ac_submissions=('verdict', lambda x: (x == 'OK').sum())
            ).reset_index()

            grouped['ac_rate_pct'] = np.where(grouped['total_submissions'] > 0, 
                                              round((grouped['ac_submissions'] / grouped['total_submissions']) * 100, 2), 0.0)
            grouped['solve_rate_pct'] = np.where(grouped['unique_problems'] > 0, 
                                                 round((grouped['unique_solved'] / grouped['unique_problems']) * 100, 2), 0.0)
            return grouped

    def get_time_patterns(self, handle: str) -> Dict[str, pd.DataFrame]:
        """Analyze submission activity by Day of Week and Hour of Day."""
        with self.get_connection() as conn:
            dow_query = """
                SELECT day_of_week, 
                       COUNT(*) as total_submissions,
                       SUM(CASE WHEN verdict = 'OK' THEN 1 ELSE 0 END) as ac_submissions
                FROM submissions
                WHERE handle = ? AND day_of_week != ''
                GROUP BY day_of_week
            """
            dow_df = pd.read_sql_query(dow_query, conn, params=(handle,))
            
            # Order days logically
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if not dow_df.empty:
                dow_df['day_of_week'] = pd.Categorical(dow_df['day_of_week'], categories=days_order, ordered=True)
                dow_df = dow_df.sort_values('day_of_week').reset_index(drop=True)
                dow_df['ac_rate_pct'] = round((dow_df['ac_submissions'] / dow_df['total_submissions']) * 100, 2)

            hour_query = """
                SELECT hour_of_day, 
                       COUNT(*) as total_submissions,
                       SUM(CASE WHEN verdict = 'OK' THEN 1 ELSE 0 END) as ac_submissions
                FROM submissions
                WHERE handle = ?
                GROUP BY hour_of_day
                ORDER BY hour_of_day ASC
            """
            hour_df = pd.read_sql_query(hour_query, conn, params=(handle,))
            if not hour_df.empty:
                hour_df['ac_rate_pct'] = round((hour_df['ac_submissions'] / hour_df['total_submissions']) * 100, 2)

            return {"day_of_week": dow_df, "hour_of_day": hour_df}

    def get_practice_vs_contest(self, handle: str) -> pd.DataFrame:
        """Compare performance in Contest vs Practice modes."""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    CASE 
                        WHEN participant_type IN ('CONTESTANT', 'OUT_OF_COMPETITION', 'VIRTUAL') THEN 'Contest/Virtual'
                        ELSE 'Practice'
                    END as mode,
                    COUNT(*) as total_submissions,
                    COUNT(DISTINCT contest_id || problem_index) as unique_problems,
                    COUNT(DISTINCT CASE WHEN verdict = 'OK' THEN contest_id || problem_index END) as unique_solved,
                    SUM(CASE WHEN verdict = 'OK' THEN 1 ELSE 0 END) as ac_submissions,
                    AVG(CASE WHEN verdict = 'OK' AND problem_rating IS NOT NULL THEN problem_rating END) as avg_problem_rating
                FROM submissions
                WHERE handle = ?
                GROUP BY mode
            """
            df = pd.read_sql_query(query, conn, params=(handle,))
            if not df.empty:
                df['ac_rate_pct'] = round((df['ac_submissions'] / df['total_submissions']) * 100, 2)
                df['avg_problem_rating'] = df['avg_problem_rating'].fillna(0).round(0).astype(int)
            return df
