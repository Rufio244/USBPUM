
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

DB_PATH = "./usbpum_data/usbpum.db"

def init_db():
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript('''
        -- ตารางเก็บข้อมูลการเรียนรู้
        CREATE TABLE IF NOT EXISTS patterns (
            hash TEXT PRIMARY KEY,
            query TEXT,
            response TEXT,
            category TEXT,
            success INTEGER,
            count INTEGER DEFAULT 1,
            created_at TEXT
        );

        -- ตารางเก็บการยืนยันอีเมล์
        CREATE TABLE IF NOT EXISTS email_verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            token TEXT UNIQUE NOT NULL,
            verified INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
    ''')
    conn.close()

def save_pattern(data: Dict):
    conn = sqlite3.connect(DB_PATH)
    h = hashlib.md5(f"{data['query']}|{data['category']}".encode()).hexdigest()[:16]
    conn.execute('''
        INSERT OR REPLACE INTO patterns 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        h, data['query'][:200], data['response'][:300],
        data.get('category', 'general'), data.get('success', 1),
        data.get('count', 1), datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0] or 0
    conn.close()
    return {"total_patterns": total}

# ฟังก์ชันจัดการยืนยันอีเมล์
def create_verification_token(email: str) -> str:
    token = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT OR REPLACE INTO email_verification (email, token, verified, created_at)
        VALUES (?, ?, 0, ?)
    ''', (email, token, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return token

def verify_email_token(token: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        UPDATE email_verification 
        SET verified = 1 
        WHERE token = ? AND created_at > ?
    ''', (token, (datetime.now() - timedelta(days=7)).isoformat()))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def is_email_verified(email: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    result = conn.execute('''
        SELECT verified FROM email_verification WHERE email = ?
    ''', (email,)).fetchone()
    conn.close()
    return result and result[0] == 1

init_db()
