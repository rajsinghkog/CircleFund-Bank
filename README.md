# CircleFund Bank Application

A simple ATM bank application built with FastAPI. It supports account management and automatic interest calculation over time.

## Features
- Create, update, and delete bank accounts
- Withdraw and deposit funds
- Automatic interest rate applied periodically
- Web interface using Jinja2 templates

## Installation & Setup

1. **Clone the ruv epository:**
    ```bash
    git clone <repo-url>
    cd CircleFund-Bank
    ```
2. **Install [uv](https://github.com/astral-sh/uv) (Python package manager):**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. **Add a package:**
    ```bash
    uv add <package_name>
    ```
4. **Remove a package:**
    ```bash
    uv remove <package_name>
    ```
5. **Install all required packages:**
    ```bash
    uv sync
    ```
6. **Start the FastAPI service:**
    ```bash
    uv run fastapi run bank.py
    ```

## Usage
- Open your browser and go to `http://localhost:8000` to access the web interface.
- Manage accounts and perform transactions directly from the web UI.

## Project Structure
```
├── bank.py           # Main FastAPI application
├── model2.py         # SQLAlchemy models
├── owndatabase.py    # Database setup (to be created)
├── templates/        # Jinja2 HTML templates
│   ├── bankweb.html
│   └── trial.html
└── README.md         # This file
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