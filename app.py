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

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

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
        balances_db[username] = 2000  # নতুন ইউজারের রেজিস্টার ব্যালেন্স 2k
        expire_times_db[username] = time.time() + (30 * 24 * 60 * 60)
        keys_db[username] = []
        return jsonify({"status": True, "message": "Registered successfully!"})
    return jsonify({"status": False, "message": "Please fill all fields!"})

@app.route('/api/generate_key', methods=['POST'])
def api_generate_key():
    data = request.form
    username = data.get('username', 'admin').strip()
    key = data.get('key', '').strip()
    duration = data.get('duration', '').strip()
    
    if username not in users_db:
        return jsonify({"status": False, "message": "User not found!"})
        
    # খরচ ক্যালকুলেট করা (Duration অনুযায়ী)
    cost = 10
    expire_seconds = 7 * 24 * 60 * 60  
    if "2 Hours" in duration:
        cost = 10
        expire_seconds = 2 * 60 * 60
    elif "1 Days" in duration:
        cost = 80
        expire_seconds = 24 * 60 * 60
    elif "7 Days" in duration:
        cost = 200
        expire_seconds = 7 * 24 * 60 * 60
        
    # ব্যালেন্স চেক করা
    current_balance = balances_db.get(username, 0)
    if current_balance < cost:
        return jsonify({"status": False, "message": "Insufficient balance to generate key!"})
        
    # ব্যালেন্স কাটা হচ্ছে
    balances_db[username] = current_balance - cost
    
    if username not in keys_db:
        keys_db[username] = []
        
    if key:
        expire_timestamp = time.time() + expire_seconds
        keys_db[username].append({
            'key': key, 
            'duration': duration, 
            'status': 'Un-used',
            'expire_time': expire_timestamp
        })
        return jsonify({"status": True, "message": "Key saved successfully! Balance deducted."})
        
    return jsonify({"status": False, "message": "Invalid key data!"})

@app.route('/api/get_keys', methods=['POST'])
def api_get_keys():
    username = request.form.get('username', 'admin').strip()
    user_keys = keys_db.get(username, [])
    user_balance = balances_db.get(username, 0)
    return jsonify({"status": True, "keys": user_keys, "balance": user_balance})

# এডমিনের জন্য সকল ইউজারের ডাটা দেখার রুট
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    all_users = []
    for user in users_db:
        all_users.append({
            "username": user,
            "balance": balances_db.get(user, 0),
            "keys_count": len(keys_db.get(user, []))
        })
    return jsonify({"status": True, "users": all_users})

# এডমিন কর্তৃক ইউজার রিমুভ করার রুট
@app.route('/api/admin/remove_user', methods=['POST'])
def admin_remove_user():
    username = request.form.get('username', '').strip()
    if username == "admin":
        return jsonify({"status": False, "message": "Cannot delete main admin!"})
    
    if username in users_db:
        users_db.pop(username, None)
        balances_db.pop(username, None)
        expire_times_db.pop(username, None)
        keys_db.pop(username, None)
        return jsonify({"status": True, "message": "User removed successfully!"})
    return jsonify({"status": False, "message": "User not found!"})

# এডমিন কর্তৃক ব্যালেন্স এড বা রিমুভ করার রুট
@app.route('/api/admin/update_balance', methods=['POST'])
def admin_update_balance():
    data = request.form
    username = data.get('username', '').strip()
    amount = int(data.get('amount', 0))
    action = data.get('action', 'add').strip() # 'add' অথবা 'remove'
    
    if username in balances_db:
        if action == 'add':
            balances_db[username] += amount
        elif action == 'remove':
            balances_db[username] = max(0, balances_db[username] - amount)
        return jsonify({"status": True, "message": "Balance updated successfully!", "new_balance": balances_db[username]})
    return jsonify({"status": False, "message": "User not found!"})

@app.route('/updateaccount', methods=['POST'])
def update_account():
    data = request.form
    old_username = data.get('old_username', '').strip()
    new_username = data.get('new_username', '').strip()
    new_password = data.get('new_password', '').strip()

    if old_username and new_username and old_username != new_username:
        if old_username not in users_db:
            return jsonify({"status": False, "message": "Original user not found!"})
        if new_username in users_db:
            return jsonify({"status": False, "message": "New username already taken!"})
        
        users_db[new_username] = users_db.pop(old_username)
        balances_db[new_username] = balances_db.pop(old_username, 2000)
        expire_times_db[new_username] = expire_times_db.pop(old_username, time.time() + (30 * 24 * 60 * 60))
        keys_db[new_username] = keys_db.pop(old_username, [])
        
        if new_password:
            users_db[new_username] = new_password
            
        return jsonify({"status": True, "message": "Username and account updated successfully!"})

    target_user = new_username if new_username else old_username
    if target_user and new_password:
        if target_user not in users_db:
            return jsonify({"status": False, "message": "User not found!"})
        users_db[target_user] = new_password
        return jsonify({"status": True, "message": "Password updated successfully!"})

    return jsonify({"status": False, "message": "No changes provided!"})

@app.route('/connect', methods=['GET', 'POST'])
def connect_api():
    user_key = request.args.get('user_key') or request.form.get('user_key', '')
    
    found_key = None
    for user, keys in keys_db.items():
        for k in keys:
            if k['key'] == user_key:
                found_key = k
                break
        if found_key:
            break
            
    if user_key == "VIP-TEST-KEY":
        return jsonify({
            "status": True,
            "data": {
                "token": "Vm8Lk7Uj2JmsjCPVPVjrLa7zgfx3uz9E",
                "rng": int(time.time()),
                "expiry": int(time.time() + 86400)
            }
        })
        
    if found_key:
        current_time = time.time()
        if current_time > found_key.get('expire_time', current_time + 1000):
            return jsonify({
                "status": False,
                "reason": "Key has expired!"
            })
            
        return jsonify({
            "status": True,
            "data": {
                "token": "Vm8Lk7Uj2JmsjCPVPVjrLa7zgfx3uz9E",
                "rng": int(time.time()),
                "expiry": int(found_key['expire_time'])
            }
        })
    else:
        return jsonify({
            "status": False,
            "reason": "Invalid or Expired Key!"
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
