import json
import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_by_id(user_id):
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['id'] == user_id:
                return User(
                    id=user['id'],
                    username=user['username'],
                    password_hash=user['password'],
                    is_admin=user.get('is_admin', False)
                )
        return None
    
    @staticmethod
    def get_by_username(username):
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['username'] == username:
                return User(
                    id=user['id'],
                    username=user['username'],
                    password_hash=user['password'],
                    is_admin=user.get('is_admin', False)
                )
        return None
    
    @staticmethod
    def register(username, password, is_admin=False):
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        # Check if username already exists
        for user in users:
            if user['username'] == username:
                return False
        
        # Create new user
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': generate_password_hash(password),
            'is_admin': is_admin
        }
        
        users.append(new_user)
        
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
        
        return True

class Fund:
    @staticmethod
    def add_entry(name, amount, date, method):
        with open('funds.json', 'r') as f:
            funds = json.load(f)
        
        new_entry = {
            'id': len(funds) + 1,
            'name': name,
            'amount': float(amount),
            'date': date,
            'method': method
        }
        
        funds.append(new_entry)
        
        with open('funds.json', 'w') as f:
            json.dump(funds, f, indent=4)
        
        return True
    
    @staticmethod
    def get_all():
        with open('funds.json', 'r') as f:
            funds = json.load(f)
        
        # Sort by date (most recent first)
        funds.sort(key=lambda x: x['date'], reverse=True)
        
        return funds
    
    @staticmethod
    def get_total():
        with open('funds.json', 'r') as f:
            funds = json.load(f)
        
        total = sum(entry['amount'] for entry in funds)
        return total

class Expense:
    @staticmethod
    def add_entry(title, amount, date, reason):
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
        
        new_entry = {
            'id': len(expenses) + 1,
            'title': title,
            'amount': float(amount),
            'date': date,
            'reason': reason
        }
        
        expenses.append(new_entry)
        
        with open('expenses.json', 'w') as f:
            json.dump(expenses, f, indent=4)
        
        return True
    
    @staticmethod
    def get_all():
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
        
        # Sort by date (most recent first)
        expenses.sort(key=lambda x: x['date'], reverse=True)
        
        return expenses
    
    @staticmethod
    def get_total():
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
        
        total = sum(entry['amount'] for entry in expenses)
        return total

class FundSubmission:
    @staticmethod
    def initialize_file():
        if not os.path.exists('fund_submissions.json'):
            with open('fund_submissions.json', 'w') as f:
                json.dump([], f)
    
    @staticmethod
    def add_submission(full_name, mobile_number, amount, transaction_id, payment_method, screenshot_filename=None):
        FundSubmission.initialize_file()
        
        with open('fund_submissions.json', 'r') as f:
            submissions = json.load(f)
        
        new_submission = {
            'id': len(submissions) + 1,
            'full_name': full_name,
            'mobile_number': mobile_number,
            'amount': float(amount),
            'transaction_id': transaction_id,
            'payment_method': payment_method,
            'screenshot': screenshot_filename,
            'date_submitted': datetime.now().strftime('%Y-%m-%d'),
            'status': 'pending'  # pending, approved, rejected
        }
        
        submissions.append(new_submission)
        
        with open('fund_submissions.json', 'w') as f:
            json.dump(submissions, f, indent=4)
        
        return True
    
    @staticmethod
    def get_all():
        FundSubmission.initialize_file()
        
        with open('fund_submissions.json', 'r') as f:
            submissions = json.load(f)
        
        # Sort by date (most recent first)
        submissions.sort(key=lambda x: x['date_submitted'], reverse=True)
        
        return submissions
    
    @staticmethod
    def get_pending_submissions():
        FundSubmission.initialize_file()
        
        with open('fund_submissions.json', 'r') as f:
            submissions = json.load(f)
        
        # Filter pending submissions and sort by date (most recent first)
        pending = [s for s in submissions if s['status'] == 'pending']
        pending.sort(key=lambda x: x['date_submitted'], reverse=True)
        
        return pending
    
    @staticmethod
    def approve_submission(submission_id):
        FundSubmission.initialize_file()
        
        with open('fund_submissions.json', 'r') as f:
            submissions = json.load(f)
        
        for submission in submissions:
            if submission['id'] == submission_id:
                submission['status'] = 'approved'
                
                # Add to funds
                Fund.add_entry(
                    name=submission['full_name'],
                    amount=submission['amount'],
                    date=submission['date_submitted'],
                    method=submission['payment_method']
                )
                
                with open('fund_submissions.json', 'w') as f:
                    json.dump(submissions, f, indent=4)
                
                return True
        
        return False
    
    @staticmethod
    def reject_submission(submission_id):
        FundSubmission.initialize_file()
        
        with open('fund_submissions.json', 'r') as f:
            submissions = json.load(f)
        
        for submission in submissions:
            if submission['id'] == submission_id:
                submission['status'] = 'rejected'
                
                with open('fund_submissions.json', 'w') as f:
                    json.dump(submissions, f, indent=4)
                
                return True
        
        return False