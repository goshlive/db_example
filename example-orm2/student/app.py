# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student

load_dotenv()  # loads .env into environment

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

    # Build SQLALCHEMY_DATABASE_URI
    user = os.getenv('DB_USER', 'root')
    pw = os.getenv('DB_PASS', '')
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', '3306')
    dbname = os.getenv('DB_NAME', 'univerity')

    # using mysql-connector
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{user}:{pw}@{host}:{port}/{dbname}"
    # if you used pymysql: f"mysql+pymysql://{user}:{pw}@{host}:{port}/{dbname}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Optionally create tables if not exist (use with caution in prod)
        db.create_all()

    # ROUTES
    @app.route('/')
    def index():
        students = Student.query.order_by(Student.id).all()
        return render_template('index.html', students=students)
    
    @app.route('/create', methods=['GET', 'POST'])
    def create():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            dept_name = request.form.get('dept_name', '').strip()
            tot_cred = request.form.get('tot_cred', '0')
            try:
                tot_cred = int(tot_cred)
            except ValueError:
                tot_cred = 0
            if not name:
                flash('Name is required.', 'danger')
                return redirect(url_for('create'))
            s = Student(name=name, dept_name=dept_name, tot_cred=tot_cred)
            db.session.add(s)
            db.session.commit()
            flash('Student created.', 'success')
            return redirect(url_for('index'))
        return render_template('form.html', student=None)

    @app.route('/edit/<id>', methods=['GET', 'POST'])
    def edit(id):
        student = Student.query.get_or_404(id)
        if request.method == 'POST':
            student.name = request.form.get('name', student.name).strip()
            student.dept_name = request.form.get('dept_name', student.dept_name).strip()
            try:
                student.tot_cred = int(request.form.get('tot_cred', student.tot_cred))
            except ValueError:
                pass
            db.session.commit()
            flash('Student updated.', 'success')
            return redirect(url_for('index'))
        return render_template('form.html', student=student)

    @app.route('/delete/<id>', methods=['POST'])
    def delete(id):
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted.', 'success')
        return redirect(url_for('index'))

    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.getenv('FLASK_DEBUG') == '1'
    app.run(debug=debug)
