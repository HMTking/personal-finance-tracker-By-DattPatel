# 💰 Personal Finance Tracker

A modern, web-based personal finance management application built with Flask and JavaScript. Track your income and expenses, visualize your financial data, and maintain a clear overview of your financial health.

## 🌟 Features

- **💸 Transaction Management**: Add, view, and delete income and expense transactions
- **📊 Financial Summary**: Real-time dashboard showing total income, expenses, and current balance
- **📈 Data Visualization**: Interactive charts powered by Chart.js
- **🏷️ Category Tracking**: Organize transactions by custom categories
- **💾 Persistent Storage**: SQLite database for reliable data storage
- **📱 Responsive Design**: Mobile-friendly interface with modern CSS styling
- **🔄 Real-time Updates**: Dynamic updates without page refresh
- **💱 Currency Support**: Indian Rupee (₹) formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HMTking/Personal-Finance-Tracker.git
   cd Personal-Finance-Tracker
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

## 🏗️ Project Structure

```
finance-tracker/
│
├── app.py                 # Main Flask application
├── finance.db            # SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
│
├── static/
│   ├── script.js        # Frontend JavaScript logic
│   └── style.css        # Responsive CSS styling
│
└── templates/
    └── index.html       # Main HTML template
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Styling**: Custom CSS with responsive design

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main dashboard page |
| `GET` | `/api/transactions` | Get all transactions |
| `POST` | `/api/transactions` | Add a new transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction |
| `GET` | `/api/summary` | Get financial summary |

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

- [ ] User authentication and multi-user support
- [ ] Data export functionality (CSV, PDF)
- [ ] Budget planning and alerts
- [ ] Monthly/yearly financial reports
- [ ] Integration with bank APIs
- [ ] Mobile app version
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


