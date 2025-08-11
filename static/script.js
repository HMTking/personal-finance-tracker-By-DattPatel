// Global variables to store application state and data
let transactions = [], filteredTransactions = [], pieChart = null, barChart = null, summaryData = null, currentUser = null;
let currentChartType = 'expense', currentPage = 1, totalPages = 1;
const itemsPerPage = 5, dateFilter = { startDate: null, endDate: null };

async function checkUserAuth() {
    try {
        const response = await fetch('/auth/me');
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            document.getElementById('username').textContent = currentUser.username;
            return true;
        }
        window.location.href = '/login';
        return false;
    } catch {
        showToast('Please log in to continue', 'error');
        setTimeout(() => window.location.href = '/login', 2000);
        return false;
    }
}

async function logout() {
    try {
        const response = await fetch('/auth/logout', { method: 'POST' });
        if (response.ok) window.location.href = '/login';
    } catch {
        showToast('Logout failed. Please try again.', 'error');
    }
}

const categories = {
    income: ['Salary', 'Freelance', 'Business', 'Investment', 'Gift', 'Other Income'],
    expense: [
        'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Education', 'Travel', 'Insurance', 'Other Expense'
    ]
};

// DOM element references
const form = document.getElementById('transaction-form');
const typeIncomeRadio = document.getElementById('type-income');
const typeExpenseRadio = document.getElementById('type-expense');
const categorySelect = document.getElementById('category');
const dateInput = document.getElementById('date');
const transactionsBody = document.getElementById('transactions-body');
const loadingDiv = document.getElementById('loading');
const toast = document.getElementById('toast');

