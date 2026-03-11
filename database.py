import sqlite3
import json
from datetime import datetime

DATABASE = 'proposals.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                budget REAL NOT NULL,
                goals TEXT,
                proposal_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_proposal(company_name, industry, budget, goals, proposal_data):
    # Ensure generated_at is set
    if 'generated_at' not in proposal_data:
        proposal_data['generated_at'] = datetime.now().isoformat()
        
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO proposals (company_name, industry, budget, goals, proposal_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (company_name, industry, budget, goals, json.dumps(proposal_data)))
        conn.commit()
        return cursor.lastrowid

def get_all_proposals():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM proposals ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        proposals = []
        for row in rows:
            data = json.loads(row['proposal_json'])
            data['id'] = row['id']
            proposals.append(data)
        return proposals

def get_proposal_by_id(proposal_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
        row = cursor.fetchone()
        
        if row:
            data = json.loads(row['proposal_json'])
            data['id'] = row['id']
            return data
        return None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
