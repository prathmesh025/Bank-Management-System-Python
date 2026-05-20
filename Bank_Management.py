import sqlite3
import json
from datetime import datetime

DB_NAME = "bank.db"

# ---------------- DATABASE SETUP ---------------- #
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    acc_no INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    pin TEXT NOT NULL,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    acc_no INTEGER,
    type TEXT,
    amount REAL,
    date TEXT,
    FOREIGN KEY(acc_no) REFERENCES accounts(acc_no)
)
""")

conn.commit()

# ---------------- FUNCTIONS ---------------- #

def create_account():
    acc_no = int(input("Enter Account Number: "))
    name = input("Enter Name: ")
    pin = input("Set 4-digit PIN: ")
    balance = float(input("Initial Deposit: "))

    try:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                       (acc_no, name, pin, balance))
        conn.commit()
        print("✅ Account created successfully")
    except:
        print("❌ Account number already exists")

def login():
    acc_no = int(input("Enter Account Number: "))
    pin = input("Enter PIN: ")

    cursor.execute("SELECT * FROM accounts WHERE acc_no=? AND pin=?", (acc_no, pin))
    user = cursor.fetchone()

    if user:
        print(f"\nWelcome {user[1]}!")
        account_menu(acc_no)
    else:
        print("❌ Invalid credentials")

def deposit(acc_no):
    amount = float(input("Enter amount to deposit: "))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE acc_no=?", (amount, acc_no))
    conn.commit()
    add_transaction(acc_no, "Deposit", amount)
    print("✅ Deposit successful")

def withdraw(acc_no):
    amount = float(input("Enter amount to withdraw: "))

    cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
    balance = cursor.fetchone()[0]

    if balance >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE acc_no=?", (amount, acc_no))
        conn.commit()
        add_transaction(acc_no, "Withdraw", amount)
        print("✅ Withdrawal successful")
    else:
        print("❌ Insufficient balance")

def check_balance(acc_no):
    cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
    balance = cursor.fetchone()[0]
    print(f"💰 Current Balance: ₹{balance}")

def add_transaction(acc_no, txn_type, amount):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transactions (acc_no, type, amount, date) VALUES (?, ?, ?, ?)",
                   (acc_no, txn_type, amount, date))
    conn.commit()

def transaction_history(acc_no):
    cursor.execute("SELECT type, amount, date FROM transactions WHERE acc_no=?", (acc_no,))
    txns = cursor.fetchall()

    if txns:
        print("\n--- Transaction History ---")
        for txn in txns:
            print(f"{txn[2]} | {txn[0]} | ₹{txn[1]}")
    else:
        print("No transactions found")

def delete_account():
    acc_no = int(input("Enter account number to delete: "))
    cursor.execute("DELETE FROM accounts WHERE acc_no=?", (acc_no,))
    conn.commit()
    print("✅ Account deleted")

def search_account():
    acc_no = int(input("Enter account number: "))
    cursor.execute("SELECT acc_no, name, balance FROM accounts WHERE acc_no=?", (acc_no,))
    user = cursor.fetchone()

    if user:
        print("\nAccount Found")
        print("Account No:", user[0])
        print("Name:", user[1])
        print("Balance:", user[2])
    else:
        print("❌ Account not found")

# ---------------- JSON BACKUP ---------------- #

def export_json():
    cursor.execute("SELECT * FROM accounts")
    data = cursor.fetchall()

    accounts = []
    for row in data:
        accounts.append({
            "acc_no": row[0],
            "name": row[1],
            "pin": row[2],
            "balance": row[3]
        })

    with open("accounts_backup.json", "w") as f:
        json.dump(accounts, f, indent=4)

    print("✅ Data exported to accounts_backup.json")

def import_json():
    try:
        with open("accounts_backup.json", "r") as f:
            accounts = json.load(f)

        for acc in accounts:
            try:
                cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                               (acc["acc_no"], acc["name"], acc["pin"], acc["balance"]))
            except:
                pass

        conn.commit()
        print("✅ Data imported successfully")
    except FileNotFoundError:
        print("❌ Backup file not found")

# ---------------- REPORT ---------------- #

def admin_report():
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM accounts")
    report = cursor.fetchone()

    print("\n--- Admin Report ---")
    print("Total Accounts:", report[0])
    print("Total Bank Balance:", report[1])

# ---------------- ACCOUNT MENU ---------------- #

def account_menu(acc_no):
    while True:
        print("\n1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. Transaction History")
        print("5. Logout")

        choice = input("Enter choice: ")

        if choice == '1':
            deposit(acc_no)
        elif choice == '2':
            withdraw(acc_no)
        elif choice == '3':
            check_balance(acc_no)
        elif choice == '4':
            transaction_history(acc_no)
        elif choice == '5':
            break
        else:
            print("Invalid choice")

# ---------------- MAIN MENU ---------------- #

def main():
    while True:
        print("\n====== BANK MANAGEMENT SYSTEM ======")
        print("1. Create Account")
        print("2. Login")
        print("3. Search Account")
        print("4. Delete Account")
        print("5. Export to JSON")
        print("6. Import from JSON")
        print("7. Admin Report")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            login()
        elif choice == '3':
            search_account()
        elif choice == '4':
            delete_account()
        elif choice == '5':
            export_json()
        elif choice == '6':
            import_json()
        elif choice == '7':
            admin_report()
        elif choice == '8':
            print("Thank you!")
            break
        else:
            print("Invalid choice")

main()
conn.close()