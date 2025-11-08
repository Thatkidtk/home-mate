run:
	FLASK_DEBUG=1 FLASK_APP=wsgi.py flask run --host=0.0.0.0 --port=8000

seed:
	FLASK_APP=wsgi.py flask seed-data

db-up:
	FLASK_APP=wsgi.py flask db upgrade

fmt:
	ruff check --fix .
	black .
