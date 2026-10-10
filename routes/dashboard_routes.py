"""
Dashboard routes for Apartment Visit Management System (AVMS).
Computes real database metrics and recent activity.
"""

from datetime import date, timedelta
from flask import Blueprint, render_template
from database.db import query_db
from security import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Render the executive property-management dashboard with real computed metrics."""
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    sevendays_str = (date.today() - timedelta(days=7)).isoformat()

    # Core visitor statistics from database
    today_vis = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitor WHERE date(EnterDate) = %s",
        (today_str,),
        one=True
    )['count']

    yesterday_vis = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitor WHERE date(EnterDate) = %s",
        (yesterday_str,),
        one=True
    )['count']

    last7days_vis = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitor WHERE date(EnterDate) >= %s",
        (sevendays_str,),
        one=True
    )['count']

    total_vis = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitor",
        one=True
    )['count']

    # Visitors currently inside (no checkout remark or outtime)
    currently_inside = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitor WHERE remark IS NULL OR remark = ''",
        one=True
    )['count']

    # Categories count
    total_categories = query_db(
        "SELECT COUNT(*) AS count FROM tblcategory",
        one=True
    )['count']

    # Pass counts
    total_passes = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitorpass",
        one=True
    )['count']

    active_passes = query_db(
        "SELECT COUNT(*) AS count FROM tblvisitorpass WHERE toDate >= %s",
        (today_str,),
        one=True
    )['count']

    # Recent visitor activity
    recent_visitors = query_db(
        """SELECT ID, VisitorName, categoryName, Apartment, Floor, WhomtoMeet, EnterDate, remark, outtime 
           FROM tblvisitor 
           ORDER BY ID DESC LIMIT 6"""
    )

    # Recent passes issued
    recent_passes = query_db(
        """SELECT ID, passnumber, VisitorName, categoryName, Apartment, Floor, fromDate, toDate, creationDate 
           FROM tblvisitorpass 
           ORDER BY ID DESC LIMIT 5"""
    )

    # Category distribution
    category_breakdown = query_db(
        """SELECT categoryName, COUNT(*) AS count 
           FROM tblvisitor 
           WHERE categoryName IS NOT NULL AND categoryName != ''
           GROUP BY categoryName 
           ORDER BY count DESC LIMIT 6"""
    )

    stats = {
        'today_visitors': today_vis,
        'yesterday_visitors': yesterday_vis,
        'last7days_visitors': last7days_vis,
        'total_visitors': total_vis,
        'currently_inside': currently_inside,
        'total_categories': total_categories,
        'total_passes': total_passes,
        'active_passes': active_passes,
    }

    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_visitors=recent_visitors,
        recent_passes=recent_passes,
        category_breakdown=category_breakdown,
        today=today_str
    )
