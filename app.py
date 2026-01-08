from flask import Flask, render_template, request, jsonify, redirect, url_for
from automation import AttendanceBot
from datetime import datetime
import threading
import uuid
import time
#updated 9:03
app = Flask(__name__)

# Simple in-memory job store (not persistent, but fine for this single-user app)
# Format: { job_id: { 'status': 'running'|'done'|'error', 'data': result_list, 'date': date_str } }
JOBS = {}

def bg_check_attendance(job_id, target_date, prn, dob, semester):
    """Runs in a background thread."""
    try:
        bot = AttendanceBot(prn, dob, semester)
        results = bot.get_attendance(target_date)
        JOBS[job_id]['data'] = results
        JOBS[job_id]['status'] = 'done'
    except Exception as e:
        JOBS[job_id]['status'] = 'error'
        JOBS[job_id]['error'] = str(e)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    today = datetime.now().strftime("%d-%m-%Y")
    # Convert to YYYY-MM-DD for input
    try:
        dt = datetime.strptime(today, "%d-%m-%Y")
        today_iso = dt.strftime("%Y-%m-%d")
    except:
        today_iso = ""
    return render_template('index.html', default_date_iso=today_iso)

@app.route('/start_check', methods=['POST'])
def start_check():
    data = request.json
    target_date = data.get('date')
    prn = data.get('prn')
    password = data.get('password')
    semester = data.get('semester', 'odd') # Default to odd

    if not target_date:
        target_date = datetime.now().strftime("%d-%m-%Y")
    
    # Defaults
    if not prn: prn = "24UCS056"
    
    # Password handling (expecting date format YYYY-MM-DD from HTML input)
    dob = "10-08-2006" # Default
    if password:
        try:
            # Convert YYYY-MM-DD to DD-MM-YYYY
            dt = datetime.strptime(password, "%Y-%m-%d")
            dob = dt.strftime("%d-%m-%Y")
        except:
             # If user typed something custom, pass as is
             dob = password

    # Format conversion for target_date
    if "-" in target_date:
        try:
            # Try parsing standard input format YYYY-MM-DD
            dt = datetime.strptime(target_date, "%Y-%m-%d")
            target_date = dt.strftime("%d-%m-%Y")
        except ValueError:
            pass 

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {'status': 'running', 'date': target_date}
    
    # Start thread
    thread = threading.Thread(target=bg_check_attendance, args=(job_id, target_date, prn, dob, semester))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>')
def job_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({'status': 'not_found'}), 404
    return jsonify({'status': job['status']})

@app.route('/result/<job_id>')
def show_result(job_id):
    job = JOBS.get(job_id)
    if not job or job['status'] != 'done':
        return redirect(url_for('index'))
    
    results = job['data']
    target_date = job['date']
    
    # Calculate stats
    present_count = sum(1 for r in results if "Present" in r['status'])
    absent_count = sum(1 for r in results if "Absent" in r['status'])
    
    return render_template('result.html', results=results, date=target_date, present=present_count, absent=absent_count)

if __name__ == '__main__':
    # Port 5001 to avoid AirPlay conflict
    app.run(debug=True, host='0.0.0.0', port=5001)
