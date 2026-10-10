"""
Reporting routes for Apartment Visit Management System (AVMS).
Provides between-dates reporting for both visitors and passes, with CSV export.
"""

import csv
import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, Response
from database.db import query_db
from security import login_required

report_bp = Blueprint('reports', __name__, url_prefix='/reports')


@report_bp.route('/visitors', methods=['GET', 'POST'])
@login_required
def visitors():
    """Between-dates visitors report."""
    from_date = request.values.get('fromdate', '').strip()
    to_date = request.values.get('todate', '').strip()
    export_format = request.values.get('export', '').strip()

    records = []
    has_searched = False
    stats = {}

    if from_date and to_date:
        has_searched = True
        records = query_db(
            """SELECT * FROM tblvisitor 
               WHERE date(EnterDate) BETWEEN %s AND %s 
               ORDER BY ID DESC""",
            (from_date, to_date)
        )

        total_in_period = len(records)
        checked_out = sum(1 for r in records if r.get('remark'))
        inside = total_in_period - checked_out
        stats = {
            'total': total_in_period,
            'checked_out': checked_out,
            'inside': inside
        }

        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'ID', 'Visitor Name', 'Category', 'Mobile Number',
                'Apartment', 'Floor', 'Whom to Meet', 'Reason to Meet',
                'Address', 'Entry Date', 'Outing Remark', 'Out Time'
            ])
            for r in records:
                writer.writerow([
                    r['ID'], r['VisitorName'], r['categoryName'], r['MobileNumber'],
                    r['Apartment'], r['Floor'], r['WhomtoMeet'], r['ReasontoMeet'],
                    r['Address'], r['EnterDate'], r['remark'] or '', r['outtime'] or ''
                ])
            output.seek(0)
            filename = f"visitor_report_{from_date}_to_{to_date}.csv"
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )

    return render_template(
        'reports/visitors_report.html',
        from_date=from_date,
        to_date=to_date,
        records=records,
        stats=stats,
        has_searched=has_searched
    )


@report_bp.route('/passes', methods=['GET', 'POST'])
@login_required
def passes():
    """Between-dates passes report."""
    from_date = request.values.get('fromdate', '').strip()
    to_date = request.values.get('todate', '').strip()
    export_format = request.values.get('export', '').strip()

    records = []
    has_searched = False
    stats = {}
    today_str = date.today().isoformat()

    if from_date and to_date:
        has_searched = True
        records = query_db(
            """SELECT * FROM tblvisitorpass 
               WHERE date(creationDate) BETWEEN %s AND %s 
               ORDER BY ID DESC""",
            (from_date, to_date)
        )

        total_in_period = len(records)
        active_count = sum(1 for r in records if str(r.get('toDate')) >= today_str)
        expired_count = total_in_period - active_count
        stats = {
            'total': total_in_period,
            'active': active_count,
            'expired': expired_count
        }

        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'ID', 'Pass Number', 'Visitor Name', 'Category', 'Mobile Number',
                'Apartment', 'Floor', 'Pass Details', 'From Date', 'To Date', 'Creation Date'
            ])
            for r in records:
                writer.writerow([
                    r['ID'], r['passnumber'], r['VisitorName'], r['categoryName'],
                    r['MobileNumber'], r['Apartment'], r['Floor'], r['passDetails'],
                    r['fromDate'], r['toDate'], r['creationDate']
                ])
            output.seek(0)
            filename = f"pass_report_{from_date}_to_{to_date}.csv"
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )

    return render_template(
        'reports/passes_report.html',
        from_date=from_date,
        to_date=to_date,
        records=records,
        stats=stats,
        today=today_str,
        has_searched=has_searched
    )
