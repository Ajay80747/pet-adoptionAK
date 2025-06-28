from flask import Flask, request, redirect, jsonify, session, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pet_adoption"]
pets_collection = db.pets
donors_collection = db.donors
volunteers_collection = db.volunteers
users_collection = db.users
endangered_collection = db.endangered

# Seed data
if pets_collection.count_documents({}) == 0:
    pets_collection.insert_many([
        {"name": "Simba", "species": "Cat", "breed": "Siamese", "age": 3, "adopter": "Aarti"},
        {"name": "Tommy", "species": "Dog", "breed": "Beagle", "age": 4, "adopter": "Meena"}
    ])

if donors_collection.count_documents({}) == 0:
    donors_collection.insert_many([
        {"name": "John Doe", "amount": 1000},
        {"name": "Vikas", "amount": 300}
    ])

if endangered_collection.count_documents({}) == 0:
    endangered_collection.insert_many([
        {"name": "Amur Leopard", "continent": "Asia", "status": "Critically Endangered", "fact": "Fewer than 100 remain in the wild."},
        {"name": "Black Rhino", "continent": "Africa", "status": "Critically Endangered", "fact": "Hunted for horns."}
    ])

# ROUTES

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/adopt', methods=['GET', 'POST'])
def adopt():
    if request.method == 'POST':
        pet_data = {
            "name": request.form['name'],
            "species": request.form['species'],
            "breed": request.form['breed'],
            "age": request.form['age'],
            "adopter": request.form['adopter']
        }
        pets_collection.insert_one(pet_data)
        return redirect('/thankyou')
    return send_from_directory('.', 'adopt.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donors_collection.insert_one({
            "name": request.form['name'],
            "amount": int(request.form['amount'])
        })
        return redirect('/thankyou')
    return send_from_directory('.', 'donate.html')

@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == 'POST':
        volunteers_collection.insert_one({
            "name": request.form['name'],
            "email": request.form['email'],
            "phone": request.form['phone']
        })
        return redirect('/thankyou')
    return send_from_directory('.', 'volunteer.html')

@app.route('/loginpage')
def loginpage():
    return send_from_directory('.', 'login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({'email': data['email']})
    if user:
        if check_password_hash(user['password'], data['password']):
            session['user'] = user['email']
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Incorrect password"})
    else:
        hashed_password = generate_password_hash(data['password'])
        users_collection.insert_one({
            'email': data['email'],
            'password': hashed_password
        })
        session['user'] = data['email']
        return jsonify({"success": True, "new_user": True})

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"<h2>Welcome {session['user']}!</h2> <a href='/logout'>Logout</a>"
    return redirect('/loginpage')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/endangered')
def endangered():
    return send_from_directory('.', 'endangered.html')

@app.route('/thankyou')
def thankyou():
    return send_from_directory('.', 'thankyou.html')

# static file serving for JS/CSS/image fallback
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
