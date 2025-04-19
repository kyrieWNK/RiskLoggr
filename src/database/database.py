import sqlite3
import os
from src.models import RiskClassification # Import RiskClassification from models.py
import json # Import json for handling JSON strings
from typing import Optional

DATABASE_FILE = 'riskloggr.db'

def initialize_database():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                basel_ii_category TEXT,
                severity_score INTEGER,
                root_cause TEXT,
                control_recommendations TEXT,
                incident_description TEXT,
                framework_tags TEXT,
                inherent_risk TEXT,
                residual_risk TEXT,
                likelihood TEXT,
                impact_type TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_identity TEXT DEFAULT 'anonymous',
                download_type TEXT
            )
        ''')

        conn.commit()
        print(f"Database initialized: {DATABASE_FILE}")
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}")
    finally:
        if conn:
            conn.close()

def save_classification_result(incident_description: str, classification: RiskClassification) -> Optional[int]:
    """Saves a classification result to the database and returns the row ID."""
    conn = None
    row_id = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # FIIIXED Extract the field from the object
        control_recommendations = classification.control_recommendations
        if isinstance(control_recommendations, list):
            control_recommendations = "\n".join(control_recommendations)

        cursor.execute('''
            INSERT INTO classifications (basel_ii_category, severity_score, root_cause, control_recommendations, incident_description, framework_tags, inherent_risk, residual_risk, likelihood, impact_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            classification.basel_ii_category,
            classification.severity_score,
            classification.root_cause,
            control_recommendations,
            incident_description,
            json.dumps(classification.framework_tags), # Store list as JSON string
            classification.inherent_risk,
            classification.residual_risk,
            classification.likelihood,
            json.dumps(classification.impact_type) # Store list as JSON string
        ))

        conn.commit()
        row_id = cursor.lastrowid
        print(f"Classification result saved to database with ID: {row_id}")
        return row_id
    except sqlite3.Error as e:
        print(f"Database error during save: {e}")
        return None
    finally:
        if conn:
            conn.close()
def get_all_classifications():
    """Fetches all classification records from the database."""
    conn = None
    classifications = []
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM classifications')
        classifications = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error during fetch: {e}")
    finally:
        if conn:
            conn.close()
    return classifications

def update_classification_result(row_id: int, classification: RiskClassification):
    """Updates an existing classification result in the database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        control_recommendations = classification.control_recommendations
        if isinstance(control_recommendations, list):
            control_recommendations = "\n".join(control_recommendations)

        cursor.execute('''
            UPDATE classifications
            SET basel_ii_category = ?,
                severity_score = ?,
                root_cause = ?,
                control_recommendations = ?,
                incident_description = ?,
                framework_tags = ?,
                inherent_risk = ?,
                residual_risk = ?,
                likelihood = ?,
                impact_type = ?
            WHERE id = ?
        ''', (
            classification.basel_ii_category,
            classification.severity_score,
            classification.root_cause,
            control_recommendations,
            classification.incident_description,
            json.dumps(classification.framework_tags),
            classification.inherent_risk,
            classification.residual_risk,
            classification.likelihood,
            json.dumps(classification.impact_type),
            row_id
        ))

        conn.commit()
        print(f"Classification result with ID {row_id} updated in database.")
    except sqlite3.Error as e:
        print(f"Database error during update: {e}")
    finally:
        if conn:
            conn.close()


def log_download(download_type: str, user_identity: str = 'anonymous'):
    """Logs a download event to the database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO download_logs (user_identity, download_type)
            VALUES (?, ?)
        ''', (user_identity, download_type))
        conn.commit()
        print(f"Download event logged: Type='{download_type}', User='{user_identity}'")
    except sqlite3.Error as e:
        print(f"Database error during download logging: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # Example usage (for testing)
    initialize_database()
    # Create a dummy classification object for testing
    class DummyClassification:
        def __init__(self, category, score, cause, recommendations):
            self.basel_ii_category = category
            self.severity_score = score
            self.root_cause = cause
            self.control_recommendations = recommendations

    dummy_incident = "This is a test incident description."
    dummy_classification = DummyClassification("Internal Fraud", 5, "Lack of oversight", "Implement stricter controls")
    save_classification_result(dummy_incident, dummy_classification)
    log_download("test_download", "test_user")\
    
    