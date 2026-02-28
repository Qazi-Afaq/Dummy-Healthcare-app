# patient registration validation
import re

def validate_registration_form(request):
    errors = []

    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    # Email validation
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not email:
        errors.append("Email is required.")
    elif not re.match(email_regex, email):
        errors.append("Invalid email format.")

    # Username validation
    if not username:
        errors.append("Username is required.")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    elif not username.isalnum():
        errors.append("Username must be alphanumeric.")

    # Password validation
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    elif not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    elif not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number.")

    if errors:
        return False, errors

    return True, None

# default page -> go to self registraton patient
@app.route("/" , methods=["GET" , "POST"])
def register_user():
    if request.method == "POST":
        is_form_valid , errors = validate_registration_form(request)
        if is_form_valid:
            # register the user(patient,admin,provider)
            
            return render_template('dashboard.html')
        else:
            return render_template("register-user.html", errors=errors)
    return render_template('register-user.html')
    