// Application initialization - this function runs when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkUserAuth()) return;
    dateInput.value = new Date().toISOString().split('T')[0];
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    const formatDate = d => `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
    startDateInput.value = formatDate(firstDay);
    endDateInput.value = formatDate(lastDay);
    dateFilter.startDate = startDateInput.value;
    dateFilter.endDate = endDateInput.value;
    setupEventListeners();
    loadTransactions();
    loadSummary();
    initializeTimeframeSummary();
    updateCategories();
});

function initializeTimeframeSummary() {
    ['timeframe-income', 'timeframe-expenses', 'timeframe-balance'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '₹0.00';
    });
    const timeframeDisplay = document.getElementById('timeframe-display');
    if (timeframeDisplay) timeframeDisplay.innerHTML = `<i class="fas fa-calendar"></i> All Transactions`;
}

function setupEventListeners() {
    form.addEventListener('submit', handleAddTransaction);
    [typeIncomeRadio, typeExpenseRadio].forEach(r => r.addEventListener('change', updateCategories));
    ['toggle-income', 'toggle-expense', 'apply-filter', 'clear-filter', 'logout-btn', 'prev-page', 'next-page', 'download-transactions-btn'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id === 'toggle-income') el.addEventListener('click', () => toggleChart('income'));
        else if (id === 'toggle-expense') el.addEventListener('click', () => toggleChart('expense'));
        else if (id === 'apply-filter') el.addEventListener('click', applyDateFilter);
        else if (id === 'clear-filter') el.addEventListener('click', clearDateFilter);
        else if (id === 'logout-btn') el.addEventListener('click', logout);
        else if (id === 'prev-page') el.addEventListener('click', () => changePage(currentPage - 1));
        else if (id === 'next-page') el.addEventListener('click', () => changePage(currentPage + 1));
        else if (id === 'download-transactions-btn') el.addEventListener('click', downloadFilteredTransactions);
    });
    // User dropdown
    const userDropdownBtn = document.getElementById('user-dropdown-btn');
    const userDropdown = userDropdownBtn?.parentElement;
    userDropdownBtn?.addEventListener('click', e => {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
    });
    document.addEventListener('click', e => {
        if (userDropdown && !userDropdown.contains(e.target)) userDropdown.classList.remove('active');
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && userDropdown) userDropdown.classList.remove('active');
    });
}

function updateCategories() {
    const selectedType = typeIncomeRadio.checked ? 'income' : (typeExpenseRadio.checked ? 'expense' : '');
    categorySelect.innerHTML = '<option value="">Select Category</option>';
    (categories[selectedType] || []).forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });
}

async function handleAddTransaction(e) {
    e.preventDefault();
    const selectedType = typeIncomeRadio.checked ? 'income' : (typeExpenseRadio.checked ? 'expense' : '');
    const transactionData = {
        amount: parseFloat(document.getElementById('amount').value),
        type: selectedType,
        category: categorySelect.value,
        date: dateInput.value,
        description: document.getElementById('description').value
    };
    try {
        showLoading(true);
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transactionData)
        });
        const result = await response.json();
        if (response.ok) {
            showToast('Transaction added successfully!', 'success');
            form.reset();
            dateInput.value = new Date().toISOString().split('T')[0];
            categorySelect.innerHTML = '<option value="">Select Category</option>';
            await loadTransactions();
            await loadSummary();
        } else {
            showToast(result.error || 'Failed to add transaction', 'error');
        }
    } catch {
        showToast('Network error. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        transactions = await response.json();
        applyCurrentFilter();
        renderTransactions();
        updateFilterStatus();
    } catch {
        showToast('Failed to load transactions', 'error');
    }
}

function applyCurrentFilter() {
    /**
     * Apply date range filtering to transactions based on current filter settings
     * Updates the filteredTransactions array with transactions that match the date criteria
     */
    
    // Check if any date filters are currently active
    if (dateFilter.startDate || dateFilter.endDate) {
        // Filter transactions based on the date range
        filteredTransactions = transactions.filter(transaction => {
            // Convert transaction date string to Date object for comparison
            const transactionDate = new Date(transaction.date);
            // Convert filter dates to Date objects (null if not set)
            const start = dateFilter.startDate ? new Date(dateFilter.startDate) : null;
            const end = dateFilter.endDate ? new Date(dateFilter.endDate) : null;
            
            // Apply filtering logic based on which dates are set
            if (start && end) {
                // Both start and end dates are set - check if transaction is within range
                return transactionDate >= start && transactionDate <= end;
            } else if (start) {
                // Only start date is set - check if transaction is on or after start date
                return transactionDate >= start;
            } else if (end) {
                // Only end date is set - check if transaction is on or before end date
                return transactionDate <= end;
            }
            // If no filters are set, include all transactions (shouldn't reach here in this condition)
            return true;
        });
    } else {
        // No date filters are active, so show all transactions
        filteredTransactions = [...transactions];
    }
    
    currentPage = 1;
    updatePagination();
}

function applyDateFilter() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    if (!startDate && !endDate) return showToast('Please select at least one date', 'error');
    if (startDate && endDate && new Date(startDate) > new Date(endDate)) return showToast('Start date cannot be after end date', 'error');
    dateFilter.startDate = startDate;
    dateFilter.endDate = endDate;
    applyCurrentFilter();
    renderTransactions();
    calculateFilteredSummary();
    updateFilterStatus();
    showToast('Date filter applied successfully', 'success');
}

function clearDateFilter() {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    dateFilter.startDate = null;
    dateFilter.endDate = null;
    filteredTransactions = [...transactions];
    renderTransactions();
    calculateFilteredSummary();
    updateFilterStatus();
    showToast('Date filter cleared', 'success');
}

function updateFilterStatus() {
    /**
     * Update the filter status indicators and descriptions throughout the UI
     * to show whether filters are active and what period is being displayed
     */
    
    const filterStatusElement = document.getElementById('filter-status').querySelector('.status-indicator');
    const summaryPeriodLabel = document.getElementById('summary-period-label');
    const chartFilterInfo = document.getElementById('chart-filter-info');
    const transactionFilterInfo = document.getElementById('transaction-filter-info');
    
    let periodText = 'All Time';
    let statusClass = 'active';
    
    if (dateFilter.startDate || dateFilter.endDate) {
        statusClass = 'filtered';
        if (dateFilter.startDate && dateFilter.endDate) {
            const startFormatted = new Date(dateFilter.startDate).toLocaleDateString();
            const endFormatted = new Date(dateFilter.endDate).toLocaleDateString();
            periodText = `${startFormatted} to ${endFormatted}`;
        } else if (dateFilter.startDate) {
            const startFormatted = new Date(dateFilter.startDate).toLocaleDateString();
            periodText = `From ${startFormatted}`;
        } else if (dateFilter.endDate) {
            const endFormatted = new Date(dateFilter.endDate).toLocaleDateString();
            periodText = `Until ${endFormatted}`;
        }
    }
    
    // Update filter status indicator
    if (filterStatusElement) {
        filterStatusElement.textContent = periodText;
        filterStatusElement.className = `status-indicator ${statusClass}`;
    }
    
    // Update summary period label
    if (summaryPeriodLabel) {
        summaryPeriodLabel.textContent = `Showing data for: ${periodText}`;
    }
    
    // Update chart filter info
    if (chartFilterInfo) {
        chartFilterInfo.textContent = `Visualizing data for: ${periodText}`;
    }
    
    // Update transaction filter info
    if (transactionFilterInfo) {
        transactionFilterInfo.textContent = `Showing transactions for: ${periodText}`;
    }
}

function renderTransactions() {
    /**
     * Render the transactions table with current transaction data
     * Updates the HTML table to display transactions, handling empty states and formatting
     */
    
    // Clear any existing content in the table body
    transactionsBody.innerHTML = '';
    
    // Determine which data to display based on whether filters are active
    const dataToRender = filteredTransactions.length > 0 || dateFilter.startDate || dateFilter.endDate 
        ? filteredTransactions   // Use filtered data if filters are active or filtered data exists
        : transactions;          // Use all transactions if no filters are active
    
    // Calculate pagination
    totalPages = Math.ceil(dataToRender.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = dataToRender.slice(startIndex, endIndex);
    
    if (dataToRender.length === 0) {
        transactionsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #666; padding: 20px;">${dateFilter.startDate || dateFilter.endDate ? 'No transactions found for the selected date range.' : 'No transactions yet. Add your first transaction above!'}</td></tr>`;
        updatePaginationInfo(0, 0, 0);
        return;
    }
    
    // Loop through each transaction in the current page and create a table row
    paginatedData.forEach(transaction => {
        // Create a new table row element
        const row = document.createElement('tr');
        
        // Format the date for display (convert from YYYY-MM-DD to local format)
        const formattedDate = new Date(transaction.date).toLocaleDateString();
        
        // Determine CSS class for styling based on transaction type
        const typeClass = transaction.type === 'income' ? 'income' : 'expense';
        
        // Determine symbol to show before amount (+ for income, - for expense)
        const typeSymbol = transaction.type === 'income' ? '+' : '-';
        
        // Build the HTML content for this row
        row.innerHTML = `
            <td>${formattedDate}</td>
            <td><span class="${typeClass}">${transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}</span></td>
            <td>${transaction.category}</td>
            <td class="${typeClass}">${typeSymbol}₹${transaction.amount.toFixed(2)}</td>
            <td>${transaction.description || '-'}</td>
            <td>
                <button class="btn-delete" onclick="deleteTransaction(${transaction.id})">
                    Delete
                </button>
            </td>
        `;
        
        // Add the completed row to the table body
        transactionsBody.appendChild(row);
    });
    
    // Update pagination info and controls
    updatePaginationInfo(startIndex + 1, Math.min(endIndex, dataToRender.length), dataToRender.length);
    updatePaginationControls();
}

