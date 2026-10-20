# Validation record

Tested with Python 3.12, MySQL Community Server 8.0.46, and these packages:

- Flask 3.1.3
- SQLAlchemy 2.0.55
- mysql-connector-python 9.7.0
- python-dotenv 1.2.4

Passed:

- Actual MySQL cursor operations in raw and prepared=True modes.
- Actual MySQL SQLAlchemy ORM CRUD, 1-N and M-N joins.
- Console CRUD demonstration, both joins and SELECT-only injection demonstration in all three modes.
- Flask test-client requests against actual MySQL: CRUD, HTML, JSON, joins, injection behavior, duplicate IDs, parent FK rejection and POST token checks.
- Optional sample loader refuses nonempty tables. Original sample data preserved after temporary-row cleanup.
- Fourteen additional isolated regression checks using SQLAlchemy/Flask and a cursor adapter.

The real MySQL checks used a separate test schema built from the original Restaurant DDL. No MySQL server, credentials, test database or virtual environment is bundled. Windows/VS Code setup commands are provided; execution here was on Linux. Configure your existing local MySQL schema before running verify_live.py.
