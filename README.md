# 💰 Personal Finance Tracker

A modern, web-based personal finance management application built with Flask and JavaScript. Track your income and expenses, visualize your financial data, and maintain a clear overview of your financial health — with secure multi-user authentication.

## Deployed Link: [Personal Finance Tracker Live Demo](https://personal-finance-tracker-by-dattpatel.onrender.com)

> 💡 Try it instantly with the **"Try Demo (No Login Required)"** button on the login page — no sign-up needed.

## 🌟 Features

- **🔐 User Authentication**: Secure registration and login with bcrypt password hashing
- **⚡ One-Click Demo**: Explore the app instantly with a pre-seeded demo account
- **💸 Transaction Management**: Add, view, edit, and delete income and expense transactions
- **📊 Financial Summary**: Real-time dashboard showing total income, expenses, and current balance
- **📈 Data Visualization**: Interactive charts powered by Chart.js
- **🏷️ Category Tracking**: Organize transactions by custom categories
- **📤 Excel Export**: Download filtered transactions as a formatted `.xlsx` file
- **💾 Persistent Storage**: SQLite database for reliable data storage
- **📱 Responsive Design**: Mobile-friendly interface with modern CSS styling
- **💱 Currency Support**: Indian Rupee (₹) formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HMTking/personal-finance-tracker-By-DattPatel.git
   cd personal-finance-tracker-By-DattPatel
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

The SQLite database (`finance.db`) is created automatically on first run.

## 🏗️ Project Structure

```
personal-finance-tracker/
│
├── app.py                  # Main Flask application & page routes
├── requirements.txt        # Python dependencies
├── Procfile                # Production start command (gunicorn)
├── runtime.txt             # Python version for deployment
├── .env.example            # Sample environment variables
│
├── models/
│   ├── user.py             # User model (auth, password hashing)
│   └── transaction.py      # Transaction model & summaries
│
├── routes/
│   ├── auth.py             # Auth routes (register, login, demo, settings)
│   ├── transactions.py     # Transaction CRUD & Excel export
│   └── summary.py          # Financial summary endpoints
│
├── utils/
│   └── db.py               # Database connection & schema setup
│
├── static/
│   ├── script.js           # Frontend JavaScript logic
│   └── style.css           # Responsive CSS styling
│
└── templates/
    ├── index.html          # Main dashboard
    ├── login.html          # Login page (with demo button)
    ├── register.html       # Registration page
    └── account_settings.html  # Account settings
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: bcrypt password hashing, session-based auth
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Export**: XlsxWriter
- **Production Server**: Gunicorn

## 📖 API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in with credentials |
| `POST` | `/auth/demo` | One-click demo login (no credentials) |
| `POST` | `/auth/logout` | Log out the current user |
| `GET` | `/auth/me` | Get the current logged-in user |

### Transactions & Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main dashboard page |
| `GET` | `/api/transactions` | Get all transactions |
| `POST` | `/api/transactions` | Add a new transaction |
| `GET` | `/api/transactions/<id>` | Get a single transaction |
| `PUT` | `/api/transactions/<id>` | Update a transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction |
| `POST` | `/api/transactions/download` | Export filtered transactions to Excel |
| `GET` | `/api/summary` | Get overall financial summary |
| `GET` | `/api/summary/current-month` | Get current-month summary |

### Transaction Model

```json
{
  "id": 1,
  "amount": 1500.00,
  "category": "Salary",
  "type": "income",
  "date": "2025-07-31",
  "description": "Monthly salary"
}
```

## 💡 Usage Examples

### Adding a Transaction

1. Fill in the transaction form with:
   - Amount (in rupees)
   - Type (Income or Expense)
   - Category (e.g., Food, Transport, Salary)
   - Date
   - Optional description

2. Click "Add Transaction" to save

### Viewing Financial Summary

The dashboard automatically displays:
- Total income
- Total expenses  
- Current balance (income - expenses)
- Category-wise breakdowns

## 🔧 Configuration

### Database

The application uses SQLite by default. The database file (`finance.db`) is automatically created on first run. No additional configuration required.


## 🔮 Future Enhancements

- [ ] Budget planning and alerts
- [ ] Monthly/yearly financial reports
- [ ] PDF export support
- [ ] Recurring transactions
- [ ] Advanced data analytics and insights

## 📞 Contact

**Datt Patel**  
🎓 **College:** Indian Institute of Information Technology, Surat  
🏆 **GATE CS AIR:** 387  
🏆 **GATE DA AIR:** 877  
📧 **Email:** dattpatel2020@gmail.com  
💼 **LinkedIn:** [Connect with me](https://www.linkedin.com/in/datt-patel-a312a5256/)

---

⭐ **Star this repository if you find it useful!**


