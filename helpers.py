import json
from datetime import datetime

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def format_currency(amount):
    return f"৳{amount:,.2f}"

def get_balance():
    with open('funds.json', 'r') as f:
        funds = json.load(f)
    
    with open('expenses.json', 'r') as f:
        expenses = json.load(f)
    
    total_funds = sum(entry['amount'] for entry in funds)
    total_expenses = sum(entry['amount'] for entry in expenses)
    
    return total_funds - total_expenses

def get_monthly_summary():
    with open('funds.json', 'r') as f:
        funds = json.load(f)
    
    with open('expenses.json', 'r') as f:
        expenses = json.load(f)
    
    # Group funds by month
    funds_by_month = {}
    for fund in funds:
        month_year = datetime.strptime(fund['date'], '%Y-%m-%d').strftime('%B %Y')
        if month_year not in funds_by_month:
            funds_by_month[month_year] = 0
        funds_by_month[month_year] += fund['amount']
    
    # Group expenses by month
    expenses_by_month = {}
    for expense in expenses:
        month_year = datetime.strptime(expense['date'], '%Y-%m-%d').strftime('%B %Y')
        if month_year not in expenses_by_month:
            expenses_by_month[month_year] = 0
        expenses_by_month[month_year] += expense['amount']
    
    # Get all unique months
    all_months = sorted(list(set(list(funds_by_month.keys()) + list(expenses_by_month.keys()))), 
                        key=lambda x: datetime.strptime(x, '%B %Y'), reverse=True)
    
    monthly_summary = []
    for month in all_months:
        funds_amount = funds_by_month.get(month, 0)
        expenses_amount = expenses_by_month.get(month, 0)
        balance = funds_amount - expenses_amount
        monthly_summary.append({
            'month': month,
            'funds': funds_amount,
            'expenses': expenses_amount,
            'balance': balance
        })
    
    return monthly_summary
