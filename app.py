
import database

# Initialize database
database.initialize_database()

print("================================")
print("     PERSONAL FINANCE TRACKER")
print("================================")


# Add a new transaction
def add_transaction():

    try:
        amount = float(input("Enter transaction amount: $"))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

        category = input("Enter category: ").strip()

        if not category:
            print("Category cannot be empty.")
            return

        transaction_type = input(
            "Enter type (Income/Expense): "
        ).strip().capitalize()

        if transaction_type not in ["Income", "Expense"]:
            print("Invalid transaction type!")
            return

        database.add_transaction(
            amount,
            category,
            transaction_type
        )

        print("Transaction saved successfully!")

    except ValueError:
        print("Please enter a valid amount.")


# View all transactions
def view_transactions():

    transactions = database.get_transactions()

    print("\n========== TRANSACTION HISTORY ==========")

    if not transactions:
        print("No transactions available.")
        return

    for transaction in transactions:

        transaction_id, amount, category, transaction_type = transaction

        print(f"ID: {transaction_id}")
        print(f"Category: {category}")
        print(f"Type: {transaction_type}")
        print(f"Amount: ${amount:.2f}")
        print("-------------------------")


# Calculate total income
def calculate_income():

    transactions = database.get_transactions()

    total_income = sum(
        transaction[1]
        for transaction in transactions
        if transaction[3] == "Income"
    )

    return total_income


# Calculate total expenses
def calculate_expenses():

    transactions = database.get_transactions()

    total_expenses = sum(
        transaction[1]
        for transaction in transactions
        if transaction[3] == "Expense"
    )

    return total_expenses


# Calculate remaining balance
def calculate_balance():

    return calculate_income() - calculate_expenses()


# Display financial summary
def financial_summary():

    print("\n========== FINANCIAL SUMMARY ==========")

    print(f"Total Income: ${calculate_income():.2f}")

    print(f"Total Expenses: ${calculate_expenses():.2f}")

    print(f"Remaining Balance: ${calculate_balance():.2f}")


# Main application menu
def main_menu():

    while True:

        print("\n========== MAIN MENU ==========")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. View Total Income")
        print("4. View Total Expenses")
        print("5. View Remaining Balance")
        print("6. Financial Summary")
        print("7. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            add_transaction()

        elif choice == "2":
            view_transactions()

        elif choice == "3":
            print(f"Total Income: ${calculate_income():.2f}")

        elif choice == "4":
            print(f"Total Expenses: ${calculate_expenses():.2f}")

        elif choice == "5":
            print(f"Remaining Balance: ${calculate_balance():.2f}")

        elif choice == "6":
            financial_summary()

        elif choice == "7":
            print("Thank you for using Personal Finance Tracker!")
            break

        else:
            print("Invalid option. Please try again.")


# Start application
if __name__ == "__main__":
    main_menu()
