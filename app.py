# app.py (diagnostic version)
from flask import Flask, render_template, request, redirect, url_for, session
import traceback
import sys

app = Flask(__name__)
app.secret_key = 'secret123'  # required for using session

# Track votes
votes = {"Mahendra Singh Dhoni": 0, "Virat Kohli": 0, "Rohit Sharma": 0}

# Track voters who already voted
voted_users = set()

def log(msg):
    print(msg, file=sys.stderr)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')  # may be empty for voters

            log(f"[LOGIN ATTEMPT] username='{username}' password_provided={'yes' if password else 'no'}")

            # Admin login
            if username == 'admin' and password == '1234':
                session['user'] = 'admin'
                log("[LOGIN] Admin logged in")
                return redirect(url_for('results'))

            # Voter login (no password)
            elif username != '':
                if username in voted_users:
                    log(f"[LOGIN] Voter '{username}' already voted")
                    return render_template('message.html', msg="You have already voted!")
                else:
                    session['user'] = username
                    log(f"[LOGIN] Voter '{username}' logged in")
                    return redirect(url_for('vote'))
            else:
                log("[LOGIN] Empty username submitted")
                return render_template('message.html', msg="Please enter your name!")
        return render_template('login.html')
    except Exception as e:
        tb = traceback.format_exc()
        log("[ERROR in /login]\n" + tb)
        return render_template('message.html', msg="Server error occurred. See console for details.")

@app.route('/vote')
def vote():
    try:
        if 'user' not in session or session['user'] == 'admin':
            log("[VOTE] Access denied: no voter logged in or admin tried to access vote page")
            return redirect(url_for('login'))
        return render_template('vote.html')
    except Exception:
        tb = traceback.format_exc()
        log("[ERROR in /vote]\n" + tb)
        return render_template('message.html', msg="Server error occurred. See console for details.")

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    try:
        if 'user' not in session or session['user'] == 'admin':
            log("[SUBMIT_VOTE] Access denied: no voter logged in or admin trying to submit")
            return redirect(url_for('login'))

        # Safely get candidate from form
        candidate = request.form.get('candidate')
        log(f"[SUBMIT_VOTE] user='{session.get('user')}' candidate='{candidate}'")

        if not candidate:
            log("[SUBMIT_VOTE] No candidate selected in form")
            return render_template('message.html', msg="No candidate selected.")

        if candidate not in votes:
            log(f"[SUBMIT_VOTE] Invalid candidate: {candidate}")
            return render_template('message.html', msg="Invalid candidate selected.")

        votes[candidate] += 1
        voted_users.add(session['user'])
        log(f"[SUBMIT_VOTE] Vote recorded for {candidate} by {session['user']}")
        return render_template('message.html', msg="Vote submitted successfully!")
    except Exception:
        tb = traceback.format_exc()
        log("[ERROR in /submit_vote]\n" + tb)
        return render_template('message.html', msg="Server error occurred. See console for details.")

@app.route('/results')
def results():
    try:
        if 'user' not in session:
            log("[RESULTS] Access denied: not logged in")
            return redirect(url_for('login'))
        if session['user'] != 'admin':
            log(f"[RESULTS] Access denied for user: {session.get('user')}")
            return render_template('message.html', msg="Access Denied: Admins only.")
        return render_template('results.html', votes=votes)
    except Exception:
        tb = traceback.format_exc()
        log("[ERROR in /results]\n" + tb)
        return render_template('message.html', msg="Server error occurred. See console for details.")

@app.route('/logout')
def logout():
    user = session.get('user')
    session.clear()
    log(f"[LOGOUT] user '{user}' logged out")
    return redirect(url_for('home'))

if __name__ == '__main__':
    log("Starting Flask app (diagnostic mode). Open http://127.0.0.1:5000/login")
    app.run(debug=True)
