from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# Simulating database storage in memory for keys and users
users_db = {"admin": "admin"}
balances_db = {"admin": 999999}
expire_times_db = {"admin": time.time() + (30 * 24 * 60 * 60)}
keys_db = {"admin": []}

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def index_page():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if username in users_db and users_db[username] == password:
        return jsonify({"status": True, "message": "Login successful"})
    return jsonify({"status": False, "message": "Invalid Username or Password!"})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if username and password:
        if username in users_db:
            return jsonify({"status": False, "message": "User already exists!"})
        users_db[username] = password
        balances_db[username] = 999999
        expire_times_db[username] = time.time() + (30 * 24 * 60 * 60)
        keys_db[username] = []
        return jsonify({"status": True, "message": "Registered successfully!"})
    return jsonify({"status": False, "message": "Please fill all fields!"})

@app.route('/connect', methods=['GET', 'POST'])
def connect_api():
    user_key = request.args.get('user_key') or request.form.get('user_key', '')
    
    isValidKey = False
    for user, keys in keys_db.items():
        for k in keys:
            if k['key'] == user_key:
                isValidKey = True
                break
        if isValidKey:
            break
            
    if isValidKey or user_key == "VIP-TEST-KEY":
        return jsonify({
            "status": True,
            "data": {
                "token": "Vm8Lk7Uj2JmsjCPVPVjrLa7zgfx3uz9E",
                "rng": int(time.time())
            }
        })
    else:
        return jsonify({
            "status": False,
            "reason": "Invalid or Expired Key!"
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
