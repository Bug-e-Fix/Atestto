# app/routes/public.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash # For hashing passwords
from app.models.user import create_user, get_user_by_email # For database operations

public_bp = Blueprint('public', __name__)

@public_bp.route('/register', methods=['GET', 'POST']) # Allow both GET (display form) and POST (submit form)
def register_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Basic validation: Check if fields are empty
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            # Re-render the form with the entered email to pre-fill it
            return render_template('register.html', email=email)

        # Check if the email already exists in the database
        if get_user_by_email(email):
            flash('Este e-mail já está registrado. Tente fazer login ou recuperar a senha.', 'danger')
            # Re-render the form with the entered email
            return render_template('register.html', email=email)

        # Hash the password before storing it in the database for security
        hashed_password = generate_password_hash(password)

        # Call the create_user function from your models to save the new user
        # Ensure create_user handles database insertion and returns True/False on success/failure
        if create_user(email, hashed_password):
            flash('Cadastro realizado com sucesso! Agora você pode fazer login.', 'success')
            # Redirect to the login page after successful registration
            return redirect(url_for('auth.login'))
        else:
            flash('Ocorreu um erro ao tentar registrar. Por favor, tente novamente.', 'danger')
            return render_template('register.html', email=email) # Stay on register page if creation fails

    # For GET requests, just render the empty registration form
    return render_template('register.html')

# You could add other public routes here if needed
# @public_bp.route('/about')
# def about():
#     return render_template('about.html')
