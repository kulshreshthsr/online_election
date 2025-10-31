from flask import Flask, render_template, request, redirect, url_for, session, flash
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "secretkey123"  # Needed for sessions

# ---- Configuration ----
ADMIN_USER = "Kulshreshtha"
ADMIN_PASS = "JAGRAN"
CANDIDATES = ["Kulshreshtha Srivas", "Prakhar Mishra", "Dhruv Tiwari", "Harshit Agnihotri"]

# ---- Data storage ----
votes = defaultdict(int)
voters = set()  # store names who have already voted


# ---- Home page ----
@app.route('/')
def index():
    return render_template('index.html')


# ---- Admin login ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            flash("Admin login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# ---- Admin home ----
@app.route('/home')
def home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


# ---- Voting page ----
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == "POST":
        name = request.form.get("name").strip().lower()
        age = request.form.get("age")
        candidate = request.form.get("candidate")

        if not name or not age or not candidate:
            flash("All fields are required!", "warning")
            return redirect(url_for('vote'))

        if name in voters:
            return render_template('message.html', message="❌ You have already voted!")

        # Register the vote
        voters.add(name)
        votes[candidate] += 1

        return render_template('message.html', message="✅ Your vote has been recorded successfully!")

    return render_template('vote.html', candidates=CANDIDATES)


# ---- Results page ----
@app.route('/results')
def results():
    if 'admin' not in session:
        flash("You must be logged in as admin to view results!", "warning")
        return redirect(url_for('login'))

    return render_template('results.html', votes=votes)


# ---- Logout ----
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


# ---- Run ----
if __name__ == "__main__":
    app.run(debug=True)
