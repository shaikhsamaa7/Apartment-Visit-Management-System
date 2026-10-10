"""
Category management routes for Apartment Visit Management System (AVMS).
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import query_db, execute_db
from security import login_required

category_bp = Blueprint('categories', __name__, url_prefix='/categories')


@category_bp.route('/', methods=['GET', 'POST'])
@login_required
def manage():
    """List all categories and handle category creation."""
    if request.method == 'POST':
        category_name = request.form.get('categoryname', '').strip()

        if not category_name:
            flash("Category name cannot be empty.", "danger")
        else:
            existing = query_db(
                "SELECT id FROM tblcategory WHERE LOWER(categoryName) = LOWER(%s)",
                (category_name,),
                one=True
            )
            if existing:
                flash(f"Category '{category_name}' already exists.", "warning")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_db(
                    "INSERT INTO tblcategory (categoryName, creationDate) VALUES (%s, %s)",
                    (category_name, now_str)
                )
                flash(f"Category '{category_name}' added successfully.", "success")
                return redirect(url_for('categories.manage'))

    categories = query_db("""
        SELECT c.id, c.categoryName, c.creationDate,
               (SELECT COUNT(*) FROM tblvisitor v WHERE v.categoryName = c.categoryName) AS visitor_count,
               (SELECT COUNT(*) FROM tblvisitorpass p WHERE p.categoryName = c.categoryName) AS pass_count
        FROM tblcategory c
        ORDER BY c.categoryName ASC
    """)

    return render_template('categories/manage.html', categories=categories)


@category_bp.route('/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete(cat_id):
    """Safely delete category via POST with CSRF verification."""
    category = query_db("SELECT id, categoryName FROM tblcategory WHERE id = %s", (cat_id,), one=True)
    if not category:
        flash("Category not found.", "warning")
    else:
        execute_db("DELETE FROM tblcategory WHERE id = %s", (cat_id,))
        flash(f"Category '{category['categoryName']}' deleted.", "info")

    return redirect(url_for('categories.manage'))
