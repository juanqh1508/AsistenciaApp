from models import db, AttendanceRecord, User
import os
from datetime import datetime
from sqlalchemy import func, extract, text, or_
from dotenv import load_dotenv
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///attendance.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'fuente-de-bendicion-secret-2024')

db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                return "Acceso Denegado: No tienes permisos para esta sección", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def init_db():
    with app.app_context():
        db.create_all()
        # Seed users if not exist (Update with new credentials)
        # Clear old testing users if any (optional but good for this change)
        if not User.query.filter_by(username='Protocolo').first():
            # Delete old users first to avoid confusion
            User.query.filter(User.username.in_(['admin', 'protocolo', 'pastor'])).delete()
            
            db.session.add(User(username='Protocolo', password='bless2026', role='protocolo'))
            db.session.add(User(username='Pastor', password='yaweh2026', role='pastor'))
            db.session.add(User(username='Administracion', password='jireh2026', role='administracion'))
            db.session.add(User(username='Developer', password='Juan1508*', role='developer'))
            db.session.commit()

init_db()

# Updated Ministries as per user request
MINISTRIES = ["Niños", "Adolescentes", "Jóvenes", "Caballeros", "Damas", "Intercesión", "Alabanza", "Evangelismo", "General", "Familia", "Águilas"]
SERVICE_TYPES = ["Local", "Zona", "Provincial", "Nacional"]
SHIFTS = ["Mañana", "Tarde", "Noche"]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user_role=session.get('role'), username=session.get('username'))

@app.route('/registro')
@login_required
@role_required(['admin', 'developer', 'protocolo'])
def index():
    return render_template('index.html', ministries=MINISTRIES, service_types=SERVICE_TYPES, shifts=SHIFTS, user_role=session.get('role'), username=session.get('username'))

