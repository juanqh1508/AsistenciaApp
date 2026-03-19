from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, AttendanceRecord
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

MINISTRIES = ["Niños", "Damas", "Intercesión", "Adolescentes y Jóvenes", "Caballeros", "Alabanza", "Evangelismo", "General", "Familia", "Águilas"]
SERVICE_TYPES = ["Local", "Zona", "Provincial", "Nacional"]
SHIFTS = ["Mañana", "Tarde", "Noche"]

@app.route('/')
def index():
    return render_template('index.html', ministries=MINISTRIES, service_types=SERVICE_TYPES, shifts=SHIFTS)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    date_str = data.get('date')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    
    record = AttendanceRecord(
        date=date_obj,
        ministry_of_service=data.get('ministry_of_service'),
        service_type=data.get('service_type'),
        shift=data.get('shift'),
        kids=int(data.get('kids', 0)),
        teens=int(data.get('teens', 0)),
        youth=int(data.get('youth', 0)),
        women=int(data.get('women', 0)),
        men=int(data.get('men', 0)),
        visits=int(data.get('visits', 0)),
        testimonies=int(data.get('testimonies', 0)),
        converts_total=int(data.get('converts_total', 0)),
        converts_kids=int(data.get('converts_kids', 0)),
        converts_teens=int(data.get('converts_teens', 0)),
        converts_youth=int(data.get('converts_youth', 0)),
        converts_men=int(data.get('converts_men', 0)),
        converts_women=int(data.get('converts_women', 0)),
        reconciled_kids=int(data.get('reconciled_kids', 0)),
        reconciled_teens=int(data.get('reconciled_teens', 0)),
        reconciled_youth=int(data.get('reconciled_youth', 0)),
        reconciled_men=int(data.get('reconciled_men', 0)),
        reconciled_women=int(data.get('reconciled_women', 0))
    )
    
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('reports'))

from sqlalchemy import func, extract

@app.route('/reports')
def reports():
    # Filter by search params if provided (Ministry or Month)
    ministry_filter = request.args.get('ministry')
    month_filter = request.args.get('month') # expected YYYY-MM
    
    query = AttendanceRecord.query
    if ministry_filter:
        query = query.filter(AttendanceRecord.ministry_of_service == ministry_filter)
    if month_filter:
        year, month = map(int, month_filter.split('-'))
        query = query.filter(extract('year', AttendanceRecord.date) == year, 
                             extract('month', AttendanceRecord.date) == month)
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    
    # Aggregates for "General Report" (all records in query)
    total_stats = db.session.query(
        func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total_attn'),
        func.sum(AttendanceRecord.visits).label('total_visits'),
        func.sum(AttendanceRecord.converts_total).label('total_converts'),
        func.sum(AttendanceRecord.reconciled_kids + AttendanceRecord.reconciled_teens + AttendanceRecord.reconciled_youth + AttendanceRecord.reconciled_men + AttendanceRecord.reconciled_women).label('total_reconciled')
    ).filter(AttendanceRecord.id.in_([r.id for r in records])).first() if records else None

    # Per-Ministry Monthly Summary (if month is selected)
    ministry_summaries = []
    if month_filter:
        year, month = map(int, month_filter.split('-'))
        for min_name in MINISTRIES:
            m_stats = db.session.query(
                func.sum(AttendanceRecord.kids + AttendanceRecord.teens + AttendanceRecord.youth + AttendanceRecord.women + AttendanceRecord.men).label('total_attn'),
                func.sum(AttendanceRecord.converts_total).label('total_converts'),
                func.count(AttendanceRecord.id).label('service_count')
            ).filter(
                extract('year', AttendanceRecord.date) == year,
                extract('month', AttendanceRecord.date) == month,
                AttendanceRecord.ministry_of_service == min_name
            ).first()
            if m_stats and m_stats.service_count > 0:
                ministry_summaries.append({
                    'name': min_name,
                    'total_attn': m_stats.total_attn or 0,
                    'total_converts': m_stats.total_converts or 0,
                    'services': m_stats.service_count
                })

    return render_template('reports.html', 
                          records=records, 
                          total_stats=total_stats, 
                          ministries=MINISTRIES,
                          selected_min=ministry_filter,
                          selected_month=month_filter,
                          ministry_summaries=ministry_summaries)

@app.route('/api/stats')
def stats():
    # Monthly and by ministry stats
    # For now, just return all as JSON for the charts if needed
    records = AttendanceRecord.query.all()
    return jsonify([r.to_dict() for r in records])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
