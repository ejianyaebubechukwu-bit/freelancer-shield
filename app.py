from flask import Flask, render_template, request, jsonify
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__, template_folder='.')
DATA_FILE = 'reminders.txt'

SMTP_SERVER = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 2525
SMTP_USER = "c51886067070c2"
SMTP_PWD = "e5df6720b5a360"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-history', methods=['GET'])
def get_history():
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            for line in f:
                if "Client:" in line and "Amount:" in line and "Due:" in line:
                    # Parse out email, amount, and the calendar deadline info safely
                    parts = line.strip().split(' | ')
                    email = parts[0].replace('Client: ', '')
                    amount = parts[1].replace('Amount: $', '')
                    due_date = parts[2].replace('Due: ', '')
                    history.append({'email': email, 'amount': amount, 'date': due_date})
    return jsonify(history)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    client_email = data.get('email')
    amount_owed = data.get('amount')
    due_date = data.get('date') # <-- NEW: Extract calendar date variable
    
    # 1. Save data permanently (now including deadline field)
    with open(DATA_FILE, 'a') as f:
        f.write(f"Client: {client_email} | Amount: ${amount_owed} | Due: {due_date}\n")
        
    # 2. Add deadline info right into the email body text!
    email_body = f"""
    Dear Client,
    
    This is an automated reminder from Freelance Shield that you have an outstanding 
    balance of ${float(amount_owed):,.2f} due for creative services rendered.
    
    CRITICAL DEADLINE: Please remit payment on or before {due_date}.
    
    Best regards,
    Freelance Shield Automated Agent
    """
    
    msg = MIMEText(email_body)
    msg['Subject'] = f'Urgent: Payment Due by {due_date}'
    msg['From'] = 'billing@freelanceshield.com'
    msg['To'] = client_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PWD)
            server.sendmail('billing@freelanceshield.com', [client_email], msg.as_string())
        
        print(f"\n🚀 [SUCCESS] Email dispatched with due date {due_date} to {client_email}")
        return jsonify({
            "status": "success",
            "message": f"Tracked successfully! Email deadline set for {due_date}."
        })
        
    except Exception as e:
        print(f"\n❌ [NETWORK ERROR] Failed: {e}")
        return jsonify({"status": "error", "message": "Network error transmitting email."})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    if os.path.exists(DATA_FILE):
        open(DATA_FILE, 'w').close() 
    return jsonify({"status": "success", "message": "Database completely cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