@app.route('/submit', methods=['POST'])
@login_required
@role_required(['admin', 'developer', 'protocolo'])
def submit():
    data = request.form
    date_str = data.get('date')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    
    # Automate Day Category
    day_category = 'Dominical' if date_obj.weekday() == 6 else 'Semana'
    
    record = AttendanceRecord(
        date=date_obj,
        ministry_of_service=data.get('ministry_of_service'),
        service_type=data.get('service_type'),
        shift=data.get('shift'),
        day_category=day_category,
        kids=int(data.get('kids', 0)),
        teens=int(data.get('teens', 0)),
        youth=int(data.get('youth', 0)),
        women=int(data.get('women', 0)),
        men=int(data.get('men', 0)),
        visits_kids=int(data.get('visits_kids', 0)),
        visits_teens=int(data.get('visits_teens', 0)),
        visits_youth=int(data.get('visits_youth', 0)),
        visits_women=int(data.get('visits_women', 0)),
        visits_men=int(data.get('visits_men', 0)),
        testimonies_kids=int(data.get('testimonies_kids', 0)),
        testimonies_teens=int(data.get('testimonies_teens', 0)),
        testimonies_youth=int(data.get('testimonies_youth', 0)),
        testimonies_women=int(data.get('testimonies_women', 0)),
        testimonies_men=int(data.get('testimonies_men', 0)),
        converts_kids=int(data.get('converts_kids', 0)),
        converts_teens=int(data.get('converts_teens', 0)),
        converts_youth=int(data.get('converts_youth', 0)),
        converts_women=int(data.get('converts_women', 0)),
        converts_men=int(data.get('converts_men', 0)),
        reconciled_kids=int(data.get('reconciled_kids', 0)),
        reconciled_teens=int(data.get('reconciled_teens', 0)),
        reconciled_youth=int(data.get('reconciled_youth', 0)),
        reconciled_women=int(data.get('reconciled_women', 0)),
        reconciled_men=int(data.get('reconciled_men', 0))
    )
    
    # Calculate totals
    record.visits = record.visits_kids + record.visits_teens + record.visits_youth + record.visits_women + record.visits_men
    record.testimonies = record.testimonies_kids + record.testimonies_teens + record.testimonies_youth + record.testimonies_women + record.testimonies_men
    record.converts_total = record.converts_kids + record.converts_teens + record.converts_youth + record.converts_women + record.converts_men
    
    try:
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"ERROR AL GUARDAR: {e}")
        return f"Error al guardar en la base de datos: {e}", 500
        
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required(['developer'])
def delete_record(id):
    record = AttendanceRecord.query.get_or_404(id)
    try:
        db.session.delete(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Error al eliminar: {e}", 500
    return redirect(url_for('details_view'))

@app.route('/reports')
@login_required
def reports():
    month_filter = request.args.get('month') or datetime.now().strftime('%Y-%m')
    year, month = map(int, month_filter.split('-'))
    
    # 1. GENERAL CHURCH REPORT
    def get_gen_stats(category=None):
        q = db.session.query(
            func.sum(AttendanceRecord.kids).label('kids'),
            func.sum(AttendanceRecord.teens).label('teens'),
            func.sum(AttendanceRecord.youth).label('youth'),
            func.sum(AttendanceRecord.women).label('women'),
            func.sum(AttendanceRecord.men).label('men'),
            func.sum(AttendanceRecord.visits_kids).label('visits_kids'),
            func.sum(AttendanceRecord.visits_teens).label('visits_teens'),
            func.sum(AttendanceRecord.visits_youth).label('visits_youth'),
            func.sum(AttendanceRecord.visits_women).label('visits_women'),
            func.sum(AttendanceRecord.visits_men).label('visits_men'),
            func.sum(AttendanceRecord.testimonies_kids).label('testimonies_kids'),
            func.sum(AttendanceRecord.testimonies_teens).label('testimonies_teens'),
            func.sum(AttendanceRecord.testimonies_youth).label('testimonies_youth'),
            func.sum(AttendanceRecord.testimonies_women).label('testimonies_women'),
            func.sum(AttendanceRecord.testimonies_men).label('testimonies_men'),
            func.sum(AttendanceRecord.converts_kids).label('converts_kids'),
            func.sum(AttendanceRecord.converts_teens).label('converts_teens'),
            func.sum(AttendanceRecord.converts_youth).label('converts_youth'),
            func.sum(AttendanceRecord.converts_women).label('converts_women'),
            func.sum(AttendanceRecord.converts_men).label('converts_men'),
            func.sum(AttendanceRecord.reconciled_kids).label('reconciled_kids'),
            func.sum(AttendanceRecord.reconciled_teens).label('reconciled_teens'),
            func.sum(AttendanceRecord.reconciled_youth).label('reconciled_youth'),
            func.sum(AttendanceRecord.reconciled_women).label('reconciled_women'),
            func.sum(AttendanceRecord.reconciled_men).label('reconciled_men'),
            func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total_asistencia'),
            func.sum(AttendanceRecord.visits_kids + AttendanceRecord.visits_teens + AttendanceRecord.visits_youth + AttendanceRecord.visits_women + AttendanceRecord.visits_men).label('total_visitas'),
            func.sum(AttendanceRecord.testimonies_kids + AttendanceRecord.testimonies_teens + AttendanceRecord.testimonies_youth + AttendanceRecord.testimonies_women + AttendanceRecord.testimonies_men).label('total_testimonios'),
            func.sum(AttendanceRecord.converts_kids + AttendanceRecord.converts_teens + AttendanceRecord.converts_youth + AttendanceRecord.converts_women + AttendanceRecord.converts_men).label('total_convertidos'),
            func.sum(AttendanceRecord.reconciled_kids + AttendanceRecord.reconciled_teens + AttendanceRecord.reconciled_youth + AttendanceRecord.reconciled_women + AttendanceRecord.reconciled_men).label('total_reconciliados')
        ).filter(extract('year', AttendanceRecord.date) == year, extract('month', AttendanceRecord.date) == month)
        if category:
            q = q.filter(AttendanceRecord.day_category == category)
        return q.first()

    gen_church = {
        'semana': get_gen_stats('Semana'),
        'dominical': get_gen_stats('Dominical'),
        'total': get_gen_stats()
    }

    # 2. MINISTRY SPECIFIC REPORTS
    MERGE_GROUPS = {'Adolescentes': ['Adolescentes', 'Jóvenes'], 'Jóvenes': ['Adolescentes', 'Jóvenes']}
    FOCUS_MAP = {'Niños': 'kids', 'Adolescentes': 'teens', 'Jóvenes': 'youth', 'Caballeros': 'men', 'Damas': 'women'}

    ministry_reports = []
    target_groups = ['Niños', 'Adolescentes', 'Jóvenes', 'Damas', 'Caballeros']

    for name in target_groups:
        source_mins = MERGE_GROUPS.get(name, [name])
        focus = FOCUS_MAP.get(name)
        if not focus: continue
        
        m_base = db.session.query(
            func.count(AttendanceRecord.id).label('service_count'),
            func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total_attn'),
            func.sum(getattr(AttendanceRecord, str(focus))).label('focus_attn')
        ).filter(extract('year', AttendanceRecord.date) == year, extract('month', AttendanceRecord.date) == month,
                 AttendanceRecord.ministry_of_service.in_(source_mins)).first()
        
        global_stats = db.session.query(
            func.sum(getattr(AttendanceRecord, str(focus))).label('total_attn'),
            func.sum(getattr(AttendanceRecord, f'converts_{focus}')).label('total_conv'),
            func.sum(getattr(AttendanceRecord, f'visits_{focus}')).label('total_visits'),
            func.sum(getattr(AttendanceRecord, f'testimonies_{focus}')).label('total_test')
        ).filter(extract('year', AttendanceRecord.date) == year, extract('month', AttendanceRecord.date) == month).first()

        dom_attn = db.session.query(func.sum(getattr(AttendanceRecord, str(focus)))).filter(
            extract('year', AttendanceRecord.date) == year, extract('month', AttendanceRecord.date) == month,
            AttendanceRecord.day_category == 'Dominical').scalar() or 0

        rec_map = {'kids': 'reconciled_kids', 'teens': 'reconciled_teens', 'youth': 'reconciled_youth', 'women': 'reconciled_women', 'men': 'reconciled_men'}
        total_rec = db.session.query(func.sum(getattr(AttendanceRecord, str(rec_map.get(focus, 'reconciled_kids'))))).filter(
            extract('year', AttendanceRecord.date) == year, extract('month', AttendanceRecord.date) == month).scalar() or 0

        ministry_reports.append({
            'name': name, 'services': m_base.service_count if m_base else 0,
            'total_attn': m_base.total_attn or 0 if m_base else 0,
            'focus_attn': m_base.focus_attn or 0 if m_base else 0,
            'dom_attn': dom_attn,
            'converts': global_stats.total_conv or 0 if global_stats else 0,
            'reconciled': total_rec, 'visits': global_stats.total_visits or 0 if global_stats else 0,
            'testimonies': global_stats.total_test or 0 if global_stats else 0
        })

    records = AttendanceRecord.query.filter(extract('year', AttendanceRecord.date) == year, 
                                            extract('month', AttendanceRecord.date) == month).order_by(AttendanceRecord.date.desc()).all()

    return render_template('reports.html', gen_church=gen_church, ministry_reports=ministry_reports, 
                          selected_month=month_filter, records=records, user_role=session.get('role'), username=session.get('username'))

@app.route('/stats')
@login_required
def stats_view():
    return redirect(url_for('stats_annual_view'))

@app.route('/details')
@login_required
def details_view():
    month_filter = request.args.get('month') or datetime.now().strftime('%Y-%m')
    year, month = map(int, month_filter.split('-'))
    
    records = AttendanceRecord.query.filter(
        extract('year', AttendanceRecord.date) == year,
        extract('month', AttendanceRecord.date) == month
    ).order_by(AttendanceRecord.date.desc()).all()
    
    # Pre-calculate percentages for each record to make template cleaner
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    for r in records:
        r.weekday_name = dias[r.date.weekday()]
        total = r.kids + r.teens + r.youth + r.women + r.men
        r.pct = {
            'kids': round((r.kids / total * 100), 1) if total > 0 else 0,
            'teens': round((r.teens / total * 100), 1) if total > 0 else 0,
            'youth': round((r.youth / total * 100), 1) if total > 0 else 0,
            'women': round((r.women / total * 100), 1) if total > 0 else 0,
            'men': round((r.men / total * 100), 1) if total > 0 else 0
        }
        r.total_attn = total

    return render_template('details.html', records=records, selected_month=month_filter, user_role=session.get('role'), username=session.get('username'))

@app.route('/stats/annual')
@login_required
def stats_annual_view():
    year = int(request.args.get('year') or datetime.now().year)
    
    # Aggregate by Month and DayCategory
    # 1. Weekly data
    weekly_res = db.session.query(
        extract('month', AttendanceRecord.date).label('month'),
        func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total')
    ).filter(
        extract('year', AttendanceRecord.date) == year,
        AttendanceRecord.day_category == 'Semana'
    ).group_by(extract('month', AttendanceRecord.date)).all()
    
    # 2. Sunday data
    sunday_res = db.session.query(
        extract('month', AttendanceRecord.date).label('month'),
        func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total')
    ).filter(
        extract('year', AttendanceRecord.date) == year,
        AttendanceRecord.day_category == 'Dominical'
    ).group_by(extract('month', AttendanceRecord.date)).all()

    # Prepare 12-month arrays
    semanal_data = [0] * 12
    dominical_data = [0] * 12
    
    for r in weekly_res:
        m = int(r.month)
        if 1 <= m <= 12:
            semanal_data[m-1] = r.total or 0
            
    for r in sunday_res:
        m = int(r.month)
        if 1 <= m <= 12:
            dominical_data[m-1] = r.total or 0
            
    return render_template('stats.html', 
                           mode='annual',
                           selected_year=year,
                           semanal_data=semanal_data,
                           dominical_data=dominical_data, 
                           user_role=session.get('role'), 
                           username=session.get('username'))

@app.route('/about')
@login_required
def about_view():
    return render_template('about.html', user_role=session.get('role'), username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
