from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

# Configure Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/smart_agriculture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

# Definitions


def is_authenticated():
    return 'user_email' in session

# Routes


@app.route('/')
def home():
    return render_template('index.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''))


@app.route('/signup')
def get_started():
    return render_template('signup.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_authenticated():
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_email'] = user.email
            session['user_name'] = user.name
            return redirect(url_for('home'))

    return render_template('login.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''))


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login'))

    # Placeholder logic for fetching dashboard data
    dashboard_data = {}  # Replace this with your actual dashboard data retrieval logic

    return render_template('dashboard.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''), dashboard_data=dashboard_data)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if is_authenticated():
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the password and confirm password match
        if password != confirm_password:
            return render_template('signup.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''), error="Passwords do not match")

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''), error="Email already exists")

        # Create a new user with a hashed password
        new_user = User(email=email, name=name,
                        password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        session['user_email'] = new_user.email
        session['user_name'] = new_user.name

        return redirect(url_for('home'))

    return render_template('signup.html', user_authenticated=is_authenticated(), user_name=session.get('user_name', ''))

# Route for the Soil Health Input Page


@app.route('/soil_health', methods=['GET', 'POST'])
def soil_health():
    response = None
    form_data = {}

    if request.method == 'POST':
        # Handle form submission and validation checks for soil-related data
        ph = request.form.get('ph')
        moisture = request.form.get('moisture')
        nutrients = request.form.get('nutrients')

        # Send the input data to the Palm API (placeholder)
        response = generate_text(
            f"What is the soil quality for pH: {ph}, Moisture: {moisture}, Nutrients: {nutrients}, and if it is bad then what should i add to make it good, explain in simple langauge")

        # Retain the form data for re-rendering the template
        form_data = {
            'ph': ph,
            'moisture': moisture,
            'nutrients': nutrients
        }

    return render_template('soil_health_input.html', response=response, form_data=form_data)


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    response = None
    form_data = {}

    if request.method == 'POST':
        
        question = request.form.get('faq')
        
        response = generate_text(
            f"answer this question in detail {question}")
        
        form_data = {
            'question': question,
        }

    return render_template('faq.html', response=response, form_data=form_data)

@app.route('/predictor', methods=['GET', 'POST'])
def predictor():
    response = None
    form_data = {}

    if request.method == 'POST':
        
        city = request.form.get('city')
        
        response = generate_text(
            f"are prices of any fruit, vegetable going to get high according to predictions in {city}, if so then make a list of them")
        
        form_data = {
            'city': city,
        }

    return render_template('predictor.html', response=response, form_data=form_data)


def generate_text(prompt):
    # Import the necessary libraries for sending requests to the Palm API
    import google.generativeai as genai

    # Configure the Palm API with your API key
    genai.configure(api_key="AIzaSyAClD8uaEKmdb_vE6BuB-ZqKrvw2XxVGhI")

    # Set default parameters and send the prompt to the Palm API
    defaults = {
        'model': 'models/text-bison-001',
        'temperature': 0.7,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.95,
        'max_output_tokens': 1024,
        'stop_sequences': [],
        'safety_settings': [
            {"category": "HARM_CATEGORY_DEROGATORY",
                "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_TOXICITY",
                "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_VIOLENCE",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUAL",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_MEDICAL",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ],
    }

    response = genai.generate_text(
        **defaults,
        prompt=prompt
    )

    # Return the generated text from the Palm API response
    return response.result


if __name__ == '__main__':
    # Create tables in the database
    with app.app_context():
        db.create_all()
    app.run(debug=True)