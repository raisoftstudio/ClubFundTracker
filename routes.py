from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Fund, Expense, FundSubmission
from forms import RegisterForm, LoginForm, FundForm, ExpenseForm, FundSubmissionForm
from datetime import datetime
import io
import csv
from flask import Response
import os
import uuid
from werkzeug.utils import secure_filename

# Helper function to save uploaded screenshot
def save_screenshot(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Generate a unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join('static/uploads', unique_filename)
        file.save(file_path)
        return unique_filename
    return None

@app.route('/')
def home():
    funds = Fund.get_all()
    expenses = Expense.get_all()
    total_funds = Fund.get_total()
    total_expenses = Expense.get_total()
    current_balance = total_funds - total_expenses
    
    return render_template(
        'home.html', 
        funds=funds[:5],  # Show only latest 5 entries
        expenses=expenses[:5],  # Show only latest 5 entries
        total_funds=total_funds,
        total_expenses=total_expenses,
        current_balance=current_balance
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Register user
        if User.register(username, password):
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('home'))
    
    funds = Fund.get_all()
    expenses = Expense.get_all()
    total_funds = Fund.get_total()
    total_expenses = Expense.get_total()
    current_balance = total_funds - total_expenses
    pending_submissions = FundSubmission.get_pending_submissions()
    
    fund_form = FundForm()
    expense_form = ExpenseForm()
    
    return render_template(
        'dashboard.html',
        fund_form=fund_form,
        expense_form=expense_form,
        funds=funds[:5],
        expenses=expenses[:5],
        total_funds=total_funds,
        total_expenses=total_expenses,
        current_balance=current_balance,
        pending_submissions=pending_submissions
    )

@app.route('/funds', methods=['GET', 'POST'])
@login_required
def funds():
    form = FundForm()
    
    if form.validate_on_submit():
        if not current_user.is_admin:
            flash('You do not have permission to add funds.', 'danger')
            return redirect(url_for('funds'))
        
        name = form.name.data
        amount = form.amount.data
        
        # Format date properly
        if form.date.data:
            date = form.date.data.strftime('%Y-%m-%d')
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            
        method = form.method.data
        
        Fund.add_entry(name, amount, date, method)
        flash('Fund entry added successfully!', 'success')
        return redirect(url_for('funds'))
    
    funds = Fund.get_all()
    total_funds = Fund.get_total()
    
    return render_template('funds.html', funds=funds, total=total_funds, form=form)

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    
    if form.validate_on_submit():
        if not current_user.is_admin:
            flash('You do not have permission to add expenses.', 'danger')
            return redirect(url_for('expenses'))
        
        title = form.title.data
        amount = form.amount.data
        
        # Format date properly
        if form.date.data:
            date = form.date.data.strftime('%Y-%m-%d')
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            
        reason = form.reason.data
        
        Expense.add_entry(title, amount, date, reason)
        flash('Expense entry added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    expenses = Expense.get_all()
    total_expenses = Expense.get_total()
    
    return render_template('expenses.html', expenses=expenses, total=total_expenses, form=form)

@app.route('/summary')
def summary():
    funds = Fund.get_all()
    expenses = Expense.get_all()
    total_funds = Fund.get_total()
    total_expenses = Expense.get_total()
    current_balance = total_funds - total_expenses
    
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
    
    return render_template(
        'summary.html',
        funds=funds,
        expenses=expenses,
        total_funds=total_funds,
        total_expenses=total_expenses,
        current_balance=current_balance,
        monthly_summary=monthly_summary
    )

@app.route('/export/funds')
@login_required
def export_funds():
    if not current_user.is_admin:
        flash('You do not have permission to export data.', 'danger')
        return redirect(url_for('funds'))
    
    funds = Fund.get_all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Amount', 'Date', 'Method'])
    
    for fund in funds:
        writer.writerow([fund['id'], fund['name'], fund['amount'], fund['date'], fund['method']])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=funds.csv'}
    )

@app.route('/export/expenses')
@login_required
def export_expenses():
    if not current_user.is_admin:
        flash('You do not have permission to export data.', 'danger')
        return redirect(url_for('expenses'))
    
    expenses = Expense.get_all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Amount', 'Date', 'Reason'])
    
    for expense in expenses:
        writer.writerow([expense['id'], expense['title'], expense['amount'], expense['date'], expense['reason']])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=expenses.csv'}
    )

@app.route('/submit_fund', methods=['GET', 'POST'])
def submit_fund():
    form = FundSubmissionForm()
    
    if form.validate_on_submit():
        # Save screenshot if provided
        screenshot_filename = None
        if form.screenshot.data:
            screenshot_filename = save_screenshot(form.screenshot.data)
            
        # Add submission to database
        FundSubmission.add_submission(
            full_name=form.full_name.data,
            mobile_number=form.mobile_number.data,
            amount=form.amount.data,
            transaction_id=form.transaction_id.data,
            payment_method=form.payment_method.data,
            screenshot_filename=screenshot_filename
        )
        
        flash('Your fund submission has been received and is pending approval.', 'success')
        return redirect(url_for('home'))
    
    return render_template('submit_fund.html', form=form)

@app.route('/approve_submission/<int:submission_id>')
@login_required
def approve_submission(submission_id):
    if not current_user.is_admin:
        flash('You do not have permission to approve fund submissions.', 'danger')
        return redirect(url_for('home'))
    
    if FundSubmission.approve_submission(submission_id):
        flash('Fund submission approved and added to funds.', 'success')
    else:
        flash('Could not find the submission or it was already processed.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/reject_submission/<int:submission_id>')
@login_required
def reject_submission(submission_id):
    if not current_user.is_admin:
        flash('You do not have permission to reject fund submissions.', 'danger')
        return redirect(url_for('home'))
    
    if FundSubmission.reject_submission(submission_id):
        flash('Fund submission rejected.', 'warning')
    else:
        flash('Could not find the submission or it was already processed.', 'danger')
    
    return redirect(url_for('dashboard'))