async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    try {
        showLoading(true);
        const response = await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
        const result = await response.json();
        if (response.ok) {
            showToast('Transaction deleted successfully!', 'success');
            await loadTransactions();
            await loadSummary();
        } else {
            showToast(result.error || 'Failed to delete transaction', 'error');
        }
    } catch {
        showToast('Network error. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadSummary() {
    /**
     * Load financial summary data from the server
     * This includes totals, balance, and category breakdowns for charts
     */
    try {
        // Fetch summary data from the API endpoint
        const response = await fetch('/api/summary');
        // Parse and store the summary data globally for chart operations
        summaryData = await response.json();
        
        // Initialize filtered transactions if not done already
        // This ensures we have data to work with for filtering operations
        if (filteredTransactions.length === 0 && transactions.length > 0) {
            filteredTransactions = [...transactions];  // Copy all transactions to filtered array
        }
        
        // Update summary displays based on whether date filters are active
        if (dateFilter.startDate || dateFilter.endDate) {
            // If date filters are active, calculate summary from filtered data
            calculateFilteredSummary();
        } else {
            // If no filters are active, use the server-provided summary data
            updateSummaryCards(summaryData);  // Update the summary cards display
            updateCharts(summaryData);        // Update the chart visualizations
        }
        
        // Always ensure timeframe summary is updated on initial load
        if (!dateFilter.startDate && !dateFilter.endDate) {
            updateTimeframeSummary(summaryData);
        }
        
    } catch (error) {
        // Handle any errors that occur during the fetch operation
        console.error('Error loading summary:', error);  // Log for debugging
        showToast('Failed to load summary', 'error');    // Show user-friendly error message
    }
}

function calculateFilteredSummary() {
    const dataToCalculate = filteredTransactions;
    
    // Calculate totals from filtered data
    const totalIncome = dataToCalculate
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const totalExpenses = dataToCalculate
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const currentBalance = totalIncome - totalExpenses;
    
    // Calculate categories from filtered data
    const expensesByCategory = {};
    const incomeByCategory = {};
    
    dataToCalculate.forEach(transaction => {
        if (transaction.type === 'expense') {
            expensesByCategory[transaction.category] = 
                (expensesByCategory[transaction.category] || 0) + transaction.amount;
        } else {
            incomeByCategory[transaction.category] = 
                (incomeByCategory[transaction.category] || 0) + transaction.amount;
        }
    });
    
    // Convert to array format
    const expensesArray = Object.entries(expensesByCategory)
        .map(([category, total]) => ({ category, total }))
        .sort((a, b) => b.total - a.total);
    
    const incomeArray = Object.entries(incomeByCategory)
        .map(([category, total]) => ({ category, total }))
        .sort((a, b) => b.total - a.total);
    
    const filteredSummary = {
        total_income: totalIncome,
        total_expenses: totalExpenses,
        current_balance: currentBalance,
        expenses_by_category: expensesArray,
        income_by_category: incomeArray
    };
    
    // Update displays - both main cards and timeframe cards
    updateSummaryCards(filteredSummary);
    updateCharts(filteredSummary);
}

function updateSummaryCards(summary) {
    // Update main summary cards
    document.getElementById('total-income').textContent = `₹${summary.total_income.toFixed(2)}`;
    document.getElementById('total-expenses').textContent = `₹${summary.total_expenses.toFixed(2)}`;
    
    const balanceElement = document.getElementById('current-balance');
    balanceElement.textContent = `₹${summary.current_balance.toFixed(2)}`;
    
    // Color the balance based on positive/negative
    if (summary.current_balance >= 0) {
        balanceElement.style.color = '#4CAF50';
    } else {
        balanceElement.style.color = '#f44336';
    }
    
    // Update timeframe summary cards
    updateTimeframeSummary(summary);
}

function updateTimeframeSummary(summary) {
    // Update timeframe summary cards
    const timeframeIncome = document.getElementById('timeframe-income');
    const timeframeExpenses = document.getElementById('timeframe-expenses');
    const timeframeBalance = document.getElementById('timeframe-balance');
    const timeframeDisplay = document.getElementById('timeframe-display');
    
    if (timeframeIncome) {
        timeframeIncome.textContent = `₹${summary.total_income.toFixed(2)}`;
    }
    if (timeframeExpenses) {
        timeframeExpenses.textContent = `₹${summary.total_expenses.toFixed(2)}`;
    }
    if (timeframeBalance) {
        timeframeBalance.textContent = `₹${summary.current_balance.toFixed(2)}`;
        
        // Color the timeframe balance based on positive/negative
        if (summary.current_balance >= 0) {
            timeframeBalance.style.color = '#4CAF50';
        } else {
            timeframeBalance.style.color = '#f44336';
        }
    }
    
    // Update timeframe display text
    if (timeframeDisplay) {
        if (dateFilter.startDate || dateFilter.endDate) {
            let dateText = '';
            if (dateFilter.startDate && dateFilter.endDate) {
                const startDate = new Date(dateFilter.startDate).toLocaleDateString();
                const endDate = new Date(dateFilter.endDate).toLocaleDateString();
                dateText = `${startDate} - ${endDate}`;
            } else if (dateFilter.startDate) {
                const startDate = new Date(dateFilter.startDate).toLocaleDateString();
                dateText = `From ${startDate}`;
            } else if (dateFilter.endDate) {
                const endDate = new Date(dateFilter.endDate).toLocaleDateString();
                dateText = `Until ${endDate}`;
            }
            timeframeDisplay.innerHTML = `<i class="fas fa-calendar-check"></i> ${dateText}`;
        } else {
            timeframeDisplay.innerHTML = `<i class="fas fa-calendar"></i> All Transactions`;
        }
    }
}

function updateCharts(summary) {
    // Store current summary for chart toggling
    summaryData = summary;
    updatePieChart();
    updateBarChart(summary);
}

function toggleChart(type) {
    currentChartType = type;
    
    // Update button states
    document.getElementById('toggle-income').classList.remove('active');
    document.getElementById('toggle-expense').classList.remove('active');
    document.getElementById(`toggle-${type}`).classList.add('active');
    
    // Update chart title
    const title = document.getElementById('pie-chart-title');
    title.textContent = type === 'income' ? 'Income by Category' : 'Expenses by Category';
    
    // Update pie chart
    updatePieChart();
}

function updatePieChart() {
    const ctx = document.getElementById('pie-chart').getContext('2d');
    
    // Destroy existing chart
    if (pieChart) {
        pieChart.destroy();
    }
    
    if (!summaryData) {
        return;
    }
    
    // Get data based on current chart type
    const categoryData = currentChartType === 'income' 
        ? summaryData.income_by_category 
        : summaryData.expenses_by_category;
    
    if (categoryData.length === 0) {
        // Show "No data" message
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText(
            `No ${currentChartType} data available`, 
            ctx.canvas.width / 2, 
            ctx.canvas.height / 2
        );
        return;
    }
    
    const labels = categoryData.map(item => item.category);
    const data = categoryData.map(item => item.total);
    
    // Generate colors based on chart type
    const colors = currentChartType === 'income' 
        ? generateIncomeColors(labels.length)
        : generateExpenseColors(labels.length);
    
    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 3,
                borderColor: '#fff',
                hoverBorderWidth: 4,
                hoverBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%', // This creates the ring effect - 60% hollow center
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ₹${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            },
            elements: {
                arc: {
                    borderJoinStyle: 'round'
                }
            }
        }
    });
}

