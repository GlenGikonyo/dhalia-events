from flask import Flask, render_template,url_for,redirect,request,jsonify,session,flash
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

from datetime import timedelta

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = False


app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

# MongoDB connection string
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client['dhalia']
collection = db['ContactForm']

# Acces for Login collection access
login_collection= db['login']

# Set the directory containing HTML files
HTML_DIR = "templates"

available_pages = {f.split('.')[0]: f for f in os.listdir(HTML_DIR) if f.endswith('.html')}
print(available_pages)

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/<page>')
def serve_page(page):
    if page in available_pages:
        return render_template(available_pages[page])
    return render_template("404.html"), 404 

@app.route('/book-now')
def book_now():
    phone_number = "254790815636"
    message = "Hello, I would like to book an event with Dhalia Events Limited. Please provide me with more details."
    
    whatsapp_url = f"https://wa.me/{phone_number}?text={message.replace(' ', '%20')}"
    print (whatsapp_url)
    
    return redirect(whatsapp_url)



@app.route('/contact-us', methods=['GET', 'POST'])
def render_contact_us():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        msg_subject = request.form.get('msg_subject')
        message = request.form.get('message')
        status = "New"

        try:
            # Insert form data into MongoDB
            form_data = {
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "msg_subject": msg_subject,
                "message": message,
                "status":status,
                "created_at": datetime.now()
            }

            result = collection.insert_one(form_data)
            print(f"Data inserted with ID: {result.inserted_id}")

            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": True})
            
            # For non-AJAX requests, redirect with flash message
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('render_contact_us'))

        except Exception as e:
            print(f"Error inserting data: {e}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "An error occurred while submitting the form."}), 500
            
            flash("An error occurred while submitting the form. Please try again later.", "danger")
            return redirect(url_for('render_contact_us'))

    # Render the HTML form for GET requests
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('username')
        password = request.form.get('password')
        print("Data from login form:",email_or_username)
        
        print("Data from login form:",password)

        # Check if user exists by email or username
        user = login_collection.find_one({
            "$or": [{"admin": email_or_username}, {"password": email_or_username}]
        })

        if user:
            if user['password'] == password:  
                session['admin'] = user['admin']  # Create a session for the admin
                print('Login successful!', 'success')
                return redirect(url_for('admin'))  
            else:
                print('Invalid password. Please try again.', 'danger')
        else:
            print('User not found. Please check your credentials.', 'danger')

    return render_template('login.html')


# Navigation to  admin 
@app.route('/admin')
def admin():
    # Check if the admin session exists
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Retrieve data from MongoDB, sorted by the timestamp or creation date field in descending order
    data = list(collection.find({}).sort("created_at", -1))  # Replace 'created_at' with the actual field name
    print(data)
    return render_template('admin.html', messages=data)

@app.route('/delete_message', methods=['POST'])
def delete_message():
    # Get the ID from the request body
    data = request.get_json()
    message_id = data.get('id')

    if not message_id:
        return jsonify({'success': False, 'message': 'No ID provided'}), 400

    # Delete the message from MongoDB
    result = collection.delete_one({'_id': ObjectId(message_id)})

    if result.deleted_count > 0:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Message not found'}), 404
    

@app.route('/logout')
def logout():
    session.pop('admin', None)  # Remove the admin session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# def register_user_once():
#     """Function to register a user only once."""
#     existing_user = users_collection.find_one({})  # Check if any user exists
    
#     if existing_user:
#         return {"message": "User already exists. Registration is disabled.", "status": "error"}

#     username = "Admin"  # Default username
#     password = "Dhalia@2025"  # Default password
#     hashed_password = generate_password_hash(password)

#     users_collection.insert_one({"username": username, "password": hashed_password})
    
#     return {"message": "Admin user registered successfully", "status": "success"}

# @app.route("/test-register", methods=["GET"])
# def test_register():
#     """Route to manually trigger the registration function for testing."""
#     result = register_user_once()
#     return jsonify(result)

def insert_admin_credentials():
    admin_data = {
        "admin": "Dhalia",
        "password": "Dhalia@2025"
    }
    try:
        existing_admin = login_collection.find_one({"admin": "Dhalia"})
        if not existing_admin:
            result = login_collection.insert_one(admin_data)
            print(f"Admin credentials inserted with ID: {result.inserted_id}")
        else:
            print("Admin credentials already exist.")
    except Exception as e:
        print(f"Error inserting admin credentials: {e}")
# insert_admin_credentials()
if __name__ == '__main__':
    app.run(debug=True)
