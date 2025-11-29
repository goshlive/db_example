# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, Course, Section, Classroom, Takes, Department
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

ALLOWED_TABLES = {
    'student': Student,
    'course': Course,
    'section': Section,
    'classroom': Classroom,
    'takes': Takes,
    'department': Department
}

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')
    user = os.getenv('DB_USER', 'root')
    pw = os.getenv('DB_PASS', '')
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', '3306')
    dbname = os.getenv('DB_NAME', 'univerity')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{user}:{pw}@{host}:{port}/{dbname}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    def get_model(table_name):
        model = ALLOWED_TABLES.get(table_name)
        if not model:
            return None
        return model

    def get_pk_columns(model):
        return [c.name for c in model.__table__.primary_key.columns]

    @app.route('/')
    def home():
        return render_template('home.html', tables=list(ALLOWED_TABLES.keys()))

    @app.route('/table/<table_name>')
    def table_view(table_name):
        model = get_model(table_name)
        if not model:
            flash('Unknown table', 'danger')
            return redirect(url_for('home'))
        # fetch all rows (careful with huge tables)
        rows = model.query.limit(1000).all()
        # convert sqlalchemy objects to dicts
        results = []
        cols = [c.name for c in model.__table__.columns]
        for r in rows:
            row = {c: getattr(r, c) for c in cols}
            results.append(row)
        pk_cols = get_pk_columns(model)

        def make_qs(row, pk_cols):
            parts = []
            for p in pk_cols:
                v = row.get(p)
                parts.append(f"{p}={v}" if v is not None else f"{p}=")
            return "&".join(parts)

        rows_with_qs = []
        for r in results:
            r['_pk_qs'] = make_qs(r, pk_cols)
            rows_with_qs.append(r)

        # pass rows_with_qs to template instead of results
        return render_template('table_view.html', table=table_name, cols=cols, rows=rows_with_qs, pk_cols=pk_cols)

    # Generic create
    @app.route('/table/<table_name>/create', methods=['GET', 'POST'])
    def create_table_item(table_name):
        model = get_model(table_name)
        if not model:
            flash('Unknown table', 'danger')
            return redirect(url_for('home'))
        cols = [c for c in model.__table__.columns]
        if request.method == 'POST':
            data = {}
            for col in cols:
                name = col.name
                # skip server-default columns (if any) when empty
                val = request.form.get(name)
                if val == '' or val is None:
                    val = None
                data[name] = val
            try:
                obj = model(**data)
                db.session.add(obj)
                db.session.commit()
                flash(f'{table_name} created.', 'success')
                return redirect(url_for('table_view', table_name=table_name))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                # fall through to re-render form
        # GET -> render form
        return render_template('dynamic_form.html', table=table_name, cols=cols, item=None)

    # Generic edit (PKs passed as querystring)
    @app.route('/table/<table_name>/edit', methods=['GET', 'POST'])
    def edit_table_item(table_name):
        model = get_model(table_name)
        if not model:
            flash('Unknown table', 'danger')
            return redirect(url_for('home'))
        pk_cols = get_pk_columns(model)
        # build pk dict from query params or form data
        pk = {}
        for p in pk_cols:
            v = request.values.get(p)
            if v is None:
                flash('Missing primary key value', 'danger')
                return redirect(url_for('table_view', table_name=table_name))
            pk[p] = v
        # find instance
        instance = model.query.filter_by(**pk).first()
        if not instance:
            flash('Row not found', 'warning')
            return redirect(url_for('table_view', table_name=table_name))
        cols = [c for c in model.__table__.columns]
        if request.method == 'POST':
            for col in cols:
                name = col.name
                # skip PK updates (still allowed if you want, but risky)
                if name in pk_cols:
                    continue
                val = request.form.get(name)
                if val == '':
                    val = None
                setattr(instance, name, val)
            try:
                db.session.commit()
                flash('Updated.', 'success')
                return redirect(url_for('table_view', table_name=table_name))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
        item = {c.name: getattr(instance, c.name) for c in cols}
        return render_template('dynamic_form.html', table=table_name, cols=cols, item=item, pk_cols=pk_cols)

    # Generic delete (POST)
    @app.route('/table/<table_name>/delete', methods=['POST'])
    def delete_table_item(table_name):
        model = get_model(table_name)
        if not model:
            flash('Unknown table', 'danger')
            return redirect(url_for('home'))
        pk_cols = get_pk_columns(model)
        pk = {}
        for p in pk_cols:
            v = request.form.get(p)
            if v is None:
                flash('Missing primary key', 'danger')
                return redirect(url_for('table_view', table_name=table_name))
            pk[p] = v
        instance = model.query.filter_by(**pk).first()
        if not instance:
            flash('Row not found', 'warning')
            return redirect(url_for('table_view', table_name=table_name))
        try:
            db.session.delete(instance)
            db.session.commit()
            flash('Deleted.', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('table_view', table_name=table_name))

    # Execute SELECT query (from textarea). Only allow SELECT queries.
    @app.route('/execute_query', methods=['POST'])
    def execute_query():
        sql = request.form.get('sql_query', '').strip()
        if not sql:
            flash('Empty query', 'warning')
            return redirect(request.referrer or url_for('home'))
        # only allow SELECT to avoid modifications
        if not sql.lower().lstrip().startswith('select'):
            flash('Only SELECT queries are allowed here.', 'danger')
            return redirect(request.referrer or url_for('home'))
        try:
            result = db.session.execute(text(sql))
            # convert to list of mappings (dict-like)
            rows = [dict(r) for r in result.mappings().all()]
            cols = list(rows[0].keys()) if rows else []
            return render_template('query_result.html', sql=sql, cols=cols, rows=rows)
        except SQLAlchemyError as e:
            flash(f'Query error: {str(e)}', 'danger')
            return redirect(request.referrer or url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.getenv('FLASK_DEBUG') == '1'
    app.run(debug=debug)
