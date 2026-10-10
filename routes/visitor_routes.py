"""
Visitor management routes for Apartment Visit Management System (AVMS).
Handles registration, listing, checkout remark recording, search, and CSV export.
"""

import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from database.db import query_db, execute_db
from security import login_required

visitor_bp = Blueprint('visitors', __name__, url_prefix='/visitors')


@visitor_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Register a new apartment visitor."""
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        visname = request.form.get('visname', '').strip()
        mobilenumber = request.form.get('mobilenumber', '').strip()
        address = request.form.get('address', '').strip()
        apartment = request.form.get('apartment', '').strip()
        floor = request.form.get('floor', '').strip()
        whomtomeet = request.form.get('whomtomeet', '').strip()
        reasontomeet = request.form.get('reasontomeet', '').strip()

        # Validation
        errors = []
        if not category:
            errors.append("Please select a visitor category.")
        if not visname:
            errors.append("Visitor name is required.")
        if not mobilenumber or not mobilenumber.isdigit() or len(mobilenumber) < 7:
            errors.append("Please enter a valid numeric mobile contact number.")
        if not apartment:
            errors.append("Apartment number is required.")
        if not floor:
            errors.append("Floor is required.")
        if not whomtomeet:
            errors.append("Resident to meet ('Whom to Meet') is required.")

        if errors:
            for err in errors:
                flash(err, "danger")
            categories = query_db("SELECT categoryName FROM tblcategory ORDER BY categoryName ASC")
            return render_template('visitors/form.html', categories=categories, form_data=request.form)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_db(
            """INSERT INTO tblvisitor 
               (categoryName, VisitorName, MobileNumber, Address, Apartment, Floor, WhomtoMeet, ReasontoMeet, EnterDate) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (category, visname, int(mobilenumber), address, apartment, floor, whomtomeet, reasontomeet, now_str)
        )

        flash(f"Visitor '{visname}' registered successfully.", "success")
        return redirect(url_for('visitors.manage'))

    categories = query_db("SELECT categoryName FROM tblcategory ORDER BY categoryName ASC")
    return render_template('visitors/form.html', categories=categories, form_data={})


@visitor_bp.route('/')
@visitor_bp.route('/manage')
@login_required
def manage():
    """List all registered visitors with status indicators and search filter."""
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    sql = "SELECT * FROM tblvisitor WHERE 1=1"
    params = []

    if category_filter:
        sql += " AND categoryName = %s"
        params.append(category_filter)

    if status_filter == 'inside':
        sql += " AND (remark IS NULL OR remark = '')"
    elif status_filter == 'checked_out':
        sql += " AND (remark IS NOT NULL AND remark != '')"

    sql += " ORDER BY ID DESC"
    visitors = query_db(sql, params)

    categories = query_db("SELECT categoryName FROM tblcategory ORDER BY categoryName ASC")

    return render_template(
        'visitors/manage.html',
        visitors=visitors,
        categories=categories,
        selected_category=category_filter,
        selected_status=status_filter
    )


@visitor_bp.route('/<int:visitor_id>', methods=['GET', 'POST'])
@login_required
def detail(visitor_id):
    """View visitor details and record checkout timestamp and remark."""
    visitor = query_db("SELECT * FROM tblvisitor WHERE ID = %s", (visitor_id,), one=True)
    if not visitor:
        flash("Visitor record not found.", "warning")
        return redirect(url_for('visitors.manage'))

    if request.method == 'POST':
        remark = request.form.get('remark', '').strip()
        if not remark:
            flash("Please provide an outing remark before checking out.", "danger")
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute_db(
                "UPDATE tblvisitor SET remark = %s, outtime = %s WHERE ID = %s",
                (remark, now_str, visitor_id)
            )
            flash("Visitor check-out time and remark recorded successfully.", "success")
            return redirect(url_for('visitors.detail', visitor_id=visitor_id))

    return render_template('visitors/detail.html', visitor=visitor)


@visitor_bp.route('/search')
@login_required
def search():
    """Search visitors by name or mobile number."""
    query = request.args.get('q', '').strip()
    results = []

    if query:
        pattern = f"%{query}%"
        results = query_db(
            """SELECT * FROM tblvisitor 
               WHERE VisitorName LIKE %s OR CAST(MobileNumber AS CHAR) LIKE %s OR Apartment LIKE %s OR WhomtoMeet LIKE %s
               ORDER BY ID DESC""",
            (pattern, pattern, pattern, pattern)
        )

    return render_template('visitors/search.html', query=query, results=results)


@visitor_bp.route('/export')
@login_required
def export_csv():
    """Export all visitor records to CSV."""
    visitors = query_db("SELECT * FROM tblvisitor ORDER BY ID DESC")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Visitor Name', 'Category', 'Mobile Number', 'Apartment',
        'Floor', 'Whom to Meet', 'Reason to Meet', 'Address', 'Entry Date',
        'Outing Remark', 'Out Time'
    ])

    for v in visitors:
        writer.writerow([
            v['ID'], v['VisitorName'], v['categoryName'], v['MobileNumber'],
            v['Apartment'], v['Floor'], v['WhomtoMeet'], v['ReasontoMeet'],
            v['Address'], v['EnterDate'], v['remark'] or '', v['outtime'] or ''
        ])

    output.seek(0)
    filename = f"visitors_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
