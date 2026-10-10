"""
Authentication and administrative account routes for AVMS.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import query_db, execute_db
from security import login_required, hash_password, verify_password_and_check_upgrade

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle administrative login with legacy MD5 upgrade support and session regeneration."""
    if session.get('admin_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('auth/login.html', username=username)

        admin = query_db(
            "SELECT ID, AdminName, UserName, MobileNumber, Email, Password FROM tbladmin WHERE UserName = %s",
            (username,),
            one=True
        )

        if admin:
            is_valid, needs_upgrade = verify_password_and_check_upgrade(admin['Password'], password)
            if is_valid:
                # If password was verified via legacy MD5, automatically upgrade hash to PBKDF2
                if needs_upgrade:
                    new_hash = hash_password(password)
                    execute_db("UPDATE tbladmin SET Password = %s WHERE ID = %s", (new_hash, admin['ID']))

                # Regenerate session state to prevent session fixation attacks
                session.clear()
                session['admin_id'] = admin['ID']
                session['admin_user'] = admin['UserName']
                session['admin_name'] = admin['AdminName'] or admin['UserName']
                session.permanent = True

                flash(f"Welcome back, {session['admin_name']}!", "success")
                next_url = request.args.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))

        flash("Invalid Username or Password. Please try again.", "danger")

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Terminate the authenticated session and redirect to login."""
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Verify administrator contact info before permitting password reset."""
    if session.get('admin_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        contactno = request.form.get('contactno', '').strip()

        if not email or not contactno:
            flash("Please enter both registered Email and Mobile Number.", "danger")
            return render_template('auth/forgot_password.html')

        admin = query_db(
            "SELECT ID FROM tbladmin WHERE Email = %s AND MobileNumber = %s",
            (email, contactno),
            one=True
        )

        if admin:
            session['reset_allowed_admin_id'] = admin['ID']
            session['reset_email'] = email
            session['reset_contactno'] = contactno
            flash("Account verified. Please set your new password.", "info")
            return redirect(url_for('auth.reset_password'))
        else:
            flash("No matching administrator record found with those details.", "danger")

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset administrator password after identity verification."""
    admin_id = session.get('reset_allowed_admin_id')
    if not admin_id:
        flash("Password reset session expired or unauthorized. Please verify your details again.", "warning")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('newpassword', '')
        confirm_password = request.form.get('confirmpassword', '')

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('auth/reset_password.html')

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/reset_password.html')

        hashed = hash_password(new_password)
        execute_db("UPDATE tbladmin SET Password = %s WHERE ID = %s", (hashed, admin_id))

        # Clear reset tokens
        session.pop('reset_allowed_admin_id', None)
        session.pop('reset_email', None)
        session.pop('reset_contactno', None)

        flash("Your password has been successfully reset. Please log in with your new credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow logged in administrator to safely change their password."""
    admin_id = session['admin_id']

    if request.method == 'POST':
        current_pass = request.form.get('currentpassword', '')
        new_pass = request.form.get('newpassword', '')
        confirm_pass = request.form.get('confirmpassword', '')

        admin = query_db("SELECT Password FROM tbladmin WHERE ID = %s", (admin_id,), one=True)
        if not admin:
            flash("User not found.", "danger")
            return redirect(url_for('auth.logout'))

        is_valid, _ = verify_password_and_check_upgrade(admin['Password'], current_pass)
        if not is_valid:
            flash("Current password is incorrect.", "danger")
            return render_template('auth/change_password.html')

        if len(new_pass) < 6:
            flash("New password must be at least 6 characters.", "danger")
            return render_template('auth/change_password.html')

        if new_pass != confirm_pass:
            flash("New passwords do not match.", "danger")
            return render_template('auth/change_password.html')

        new_hash = hash_password(new_pass)
        execute_db("UPDATE tbladmin SET Password = %s WHERE ID = %s", (new_hash, admin_id))
        flash("Password successfully changed.", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update administrator profile information."""
    admin_id = session['admin_id']

    if request.method == 'POST':
        admin_name = request.form.get('adminname', '').strip()
        mob_number = request.form.get('mobilenumber', '').strip()
        email = request.form.get('email', '').strip()

        if not admin_name or not mob_number or not email:
            flash("All fields are required.", "danger")
        else:
            execute_db(
                "UPDATE tbladmin SET AdminName = %s, MobileNumber = %s, Email = %s WHERE ID = %s",
                (admin_name, mob_number, email, admin_id)
            )
            session['admin_name'] = admin_name
            flash("Admin profile successfully updated.", "success")
            return redirect(url_for('auth.profile'))

    admin = query_db("SELECT * FROM tbladmin WHERE ID = %s", (admin_id,), one=True)
    return render_template('auth/profile.html', admin=admin)
