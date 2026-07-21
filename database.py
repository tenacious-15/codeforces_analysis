import sqlite3
import datetime
import logging
from typing import Dict, Any, List
from pathlib import Path
from config import DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DatabaseEngine:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                handle TEXT PRIMARY KEY,
                rank TEXT,
                max_rank TEXT,
                rating INTEGER,
                max_rating INTEGER,
                avatar TEXT,
                organization TEXT
            );
            """)

            # Rating History Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rating_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                handle TEXT,
                contest_id INTEGER,
                contest_name TEXT,
                rank INTEGER,
                old_rating INTEGER,
                new_rating INTEGER,
                rating_change INTEGER,
                rating_update_time TEXT,
                rating_update_epoch INTEGER,
                FOREIGN KEY (handle) REFERENCES users(handle)
            );
            """)

            # Submissions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id INTEGER PRIMARY KEY,
                handle TEXT,
                contest_id INTEGER,
                problem_index TEXT,
                problem_name TEXT,
                problem_rating INTEGER,
                verdict TEXT,
                passed_test_count INTEGER,
                time_consumed_ms INTEGER,
                memory_consumed_bytes INTEGER,
                programming_language TEXT,
                participant_type TEXT,
                creation_time TEXT,
                creation_epoch INTEGER,
                day_of_week TEXT,
                hour_of_day INTEGER,
                FOREIGN KEY (handle) REFERENCES users(handle)
            );
            """)

            # Submission Tags Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS submission_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER,
                handle TEXT,
                problem_id TEXT,
                tag TEXT,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
            );
            """)

            conn.commit()
        logging.info("Database schema initialized successfully.")

    def save_user_info(self, user_info: Dict[str, Any]):
        if not user_info:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO users (handle, rank, max_rank, rating, max_rating, avatar, organization)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_info.get("handle"),
                user_info.get("rank"),
                user_info.get("maxRank"),
                user_info.get("rating"),
                user_info.get("maxRating"),
                user_info.get("titlePhoto"),
                user_info.get("organization", "")
            ))
            conn.commit()

    def save_rating_history(self, handle: str, rating_history: List[Dict[str, Any]]):
        if not rating_history:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Clear old history for handle
            cursor.execute("DELETE FROM rating_history WHERE handle = ?", (handle,))
            
            for item in rating_history:
                epoch = item.get("ratingUpdateTimeSeconds", 0)
                dt_str = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S') if epoch else ""
                old_r = item.get("oldRating", 0)
                new_r = item.get("newRating", 0)
                cursor.execute("""
                INSERT INTO rating_history 
                (handle, contest_id, contest_name, rank, old_rating, new_rating, rating_change, rating_update_time, rating_update_epoch)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    handle,
                    item.get("contestId"),
                    item.get("contestName"),
                    item.get("rank"),
                    old_r,
                    new_r,
                    new_r - old_r,
                    dt_str,
                    epoch
                ))
            conn.commit()

    def save_submissions(self, handle: str, submissions: List[Dict[str, Any]]):
        if not submissions:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing data for handle
            cursor.execute("DELETE FROM submission_tags WHERE handle = ?", (handle,))
            cursor.execute("DELETE FROM submissions WHERE handle = ?", (handle,))
            
            sub_rows = []
            tag_rows = []

            for sub in submissions:
                sub_id = sub.get("id")
                creation_epoch = sub.get("creationTimeSeconds", 0)
                if creation_epoch:
                    dt = datetime.datetime.fromtimestamp(creation_epoch, tz=datetime.timezone.utc)
                    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    day_of_week = dt.strftime('%A')
                    hour_of_day = dt.hour
                else:
                    dt_str, day_of_week, hour_of_day = "", "", 0

                problem = sub.get("problem", {})
                contest_id = problem.get("contestId", sub.get("contestId"))
                index = problem.get("index", "")
                problem_id = f"{contest_id}{index}" if contest_id and index else ""
                
                author = sub.get("author", {})
                p_type = author.get("participantType", "UNKNOWN")

                sub_rows.append((
                    sub_id,
                    handle,
                    contest_id,
                    index,
                    problem.get("name", ""),
                    problem.get("rating"),
                    sub.get("verdict", "UNKNOWN"),
                    sub.get("passedTestCount", 0),
                    sub.get("timeConsumedMillis", 0),
                    sub.get("memoryConsumedBytes", 0),
                    sub.get("programmingLanguage", ""),
                    p_type,
                    dt_str,
                    creation_epoch,
                    day_of_week,
                    hour_of_day
                ))

                for tag in problem.get("tags", []):
                    tag_rows.append((sub_id, handle, problem_id, tag))

            cursor.executemany("""
            INSERT OR REPLACE INTO submissions 
            (submission_id, handle, contest_id, problem_index, problem_name, problem_rating, 
             verdict, passed_test_count, time_consumed_ms, memory_consumed_bytes, programming_language, 
             participant_type, creation_time, creation_epoch, day_of_week, hour_of_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sub_rows)

            cursor.executemany("""
            INSERT INTO submission_tags (submission_id, handle, problem_id, tag)
            VALUES (?, ?, ?, ?)
            """, tag_rows)

            conn.commit()
        logging.info(f"Saved {len(sub_rows)} submissions and {len(tag_rows)} tag mappings for {handle}.")
