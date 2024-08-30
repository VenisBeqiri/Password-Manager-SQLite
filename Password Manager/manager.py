import sqlite3
import json
from hashlib import sha256
from datetime import datetime

def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # user table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        personal_question TEXT NOT NULL,
        personal_answer TEXT NOT NULL
    )''')

    # notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        username TEXT NOT NULL,
        title TEXT NOT NULL,
        note TEXT NOT NULL,
        date_created TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')

    # accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        username TEXT NOT NULL,
        title TEXT NOT NULL,
        account_username TEXT NOT NULL,
        password TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username),
        PRIMARY KEY (username, title)
    )''')

    conn.commit()
    conn.close()

def save_user(username, password, personal_question, personal_answer):
    hashed_password = sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO users (username, password, personal_question, personal_answer) 
        VALUES (?, ?, ?, ?)''', (username, hashed_password, personal_question, personal_answer))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")
    conn.close()

def verify_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?''', (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_personal_question(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT personal_question FROM users WHERE username = ?''', (username,))
    question = cursor.fetchone()
    conn.close()
    return question[0] if question else None

def verify_personal_answer(username, answer):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT personal_answer FROM users WHERE username = ?''', (username,))
    stored_answer = cursor.fetchone()
    conn.close()
    return stored_answer[0] == answer if stored_answer else False

def get_actual_password(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT password FROM users WHERE username = ?''', (username,))
    password = cursor.fetchone()
    conn.close()
    return password[0] if password else None

def reset_password(username, new_password):
    hashed_password = sha256(new_password.encode()).hexdigest()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE users SET password = ? WHERE username = ?''', (hashed_password, username))
    conn.commit()
    conn.close()

def delete_account(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    cursor.execute('DELETE FROM notes WHERE username = ?', (username,))
    cursor.execute('DELETE FROM accounts WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    print("Account deleted successfully.")

def save_note(username, title, note):
    date_created = datetime.now().isoformat()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO notes (username, title, note, date_created) VALUES (?, ?, ?, ?)''', 
                   (username, title, note, date_created))
    conn.commit()
    conn.close()

def display_notes(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT title, note, date_created FROM notes WHERE username = ?''', (username,))
    notes = cursor.fetchall()
    conn.close()
    
    if notes:
        print("\n--- Your Notes ---")
        for note in notes:
            print(f"Title: {note[0]}")
            print(f"Note: {note[1]}")
            print(f"Date Created: {note[2]}")
            print("-" * 30)
    else:
        print("No notes found.")

def save_account(username, title, account_username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO accounts (username, title, account_username, password) 
    VALUES (?, ?, ?, ?)''', (username, title, account_username, password))
    conn.commit()
    conn.close()
    print("Account added successfully.")

def display_accounts(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT title, account_username, password FROM accounts WHERE username = ?''', (username,))
    accounts = cursor.fetchall()
    conn.close()

    if accounts:
        print("\n--- Your Accounts ---")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. Title: {account[0]} - Username: {account[1]} - Password: {account[2]}")
    else:
        print("No accounts found.")

def update_account(username, old_title, new_title, new_account_username, new_password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE accounts 
    SET title = ?, account_username = ?, password = ?
    WHERE username = ? AND title = ?''', (new_title, new_account_username, new_password, username, old_title))
    conn.commit()
    conn.close()
    print("Account updated successfully.")

def delete_account_info(username, title):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE username = ? AND title = ?', (username, title))
    conn.commit()
    conn.close()
    print("Account deleted successfully.")

def export_data(username, filename):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # export users
    cursor.execute('SELECT username, password, personal_question, personal_answer FROM users WHERE username = ?', (username,))
    users = cursor.fetchall()

    # export notes
    cursor.execute('SELECT username, title, note, date_created FROM notes WHERE username = ?', (username,))
    notes = cursor.fetchall()

    #export accounts
    cursor.execute('SELECT username, title, account_username, password FROM accounts WHERE username = ?', (username,))
    accounts = cursor.fetchall()

    conn.close()

    #save data to JSON file
    with open(filename, 'w') as file:
        json.dump({
            'users': [{'username': user[0], 'password': user[1], 'personal_question': user[2], 'personal_answer': user[3]} for user in users],
            'notes': [{'username': note[0], 'title': note[1], 'note': note[2], 'date_created': note[3]} for note in notes],
            'accounts': [{'username': account[0], 'title': account[1], 'account_username': account[2], 'password': account[3]} for account in accounts]
        }, file, indent=4)

    print(f"Data exported successfully to {filename}")
