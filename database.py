import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        skills TEXT
    )
    ''')

    cursor.execute('''
    INSERT INTO jobs (job_title, skills)
    SELECT 'Python Developer', 'python flask api mysql'
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs WHERE job_title='Python Developer'
    )
    ''')

    cursor.execute('''
    INSERT INTO jobs (job_title, skills)
    SELECT 'Frontend Developer', 'html css javascript react'
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs WHERE job_title='Frontend Developer'
    )
    ''')

    cursor.execute('''
    INSERT INTO jobs (job_title, skills)
    SELECT 'Data Analyst', 'python pandas sql excel'
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs WHERE job_title='Data Analyst'
    )
    ''')

    cursor.execute('''
    INSERT INTO jobs (job_title, skills)
    SELECT 'AI Engineer', 'python machine learning tensorflow'
    WHERE NOT EXISTS (
        SELECT 1 FROM jobs WHERE job_title='AI Engineer'
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database Created Successfully")