function updateBarChart(summary) {
    const ctx = document.getElementById('bar-chart').getContext('2d');
    
    // Destroy existing chart
    if (barChart) {
        barChart.destroy();
    }
    
    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Income', 'Expenses', 'Balance'],
            datasets: [{
                label: 'Amount (₹)',
                data: [
                    summary.total_income,
                    summary.total_expenses,
                    Math.abs(summary.current_balance)
                ],
                backgroundColor: [
                    '#4CAF50',
                    '#f44336',
                    summary.current_balance >= 0 ? '#2196F3' : '#FF9800'
                ],
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.parsed.y;
                            if (context.dataIndex === 2) { // Balance
                                value = summary.current_balance;
                            }
                            return `${context.label}: ₹${value.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

function generateColors(count) {
    // General high-contrast color palette with distinct colors
    const colors = [
        '#FF6384', // Pink/Red
        '#36A2EB', // Blue
        '#FFCE56', // Yellow
        '#4BC0C0', // Teal
        '#9966FF', // Purple
        '#FF9F40', // Orange
        '#FF6384', // Pink (repeat for more categories)
        '#C9CBCF', // Grey
        '#4BC0C0', // Teal (repeat)
        '#E7E9ED', // Light grey
        '#71B37C', // Green
        '#B19CD9'  // Light purple
    ];
    
    return colors.slice(0, count);
}

function generateIncomeColors(count) {
    // Distinct color palette for income categories - mix of greens, blues, and positive colors
    const incomeColors = [
        '#4CAF50', // Green - Primary income color
        '#2196F3', // Blue - Secondary income
        '#00BCD4', // Cyan - Freelance/side income
        '#8BC34A', // Light green - Business income
        '#3F51B5', // Indigo - Investment income
        '#009688', // Teal - Gift/bonus
        '#4FC3F7', // Light blue - Other income
        '#66BB6A', // Medium green
        '#42A5F5', // Medium blue
        '#26C6DA', // Light cyan
        '#7986CB', // Light indigo
        '#4DB6AC'  // Medium teal
    ];
    
    return incomeColors.slice(0, count);
}

function generateExpenseColors(count) {
    // Distinct color palette for expense categories - mix of reds, oranges, and warm colors
    const expenseColors = [
        '#f44336', // Red - Primary expense color
        '#FF9800', // Orange - Food & dining
        '#E91E63', // Pink - Shopping
        '#9C27B0', // Purple - Entertainment
        '#FF5722', // Deep orange - Transportation
        '#795548', // Brown - Bills & utilities
        '#607D8B', // Blue grey - Healthcare
        '#FFC107', // Amber - Education
        '#FF6F00', // Orange accent - Travel
        '#8E24AA', // Purple accent - Insurance
        '#D32F2F', // Dark red - Other expenses
        '#F57C00'  // Orange darken - Miscellaneous
    ];
    
    return expenseColors.slice(0, count);
}

function showLoading(show) {
    if (show) {
        loadingDiv.classList.remove('hidden');
    } else {
        loadingDiv.classList.add('hidden');
    }
}

function showToast(message, type) {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Pagination functions
function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderTransactions();
    }
}

function updatePagination() {
    const dataToRender = filteredTransactions.length > 0 || dateFilter.startDate || dateFilter.endDate 
        ? filteredTransactions 
        : transactions;
    
    totalPages = Math.ceil(dataToRender.length / itemsPerPage);
    if (currentPage > totalPages) {
        currentPage = Math.max(1, totalPages);
    }
}

function updatePaginationInfo(start, end, total) {
    const paginationInfo = document.getElementById('pagination-info-text');
    if (total === 0) {
        paginationInfo.textContent = 'No transactions to display';
    } else {
        paginationInfo.textContent = `Showing ${start}-${end} of ${total} transactions`;
    }
}

function updatePaginationControls() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageNumbers = document.getElementById('page-numbers');
    
    // Update button states
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    
    // Generate page numbers
    pageNumbers.innerHTML = '';
    
    if (totalPages <= 1) {
        return;
    }
    
    // Show page numbers (max 5 pages visible)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('span');
        pageBtn.className = `page-number ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.addEventListener('click', () => changePage(i));
        pageNumbers.appendChild(pageBtn);
    }
}

async function downloadFilteredTransactions() {
    /**
     * Download the currently filtered transactions as an Excel file
     * Uses the same date filters that are applied to the transaction table
     */
    try {
        const downloadBtn = document.getElementById('download-transactions-btn');
        
        // Disable button and show loading state
        downloadBtn.disabled = true;
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Downloading...</span>';
        
        // Prepare filter data - use current date filter state
        const filterData = {
            start_date: dateFilter.startDate,
            end_date: dateFilter.endDate
        };
        
        // Make request to download endpoint
        const response = await fetch('/api/transactions/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }
        
        // Get the filename from the response headers or create a default one
        let filename = 'transactions.xlsx';
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }
        
        // Create blob from response and trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary link element to trigger download
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Show success message
        let downloadMessage = 'Transactions downloaded successfully!';
        if (dateFilter.startDate || dateFilter.endDate) {
            downloadMessage = 'Filtered transactions downloaded successfully!';
        }
        showToast(downloadMessage, 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showToast(error.message || 'Failed to download transactions', 'error');
    } finally {
        // Re-enable button and restore original text
        const downloadBtn = document.getElementById('download-transactions-btn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download"></i><span>Download Excel</span>';
    }
}
