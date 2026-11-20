
import streamlit as st  # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
import database

from datetime import date

# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

database.initialize_database()

# Automatically process scheduled transactions.
database.process_due_recurring_transactions()

TODAY = date.today()


# ============================================================
# DESIGN AND STYLING
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F6F6F6;
        color: #171717;
    }

    .block-container {
        max-width: 1500px;
        padding: 2rem 2.5rem 3rem;
    }

    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #292929;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #AAAAAA;
    }

    h1, h2, h3 {
        color: #171717;
        font-weight: 650;
    }

    .subtitle {
        color: #777777;
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 24px;
    }

    .balance-card {
        background: #111111;
        color: #FFFFFF;
        padding: 32px;
        border-radius: 14px;
        margin-bottom: 24px;
    }

    .balance-label {
        color: #BBBBBB;
        font-size: 12px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .balance-amount {
        color: #FFFFFF;
        font-size: 44px;
        font-weight: 700;
        margin: 12px 0;
    }

    .balance-description {
        color: #BBBBBB;
        font-size: 13px;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E7E7E7;
        border-radius: 12px;
        padding: 20px;
    }

    div[data-testid="stMetricLabel"] {
        color: #777777;
    }

    div[data-testid="stMetricValue"] {
        color: #171717;
        font-weight: 650;
        font-size: clamp(18px, 2vw, 28px);
    }

    div[data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E7E7E7;
        border-radius: 12px;
        padding: 22px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button,
    div.stDownloadButton > button {
        background: #111111;
        color: #FFFFFF;
        border: 1px solid #111111;
        border-radius: 7px;
        font-weight: 600;
        min-height: 40px;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    div.stDownloadButton > button:hover {
        background: #444444;
        color: #FFFFFF;
        border-color: #444444;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E7E7E7;
        border-radius: 10px;
    }

    hr {
        border-color: #E5E5E5;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    return f"${value:,.2f}"


def load_data():

    records = database.get_transactions_with_dates()

    data = pd.DataFrame(
        records,
        columns=[
            "ID",
            "Amount",
            "Category",
            "Type",
            "Date"
        ]
    )

    if not data.empty:

        data["Amount"] = pd.to_numeric(
            data["Amount"],
            errors="coerce"
        ).fillna(0)

        data["Date"] = pd.to_datetime(
            data["Date"],
            errors="coerce"
        )

        data = data.dropna(subset=["Date"])

    return data


def calculate_totals(data):

    if data.empty:
        return 0.0, 0.0, 0.0

    income = data.loc[
        data["Type"] == "Income",
        "Amount"
    ].sum()

    expenses = data.loc[
        data["Type"] == "Expense",
        "Amount"
    ].sum()

    balance = income - expenses

    return income, expenses, balance


def display_transactions(data):

    result = data.copy()

    if result.empty:
        return result

    result["Date"] = result["Date"].dt.strftime("%Y-%m-%d")

    result["Amount"] = result["Amount"].map(money)

    return result


def create_csv_download(data, filename, label):

    csv_data = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )


def page_description(description):

    st.markdown(
        f'<p class="subtitle">{description}</p>',
        unsafe_allow_html=True
    )


# Load transaction records.
df = load_data()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown("# FINANCE")
st.sidebar.caption("PERSONAL FINANCE MANAGEMENT")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Transactions",
        "Monthly Reports",
        "Budgets",
        "Spending Analysis",
        "Add Transaction",
        "Manage Transactions",
        "Recurring Transactions"
    ]
)

st.sidebar.divider()

st.sidebar.caption("PERSONAL FINANCE TRACKER")
st.sidebar.caption("Manage your money with clarity.")

st.sidebar.divider()

st.sidebar.caption(
    f"Last opened: {TODAY.strftime('%B %d, %Y')}"
)


# ============================================================
# 1. FINANCIAL OVERVIEW
# ============================================================

if page == "Overview":

    st.title("Financial Overview")

    page_description(
        "Review your financial position, monitor your available "
        "balance, and understand your overall income and spending activity."
    )

    total_income, total_expenses, balance = calculate_totals(df)

    st.markdown(f"""
    <div class="balance-card">
        <div class="balance-label">Available Balance</div>
        <div class="balance-amount">{money(balance)}</div>
        <div class="balance-description">
            Total recorded income less total recorded expenses
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Account Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Income",
        money(total_income)
    )

    col2.metric(
        "Total Expenses",
        money(total_expenses)
    )

    col3.metric(
        "Net Cash Flow",
        money(balance)
    )

    st.divider()

    left, right = st.columns([1.5, 1])

    with left:

        st.subheader("Income and Expenses")

        comparison = pd.DataFrame(
            {"Amount": [total_income, total_expenses]},
            index=["Income", "Expenses"]
        )

        st.bar_chart(comparison)

    with right:

        st.subheader("Account Activity")

        st.metric(
            "Recorded Transactions",
            len(df)
        )

        average = (
            df["Amount"].mean()
            if not df.empty else 0
        )

        st.metric(
            "Average Transaction",
            money(average)
        )

        expense_count = (
            int((df["Type"] == "Expense").sum())
            if not df.empty else 0
        )

        st.metric(
            "Expense Transactions",
            expense_count
        )

    st.divider()

    st.subheader("Recent Transactions")

    if not df.empty:

        recent = display_transactions(
            df.head(6)
        )

        st.dataframe(
            recent[
                ["ID", "Date", "Category", "Type", "Amount"]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No transactions have been recorded yet.")


# ============================================================
# 2. TRANSACTION HISTORY AND SEARCH
# ============================================================

elif page == "Transactions":

    st.title("Transaction History")

    page_description(
        "Review, search, and filter your financial records. "
        "Export your transaction history whenever needed."
    )

    if not df.empty:

        col1, col2, col3 = st.columns(3)

        with col1:

            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )

        with col2:

            categories = sorted(
                df["Category"].unique().tolist()
            )

            category_filter = st.selectbox(
                "Category",
                ["All"] + categories
            )

        with col3:

            months = sorted(
                df["Date"].dt.strftime("%Y-%m").unique().tolist(),
                reverse=True
            )

            month_filter = st.selectbox(
                "Month",
                ["All"] + months
            )

        search_term = st.text_input(
            "Search Transactions",
            placeholder="Search category, type, date, or amount..."
        )

        filtered = df.copy()

        if type_filter != "All":

            filtered = filtered[
                filtered["Type"] == type_filter
            ]

        if category_filter != "All":

            filtered = filtered[
                filtered["Category"] == category_filter
            ]

        if month_filter != "All":

            filtered = filtered[
                filtered["Date"].dt.strftime("%Y-%m") == month_filter
            ]

        if search_term.strip():

            term = search_term.strip().lower()

            searchable = filtered.astype(str).apply(
                lambda column: column.str.lower().str.contains(
                    term,
                    regex=False
                )
            ).any(axis=1)

            filtered = filtered[searchable]

        st.subheader("Transaction Records")

        display = display_transactions(filtered)

        st.dataframe(
            display[
                ["ID", "Date", "Category", "Type", "Amount"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"{len(filtered)} transaction(s) displayed."
        )

        create_csv_download(
            filtered,
            "finance_transactions.csv",
            "Download Filtered Transactions (CSV)"
        )

    else:

        st.info("No transactions available.")


# ============================================================
# 3. MONTHLY FINANCIAL REPORTS
# ============================================================

elif page == "Monthly Reports":

    st.title("Monthly Financial Reports")

    page_description(
        "Review monthly financial activity, compare income and "
        "expenses, and download detailed financial reports."
    )

    month_col, year_col = st.columns(2)

    with month_col:

        selected_month = st.selectbox(
            "Select Month",
            list(range(1, 13)),
            index=TODAY.month - 1,
            format_func=lambda month: date(
                2000, month, 1
            ).strftime("%B")
        )

    if not df.empty:

        available_years = sorted(
            set(df["Date"].dt.year.tolist() + [TODAY.year]),
            reverse=True
        )

    else:

        available_years = [TODAY.year]

    with year_col:

        selected_year = st.selectbox(
            "Select Year",
            available_years
        )

    monthly = df[
        (df["Date"].dt.month == selected_month)
        & (df["Date"].dt.year == selected_year)
    ].copy() if not df.empty else df.copy()

    monthly_income, monthly_expenses, monthly_balance = (
        calculate_totals(monthly)
    )

    st.divider()

    st.subheader(
        date(
            selected_year,
            selected_month,
            1
        ).strftime("%B %Y")
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Monthly Income",
        money(monthly_income)
    )

    c2.metric(
        "Monthly Expenses",
        money(monthly_expenses)
    )

    c3.metric(
        "Monthly Net Cash Flow",
        money(monthly_balance)
    )

    st.divider()

    st.subheader("Monthly Cash Flow")

    monthly_chart = pd.DataFrame(
        {"Amount": [monthly_income, monthly_expenses]},
        index=["Income", "Expenses"]
    )

    st.bar_chart(monthly_chart)

    st.subheader("Monthly Transaction Details")

    if not monthly.empty:

        display = display_transactions(monthly)

        st.dataframe(
            display[
                ["ID", "Date", "Category", "Type", "Amount"]
            ],
            use_container_width=True,
            hide_index=True
        )

        create_csv_download(
            monthly,
            f"finance_report_{selected_year}_{selected_month:02d}.csv",
            "Download Monthly Report (CSV)"
        )

    else:

        st.info("No transactions were recorded for this month.")


# ============================================================
# 4. BUDGET MANAGEMENT
# ============================================================

elif page == "Budgets":

    st.title("Budget Management")

    page_description(
        "Create category-based monthly spending limits, "
        "monitor your expenses, and track your remaining budget."
    )

    selected_budget_month = st.date_input(
        "Choose Budget Month",
        value=date(TODAY.year, TODAY.month, 1)
    )

    budget_month = selected_budget_month.strftime("%Y-%m")

    st.divider()

    st.subheader("Create or Update a Budget")

    with st.form("budget_form"):

        budget_category = st.text_input(
            "Budget Category",
            placeholder="Example: Groceries"
        )

        budget_amount = st.number_input(
            "Monthly Spending Limit ($)",
            min_value=0.01,
            step=10.0
        )

        save_budget_button = st.form_submit_button(
            "Save Budget"
        )

        if save_budget_button:

            if budget_category.strip():

                database.save_budget(
                    budget_category.strip(),
                    budget_month,
                    budget_amount
                )

                st.success("Budget saved successfully.")

                st.rerun()

            else:

                st.error("Please enter a budget category.")

    st.divider()

    st.subheader("Budget Performance")

    budgets = database.get_budgets(budget_month)

    if budgets:

        month_expenses = df[
            (df["Type"] == "Expense")
            & (
                df["Date"].dt.strftime("%Y-%m")
                == budget_month
            )
        ] if not df.empty else pd.DataFrame()

        for category, month, limit in budgets:

            actual = (
                month_expenses.loc[
                    month_expenses["Category"] == category,
                    "Amount"
                ].sum()
                if not month_expenses.empty else 0
            )

            remaining = limit - actual

            progress = (
                min(actual / limit, 1.0)
                if limit > 0 else 0
            )

            st.markdown(f"**{category}**")

            st.progress(progress)

            c1, c2, c3 = st.columns(3)

            c1.metric("Budget", money(limit))
            c2.metric("Spent", money(actual))
            c3.metric("Remaining", money(remaining))

            if actual > limit:

                st.warning(
                    f"You are over budget by {money(actual - limit)}."
                )

            elif progress >= 0.8:

                st.warning(
                    "You have used at least 80% of this budget."
                )

            else:

                st.caption(
                    "Spending is currently within budget."
                )

            if st.button(
                f"Delete {category} Budget",
                key=f"delete_budget_{category}_{month}"
            ):

                database.delete_budget(
                    category,
                    month
                )

                st.rerun()

            st.divider()

    else:

        st.info(
            "No budgets have been created for this month yet."
        )


# ============================================================
# 5. SPENDING ANALYSIS
# ============================================================

elif page == "Spending Analysis":

    st.title("Spending Analysis")

    page_description(
        "Understand how your expenses are distributed across "
        "categories and identify your largest spending areas."
    )

    expenses = (
        df[df["Type"] == "Expense"].copy()
        if not df.empty else pd.DataFrame()
    )

    if not expenses.empty:

        analysis_period = st.selectbox(
            "Analysis Period",
            ["All Time", "This Month", "This Year"]
        )

        if analysis_period == "This Month":

            expenses = expenses[
                (expenses["Date"].dt.month == TODAY.month)
                & (expenses["Date"].dt.year == TODAY.year)
            ]

        elif analysis_period == "This Year":

            expenses = expenses[
                expenses["Date"].dt.year == TODAY.year
            ]

        if not expenses.empty:

            category_totals = (
                expenses.groupby("Category")["Amount"]
                .sum()
                .sort_values(ascending=False)
            )

            total_period_expenses = category_totals.sum()

            st.subheader("Spending by Category")

            st.bar_chart(category_totals)

            st.subheader("Category Breakdown")

            details = category_totals.reset_index()

            details.columns = [
                "Category",
                "Amount"
            ]

            details["Percentage"] = (
                details["Amount"]
                / total_period_expenses
                * 100
            ).map(
                lambda value: f"{value:.1f}%"
            )

            details["Amount"] = details["Amount"].map(money)

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True
            )

            st.metric(
                "Total Expenses for Selected Period",
                money(total_period_expenses)
            )

            create_csv_download(
                category_totals.reset_index(),
                "finance_spending_analysis.csv",
                "Download Spending Analysis (CSV)"
            )

        else:

            st.info(
                "No expenses found for the selected period."
            )

    else:

        st.info(
            "Record expenses to see your spending analysis."
        )


# ============================================================
# 6. ADD TRANSACTION
# ============================================================

elif page == "Add Transaction":

    st.title("Add Transaction")

    page_description(
        "Record money received or spent. Saved transactions "
        "automatically update your financial reports and dashboard."
    )

    with st.form("add_transaction_form"):

        amount = st.number_input(
            "Transaction Amount ($)",
            min_value=0.01,
            step=0.01,
            format="%.2f"
        )

        category = st.text_input(
            "Category",
            placeholder="Example: Salary, Groceries, Transportation"
        )

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Income", "Expense"]
        )

        transaction_date = st.date_input(
            "Transaction Date",
            value=TODAY
        )

        submitted = st.form_submit_button(
            "Save Transaction",
            use_container_width=True
        )

        if submitted:

            if not category.strip():

                st.error(
                    "Please enter a transaction category."
                )

            else:

                database.add_transaction(
                    amount,
                    category.strip(),
                    transaction_type,
                    transaction_date.isoformat()
                )

                st.success(
                    "Transaction saved successfully."
                )

                st.rerun()


# ============================================================
# 7. MANAGE TRANSACTIONS
# ============================================================

elif page == "Manage Transactions":

    st.title("Manage Transactions")

    page_description(
        "Edit transaction details or remove records that "
        "were entered incorrectly."
    )

    if not df.empty:

        transaction_options = {
            (
                f"#{int(row['ID'])} | {row['Category']} | "
                f"{row['Type']} | {money(row['Amount'])} | "
                f"{row['Date'].strftime('%Y-%m-%d')}"
            ): int(row["ID"])
            for _, row in df.iterrows()
        }

        selected_label = st.selectbox(
            "Select Transaction",
            list(transaction_options.keys())
        )

        selected_id = transaction_options[selected_label]

        selected_row = df[
            df["ID"] == selected_id
        ].iloc[0]

        st.divider()

        st.subheader("Edit Transaction")

        with st.form("edit_transaction_form"):

            edit_amount = st.number_input(
                "Amount ($)",
                min_value=0.01,
                value=float(selected_row["Amount"]),
                step=0.01,
                format="%.2f"
            )

            edit_category = st.text_input(
                "Category",
                value=str(selected_row["Category"])
            )

            edit_type = st.selectbox(
                "Transaction Type",
                ["Income", "Expense"],
                index=(
                    0 if selected_row["Type"] == "Income"
                    else 1
                )
            )

            edit_date = st.date_input(
                "Transaction Date",
                value=selected_row["Date"].date()
            )

            update_button = st.form_submit_button(
                "Update Transaction"
            )

            if update_button:

                if not edit_category.strip():

                    st.error(
                        "Category cannot be empty."
                    )

                else:

                    database.update_transaction(
                        selected_id,
                        edit_amount,
                        edit_category.strip(),
                        edit_type,
                        edit_date.isoformat()
                    )

                    st.success(
                        "Transaction updated successfully."
                    )

                    st.rerun()

        st.divider()

        st.subheader("Delete Transaction")

        st.warning(
            "Deleting a transaction permanently removes it "
            "from your database."
        )

        confirm_delete = st.checkbox(
            f"I confirm that I want to delete transaction #{selected_id}."
        )

        if st.button(
            "Delete Selected Transaction",
            disabled=not confirm_delete
        ):

            database.delete_transaction(selected_id)

            st.success("Transaction deleted.")

            st.rerun()

    else:

        st.info(
            "There are no transactions available to manage."
        )


# ============================================================
# 8. RECURRING TRANSACTIONS
# ============================================================

elif page == "Recurring Transactions":

    st.title("Recurring Transactions")

    page_description(
        "Schedule regular income and expenses. Due schedules "
        "are automatically processed when the application opens."
    )

    st.subheader("Create a Recurring Transaction")

    with st.form("recurring_form"):

        recurring_amount = st.number_input(
            "Amount ($)",
            min_value=0.01,
            step=0.01,
            format="%.2f"
        )

        recurring_category = st.text_input(
            "Category",
            placeholder="Example: Rent, Paycheck, Subscription"
        )

        recurring_type = st.selectbox(
            "Transaction Type",
            ["Income", "Expense"]
        )

        frequency = st.selectbox(
            "Frequency",
            ["Weekly", "Monthly"]
        )

        start_date = st.date_input(
            "First Transaction Date",
            value=TODAY
        )

        save_recurring = st.form_submit_button(
            "Create Recurring Schedule"
        )

        if save_recurring:

            if not recurring_category.strip():

                st.error(
                    "Please enter a transaction category."
                )

            elif start_date < TODAY:

                st.error(
                    "Please choose today or a future date."
                )

            else:

                database.add_recurring_transaction(
                    recurring_amount,
                    recurring_category.strip(),
                    recurring_type,
                    frequency,
                    start_date.isoformat()
                )

                st.success(
                    "Recurring schedule created successfully."
                )

                st.rerun()

    st.divider()

    st.subheader("Scheduled Transactions")

    recurring_records = database.get_recurring_transactions()

    if recurring_records:

        recurring_df = pd.DataFrame(
            recurring_records,
            columns=[
                "ID",
                "Amount",
                "Category",
                "Type",
                "Frequency",
                "Next Date",
                "Active"
            ]
        )

        recurring_df["Amount"] = recurring_df["Amount"].map(money)

        recurring_df["Status"] = recurring_df["Active"].map(
            {1: "Active", 0: "Inactive"}
        )

        st.dataframe(
            recurring_df[
                [
                    "ID",
                    "Category",
                    "Type",
                    "Amount",
                    "Frequency",
                    "Next Date",
                    "Status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        active_records = [
            record
            for record in recurring_records
            if record[6] == 1
        ]

        if active_records:

            schedule_options = {
                (
                    f"#{record[0]} | {record[2]} | "
                    f"{record[4]} | {money(record[1])}"
                ): record[0]
                for record in active_records
            }

            selected_schedule = st.selectbox(
                "Select a schedule to deactivate",
                list(schedule_options.keys())
            )

            if st.button(
                "Deactivate Selected Schedule"
            ):

                database.deactivate_recurring_transaction(
                    schedule_options[selected_schedule]
                )

                st.success(
                    "Recurring schedule deactivated."
                )

                st.rerun()

    else:

        st.info(
            "No recurring transactions have been scheduled."
        )


# ============================================================
# END OF APPLICATION
# ============================================================

