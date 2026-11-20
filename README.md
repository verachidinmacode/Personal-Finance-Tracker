
# Personal Finance Tracker

A Python-based personal finance management application featuring an interactive dashboard for tracking income, expenses, budgets, and recurring transactions.

## Overview

The Personal Finance Tracker helps users organize financial activity, monitor cash flow, analyze spending habits, and manage monthly budgets through a web-based interface.

Built with Python, SQLite, Pandas, and Streamlit, the application combines database management with interactive financial reporting.

## Features

- **Financial Dashboard:** View available balance, total income, expenses, and net cash flow.
- **Transaction Management:** Add, edit, delete, search, and filter financial transactions.
- **Budget Management:** Set monthly spending limits and monitor category-based budgets.
- **Monthly Reports:** Review monthly income, expenses, and cash flow.
- **Spending Analysis:** Examine spending by category and identify major expense areas.
- **Recurring Transactions:** Schedule weekly and monthly income or expenses.
- **CSV Exports:** Download transaction history and monthly financial reports.

## Technologies

- Python
- SQLite
- Streamlit
- Pandas
- Git
- GitHub

## Project Structure

```text
Personal Finance Tracker/
├── .streamlit/
│   └── config.toml
├── app.py
├── dashboard.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Launch the dashboard:

```bash
python3 -m streamlit run dashboard.py
```

## Database

The application uses SQLite to store transaction records, budgets, and recurring transaction schedules locally.

The database is initialized automatically when the application starts.

## Author

**Vera Chidinma Enweana**

Computer Science & Information Systems Student

Interested in software development, information systems, and technology-driven solutions.
