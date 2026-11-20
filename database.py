import calendar
import sqlite3
from datetime import date, timedelta 

DATABASE_NAME = "finance.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            next_run_date TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]

    if "transaction_date" not in columns:
        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN transaction_date TEXT
        """)

        cursor.execute("""
            UPDATE transactions
            SET transaction_date = ?
            WHERE transaction_date IS NULL
        """, (date.today().isoformat(),))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            UNIQUE(category, month)
        )
    """)

    connection.commit()
    connection.close()


def add_transaction(amount, category, transaction_type,
                    transaction_date=None):

    if transaction_date is None:
        transaction_date = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (amount, category, type, transaction_date)
        VALUES (?, ?, ?, ?)
    """, (
        amount,
        category.strip(),
        transaction_type,
        transaction_date
    ))

    connection.commit()
    connection.close()


def get_transactions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, amount, category, type
        FROM transactions
        ORDER BY id
    """)

    records = cursor.fetchall()
    connection.close()
    return records


def get_transactions_with_dates():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, amount, category, type, transaction_date
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)

    records = cursor.fetchall()
    connection.close()
    return records


def update_transaction(transaction_id, amount, category,
                       transaction_type, transaction_date):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET amount = ?,
            category = ?,
            type = ?,
            transaction_date = ?
        WHERE id = ?
    """, (
        amount,
        category.strip(),
        transaction_type,
        transaction_date,
        transaction_id
    ))

    connection.commit()
    connection.close()


def delete_transaction(transaction_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    connection.commit()
    connection.close()


def save_budget(category, month, amount):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO budgets (category, month, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(category, month)
        DO UPDATE SET amount = excluded.amount
    """, (category.strip(), month, amount))

    connection.commit()
    connection.close()


def get_budgets(month):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, month, amount
        FROM budgets
        WHERE month = ?
        ORDER BY category
    """, (month,))

    records = cursor.fetchall()
    connection.close()
    return records


def delete_budget(category, month):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM budgets
        WHERE category = ? AND month = ?
    """, (category, month))

    connection.commit()
    connection.close()

def add_recurring_transaction(
    amount,
    category,
    transaction_type,
    frequency,
    start_date
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recurring_transactions
        (amount, category, type, frequency, next_run_date, active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (
        amount,
        category.strip(),
        transaction_type,
        frequency,
        start_date
    ))

    connection.commit()
    connection.close()


def get_recurring_transactions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, amount, category, type,
               frequency, next_run_date, active
        FROM recurring_transactions
        ORDER BY next_run_date
    """)

    records = cursor.fetchall()
    connection.close()
    return records


def deactivate_recurring_transaction(recurring_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE recurring_transactions
        SET active = 0
        WHERE id = ?
    """, (recurring_id,))

    connection.commit()
    connection.close()


def advance_recurring_date(current_date, frequency):
    current = date.fromisoformat(current_date)

    if frequency == "Weekly":
        next_date = current + timedelta(days=7)

    elif frequency == "Monthly":
        year = current.year
        month = current.month + 1

        if month > 12:
            month = 1
            year += 1

        last_day = calendar.monthrange(year, month)[1]
        day = min(current.day, last_day)

        next_date = date(year, month, day)

    else:
        raise ValueError("Unsupported recurring frequency.")

    return next_date.isoformat()


def process_due_recurring_transactions():
    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, amount, category, type,
               frequency, next_run_date
        FROM recurring_transactions
        WHERE active = 1 AND next_run_date <= ?
    """, (today,))

    due_records = cursor.fetchall()
    generated_count = 0

    for record in due_records:
        recurring_id, amount, category, transaction_type, frequency, next_date = record

        # Generate each missed occurrence exactly once.
        while next_date <= today:
            cursor.execute("""
                INSERT INTO transactions
                (amount, category, type, transaction_date)
                VALUES (?, ?, ?, ?)
            """, (
                amount,
                category,
                transaction_type,
                next_date
            ))

            next_date = advance_recurring_date(
                next_date,
                frequency
            )

            generated_count += 1

        cursor.execute("""
            UPDATE recurring_transactions
            SET next_run_date = ?
            WHERE id = ?
        """, (next_date, recurring_id))

    connection.commit()
    connection.close()

    return generated_count

