"""
Tests for between-dates reports for visitors and passes.
"""

from datetime import date, timedelta


def test_visitor_between_dates_report(authenticated_client):
    """Test generating a between-dates visitors report."""
    today_str = date.today().isoformat()
    past_str = (date.today() - timedelta(days=30)).isoformat()

    resp = authenticated_client.post('/reports/visitors', data={
        'fromdate': past_str,
        'todate': today_str
    })

    assert resp.status_code == 200
    assert b"Report Period" in resp.data
    assert b"Total Visits" in resp.data


def test_pass_between_dates_report(authenticated_client):
    """Test generating a between-dates pass report."""
    today_str = date.today().isoformat()
    past_str = (date.today() - timedelta(days=30)).isoformat()

    resp = authenticated_client.post('/reports/passes', data={
        'fromdate': past_str,
        'todate': today_str
    })

    assert resp.status_code == 200
    assert b"Creation Window" in resp.data
    assert b"Total Passes" in resp.data


def test_report_csv_export(authenticated_client):
    """Test CSV export within the between-dates report view."""
    today_str = date.today().isoformat()
    past_str = (date.today() - timedelta(days=30)).isoformat()

    resp = authenticated_client.post('/reports/visitors', data={
        'fromdate': past_str,
        'todate': today_str,
        'export': 'csv'
    })

    assert resp.status_code == 200
    assert resp.mimetype == 'text/csv'
    assert f"visitor_report_{past_str}_to_{today_str}.csv" in resp.headers['Content-Disposition']
