# CircleFund Bank Application

A simple ATM bank application built with FastAPI. It supports group-based savings with periodic deposits, account management, and automatic interest calculation.

## Features
- Create, update, and delete bank accounts
- Join savings groups with different contribution cycles (daily, weekly, monthly)
- Track and manage periodic deposits
- Automatic deposit reminders and tracking
- Web interface using Jinja2 templates

## Installation & Setup

1. **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd CircleFund-Bank
    ```
2. **Install [uv](https://github.com/astral-sh/uv) (Python package manager):**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. **Install required packages:**
    ```bash
    uv sync
    ```
4. **Set up the database:**
    - Make sure PostgreSQL is installed and running
    - Create a new database for the application
    - Copy the example environment file and update with your database credentials:
      ```bash
      cp .env.example .env
      # Edit the .env file with your database credentials
      ```
    - Update the `DATABASE_URL` in the `.env` file with your database connection string

5. **Install database dependencies:**
    ```bash
    uv add psycopg2-binary
    ```

6. **Run database migrations:**
    ```bash
    uv run python -m app.db.init_db
    ```

6. **Start the FastAPI service:**
    ```bash
    uv run uvicorn app.main:app --reload
    ```

## Deposit Tracking Feature

The application now includes a deposit tracking system that helps users manage their periodic contributions to savings groups:

- **Automatic Deposit Scheduling**: When a user joins a group, the system automatically schedules expected deposits based on the group's contribution cycle (daily, weekly, or monthly).

- **Pending Deposits Dashboard**: Users can see all their pending deposits, including due dates and amounts, on the deposits page.

- **One-Click Payment**: Users can easily make payments for pending deposits with a single click, which automatically fills in the payment form.

- **Deposit History**: A complete history of all deposits made by the user is available, including the date, amount, and status.

- **Overdue Alerts**: The system highlights overdue deposits in red and provides visual indicators to help users stay on track with their contributions.

## Usage
- Open your browser and go to `http://localhost:8000` to access the web interface.
- Manage accounts and perform transactions directly from the web UI.

## Project Structure
```
```

## Requirements
- Python 3.8+
- FastAPI
- SQLAlchemy
- Jinja2
- APScheduler
- Starlette

## License
MIT