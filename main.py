import sqlite3
import subprocess
from manager import setup_database, save_user, verify_user, verify_personal_answer, get_personal_question, save_account, display_accounts, update_account, delete_account_info, save_note, display_notes, export_data, delete_account

# Define color codes
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

def print_colored(message, color):
    print(f"{color}{message}{RESET}")



def password_manager_menu(username):
    while True:
        print("\n" + "-"*30)
        print(f"{BLUE}|{'Password Manager':^28}|{RESET}")
        print("-"*30)
        print(f"{WHITE}| 1. Add an account              |")
        print(f"{WHITE}| 2. View all accounts           |")
        print(f"{WHITE}| 3. Update an account           |")
        print(f"{WHITE}| 4. Delete an account           |")
        print(f"{WHITE}| 6. Go back                     |")
        print("-"*30)

        pm_choice = input("Enter your choice: ")

        if pm_choice == "1":
            title = input("Enter the title for the account: ")
            account_username = input("Enter the username for the account: ")
            password = input("Enter the password for the account: ")
            save_account(username, title, account_username, password)
            print_colored("Account added successfully.", GREEN)
        elif pm_choice == "2":
            display_accounts(username)
            input("Press Enter to go back...")
        elif pm_choice == "3":
            display_accounts(username)
            account_number = int(input("Enter the number of the account to update: ")) - 1
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
            SELECT title, account_username, password FROM accounts WHERE username = ?''', (username,))
            accounts = cursor.fetchall()
            conn.close()

            if 0 <= account_number < len(accounts):
                old_title = accounts[account_number][0]
                print(f"Current details - Title: {old_title}, Username: {accounts[account_number][1]}, Password: {accounts[account_number][2]}")
                new_title = input("Enter the new title: ")
                new_account_username = input("Enter the new username: ")
                new_password = input("Enter the new password: ")
                if verify_personal_answer(username, input("Answer your personal question: ")):
                    update_account(username, old_title, new_title, new_account_username, new_password)
                    print_colored("Account updated successfully.", GREEN)
                else:
                    print_colored("Failed to verify personal answer.", RED)
            else:
                print_colored("Invalid account number.", RED)
        elif pm_choice == "4":
            display_accounts(username)
            account_number = int(input("Enter the number of the account to delete: ")) - 1
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
            SELECT title FROM accounts WHERE username = ?''', (username,))
            accounts = cursor.fetchall()
            conn.close()

            if 0 <= account_number < len(accounts):
                title = accounts[account_number][0]
                if verify_personal_answer(username, input("Answer your personal question: ")):
                    delete_account_info(username, title)
                    print_colored("Account deleted successfully.", GREEN)
                else:
                    print_colored("Failed to verify personal answer.", RED)
            else:
                print_colored("Invalid account number.", RED)

        elif pm_choice == "6":
            break
        else:
            print_colored("Invalid choice. Please try again.", RED)

def logged_in_menu(username):
    while True:
        print("\n" + "-"*30)
        print(f"{BLUE}|{'Logged in as ' + username:^28}|{RESET}")
        print("-"*30)
        print(f"{WHITE}| 1. Password Manager             |")
        print(f"{WHITE}| 2. Add a new note               |")
        print(f"{WHITE}| 3. View all notes               |")
        print(f"{WHITE}| 4. Export data                  |")
        print(f"{WHITE}| 5. Delete account               |")
        print(f"{WHITE}| 6. Logout                       |")
        print("-"*30)
        
        choice = input("Enter your choice: ")

        if choice == "1":
            password_manager_menu(username)
        elif choice == "2":
            title = input("Enter the title of the note: ")
            note = input("Enter the content of the note: ")
            save_note(username, title, note)
            print_colored("Note added successfully.", GREEN)
        elif choice == "3":
            display_notes(username)
            input("Press Enter to go back...")
        elif choice == "4":
            personal_question = get_personal_question(username)
            if personal_question:
                print(f"Personal Question: {personal_question}")
                personal_answer = input("Answer your personal question: ")
                if verify_personal_answer(username, personal_answer):
                    filename = input("Enter the filename to export data to (e.g., backup.json): ")
                    export_data(username, filename)
                    print_colored(f"Data exported to {filename}.", GREEN)
                else:
                    print_colored("Failed to verify personal answer.", RED)
            else:
                print_colored("Personal question not found.", RED)
        elif choice == "5":
            confirm = input("Are you sure you want to delete your account? This action cannot be undone. (yes/no): ")
            if confirm.lower() == "yes":
                delete_account(username)
                print_colored("Account deleted successfully.", GREEN)
                break
        elif choice == "6":
            print_colored("Logging out...", YELLOW)
            break
        else:
            print_colored("Invalid choice. Please try again.", RED)

def main():
    setup_database()  # Ensure the database and tables are set up

    while True:
        print("\n--- Password Manager ---")
        print("1. Login")
        print("2. Register")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            if verify_user(username, password):
                logged_in_menu(username)
            else:
                print_colored("Failed to verify user credentials.", RED)
        elif choice == "2":
            username = input("Enter a username: ")
            
            # Check if username already exists
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            exists = cursor.fetchone()
            conn.close()
            
            if exists:
                print_colored("Username already exists. Please choose a different username.", RED)
                continue

            password = input("Enter a password: ")
            print("Choose a personal question to help retrieve your password:")
            print("1. What is your mother's name?")
            print("2. What is your pet's name?")
            print("3. What is your date of birth?")
            personal_question_choice = input("Enter your choice (1/2/3): ")

            personal_question = ""
            if personal_question_choice == "1":
                personal_question = "What is your mother's name?"
            elif personal_question_choice == "2":
                personal_question = "What is your pet's name?"
            elif personal_question_choice == "3":
                personal_question = "What is your date of birth?"
            else:
                print_colored("Invalid choice. Please try again.", RED)
                continue

            personal_answer = input(f"Answer: ")

            save_user(username, password, personal_question, personal_answer)
            print_colored("Registration successful.", GREEN)
        elif choice == "3":
            print_colored("Goodbye!", CYAN)
            break
        else:
            print_colored("Invalid choice. Please try again.", RED)

if __name__ == "__main__":
    main()
