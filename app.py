from flask import Flask, render_template, request, jsonify
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__, template_folder='.')
DATA_FILE = 'reminders.txt'

# ==========================================
# 🔐 YOUR MAILTRAP CREDENTIALS INSTALLED 🔐
# ==========================================
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
                # Safely inspect lines that contain Email, Amount, and Due Date layout structures
                if "Client:" in line and "Amount:" in line and "Due:" in line:
                    parts = line.strip().split(' | ')
                    if len(parts) == 3:
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
    due_date = data.get('date')
    
    # Save the 3 data values permanently to our text database document file
    with open(DATA_FILE, 'a') as f:
        f.write(f"Client: {client_email} | Amount: ${amount_owed} | Due: {due_date}\n")
        
    # Build the automated transactional invoice message content body
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

    # Open network connection stream and dispatch live over the web grid array
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PWD)
            server.sendmail('billing@freelanceshield.com', [client_email], msg.as_string())
        
        return jsonify({
            "status": "success",
            "message": f"Tracked successfully! Email deadline set for {due_date}."
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Network error: Could not transmit email."
        })

@app.route('/clear-history', methods=['POST'])
def clear_history():
    if os.path.exists(DATA_FILE):
        open(DATA_FILE, 'w').close() 
    return jsonify({"status": "success", "message": "Database completely cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
