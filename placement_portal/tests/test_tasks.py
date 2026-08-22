from app.tasks import monthly_report
def test_monthly_report(app):
    with app.app_context():
        result=monthly_report()
        assert result["path"].endswith('.html')
        assert result["delivery"] in ("EMAIL","LOCAL_LOG")
