"""Local Flask UI. Routes reuse exactly the repositories called by console.py."""
import os
import secrets
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from mysql.connector import Error as MySQLError, IntegrityError as MySQLIntegrityError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config import enabled
from dto import CustomerDTO, to_plain
from repositories import get_repository


def create_app(repository_factory=None):
    app = Flask(__name__)
    # A fresh signing key, reseted on each restart.
    app.secret_key = secrets.token_hex(32)
    factory = repository_factory or get_repository

    @app.context_processor
    def form_helpers():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(24)
        return {'csrf_token': session['csrf_token'],
                'raw_enabled': enabled('ALLOW_UNSAFE_SQL')}

    @app.before_request
    def check_form_token():
        # A POST changes data; a GET never performs CRUD writes.
        if request.method == 'POST':
            expected = session.get('csrf_token', '')
            supplied = request.form.get('csrf_token', '')
            if not expected or not secrets.compare_digest(expected, supplied):
                abort(403, 'Reload the page and submit its form again.')

    def mode():
        return request.values.get('mode', 'prepared')

    def repository():
        return factory(mode())

    def page(rows=None, title='Customers', message=''):
        return render_template('index.html', mode=mode(), title=title,
                               rows=to_plain(rows or []), message=message)

    def identity(value):
        value = value.strip()
        if not value or len(value) > 10:
            raise ValueError('ID must contain 1 to 10 characters.')
        return value

    def customer_name():
        value = request.form.get('customer_name', '').strip()
        if not value or len(value) > 100:
            raise ValueError('Name must contain 1 to 100 characters.')
        return value

    @app.get('/')
    def index():
        return page(repository().list_customers(), message=request.args.get('message', ''))

    @app.get('/customer')
    def customer():
        result = repository().get_customer(identity(request.args.get('customer_id', '')))
        return page([result] if result else [], 'One customer')

    @app.post('/customers/create')
    def create_customer():
        customer_id = identity(request.form.get('customer_id', ''))
        repository().create_customer(CustomerDTO(customer_id, customer_name()))
        return redirect(url_for('index', mode=mode(), message='Customer created.'))

    @app.post('/customers/update')
    def update_customer():
        customer_id = identity(request.form.get('customer_id', ''))
        count = repository().update_customer(customer_id, customer_name())
        message = 'Update processed. Read the customer to verify.' if count else 'No change or ID not found.'
        return redirect(url_for('index', mode=mode(), message=message))

    @app.post('/customers/delete')
    def delete_customer():
        customer_id = identity(request.form.get('customer_id', ''))
        count = repository().delete_customer(customer_id)
        return redirect(url_for('index', mode=mode(), message=f'Deleted rows: {count}'))

    @app.get('/search')
    def search():
        # Keep the same search value for all three modes, including the lesson payload.
        return page(repository().search_customers(request.args.get('name', '')), 'Exact-name search')

    @app.get('/orders')
    def orders():
        customer_id = identity(request.args.get('customer_id', 'C01'))
        return page(repository().customer_orders(customer_id), '1-N Customer orders')

    @app.get('/details')
    def details():
        order_id = identity(request.args.get('order_id', 'O101'))
        return page(repository().order_details(order_id), 'M-N Order menu items')

    @app.get('/api/customers')
    def api_customers():
        return jsonify(to_plain(repository().list_customers()))

    @app.get('/api/orders/<order_id>/items')
    def api_order_items(order_id):
        return jsonify(to_plain(repository().order_details(identity(order_id))))

    @app.errorhandler(ValueError)
    def invalid_input(error):
        return page(title='Input or configuration error', message=str(error)), 400

    @app.errorhandler(MySQLError)
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        app.logger.exception('Database operation failed')
        conflict = isinstance(error, (MySQLIntegrityError, IntegrityError))
        message = ('Constraint rejected the operation. Check duplicate IDs or dependent orders.'
                   if conflict else
                   'Database operation failed. Check the VS Code terminal for details. '
                   'In raw mode, an apostrophe may break the SQL statement.')
        return page(title='Database error', message=message), 409 if conflict else 500

    return app


if __name__ == '__main__':
    # run the app with a fixed port, so the browser can bookmark it. 
    create_app().run(host='127.0.0.1', port=int(os.getenv('FLASK_PORT', '5000')),
                     debug=False, use_reloader=False)
