"""
Visitor pass management routes for Apartment Visit Management System (AVMS).
Handles creation, listing, printable pass display, deletion, and CSV export.
"""

import csv
import io
import random
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from database.db import query_db, execute_db
from security import login_required

pass_bp = Blueprint('passes', __name__, url_prefix='/passes')


@pass_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new apartment visitor pass."""
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        visname = request.form.get('visname', '').strip()
        mobilenumber = request.form.get('mobilenumber', '').strip()
        address = request.form.get('address', '').strip()
        apartment = request.form.get('apartment', '').strip()
        floor = request.form.get('floor', '').strip()
        pass_desc = request.form.get('passdescription', '').strip()
        from_date = request.form.get('fromdate', '').strip()
        to_date = request.form.get('todate', '').strip()

        errors = []
        if not category:
            errors.append("Please select a visitor category.")
        if not visname:
            errors.append("Visitor name is required.")
        if not mobilenumber or not mobilenumber.isdigit():
            errors.append("Please enter a valid numeric contact number.")
        if not apartment:
            errors.append("Apartment number is required.")
        if not floor:
            errors.append("Floor is required.")
        if not pass_desc:
            errors.append("Pass description is required.")
        if not from_date or not to_date:
            errors.append("Both From Date and To Date are required.")
        elif from_date > to_date:
            errors.append("From Date cannot be later than To Date.")

        if errors:
            for err in errors:
                flash(err, "danger")
            categories = query_db("SELECT categoryName FROM tblcategory ORDER BY categoryName ASC")
            return render_template('passes/create.html', categories=categories, form_data=request.form)

        # Generate unique 8-digit pass number
        pass_num = random.randint(10000000, 99999999)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lastrowid, _ = execute_db(
            """INSERT INTO tblvisitorpass 
               (passnumber, categoryName, VisitorName, MobileNumber, Address, Apartment, Floor, passDetails, fromDate, toDate, creationDate) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (pass_num, category, visname, int(mobilenumber), address, apartment, floor, pass_desc, from_date, to_date, now_str)
        )

        flash(f"Pass #{pass_num} issued successfully for {visname}.", "success")
        return redirect(url_for('passes.detail', pass_id=lastrowid))

    categories = query_db("SELECT categoryName FROM tblcategory ORDER BY categoryName ASC")
    today_str = date.today().isoformat()
    return render_template('passes/create.html', categories=categories, today=today_str, form_data={})


@pass_bp.route('/')
@pass_bp.route('/manage')
@login_required
def manage():
    """List all passes with validity statuses and delete actions."""
    status_filter = request.args.get('status', '').strip()
    today_str = date.today().isoformat()

    sql = "SELECT * FROM tblvisitorpass WHERE 1=1"
    params = []

    if status_filter == 'active':
        sql += " AND toDate >= %s"
        params.append(today_str)
    elif status_filter == 'expired':
        sql += " AND toDate < %s"
        params.append(today_str)

    sql += " ORDER BY ID DESC"
    passes = query_db(sql, params)

    return render_template(
        'passes/manage.html',
        passes=passes,
        today=today_str,
        selected_status=status_filter
    )


@pass_bp.route('/<int:pass_id>')
@login_required
def detail(pass_id):
    """View pass details formatted for printable pass card badge."""
    vpass = query_db("SELECT * FROM tblvisitorpass WHERE ID = %s", (pass_id,), one=True)
    if not vpass:
        flash("Pass record not found.", "warning")
        return redirect(url_for('passes.manage'))

    today_str = date.today().isoformat()
    is_active = (str(vpass['toDate']) >= today_str)

    return render_template('passes/detail.html', vpass=vpass, is_active=is_active)


@pass_bp.route('/<int:pass_id>/delete', methods=['POST'])
@login_required
def delete(pass_id):
    """Safely delete a visitor pass via POST with CSRF verification."""
    vpass = query_db("SELECT passnumber FROM tblvisitorpass WHERE ID = %s", (pass_id,), one=True)
    if not vpass:
        flash("Pass not found or already deleted.", "warning")
    else:
        execute_db("DELETE FROM tblvisitorpass WHERE ID = %s", (pass_id,))
        flash(f"Pass #{vpass['passnumber']} has been deleted.", "info")

    return redirect(url_for('passes.manage'))


@pass_bp.route('/export')
@login_required
def export_csv():
    """Export all visitor passes to CSV."""
    passes = query_db("SELECT * FROM tblvisitorpass ORDER BY ID DESC")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Pass Number', 'Visitor Name', 'Category', 'Mobile Number',
        'Apartment', 'Floor', 'Pass Details', 'From Date', 'To Date', 'Creation Date'
    ])

    for p in passes:
        writer.writerow([
            p['ID'], p['passnumber'], p['VisitorName'], p['categoryName'],
            p['MobileNumber'], p['Apartment'], p['Floor'], p['passDetails'],
            p['fromDate'], p['toDate'], p['creationDate']
        ])

    output.seek(0)
    filename = f"passes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
