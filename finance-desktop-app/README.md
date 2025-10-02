# Finance Desktop Application

A PyQt5-based desktop application for personal finance management.

## Features

- User authentication (login/register)
- Transaction management (add, edit, delete, categorize)
- Dashboard with financial overview
- Data visualization with charts and graphs
- AI-powered transaction categorization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Testing

Run tests with:
```bash
pytest tests/
```

## Architecture

- `main.py` - Application entry point
- `src/ui/` - UI components and windows
- `src/api/` - Backend API communication
- `src/utils/` - Utility functions and helpers
- `tests/` - Unit tests