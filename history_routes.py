"""
Routes for prediction history, tracking, trend analysis, and data export
"""

from flask import Blueprint, render_template, request, jsonify, send_file, session
from flask_login import login_required, current_user
from models import db, PredictionHistory
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import csv
import json
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import func

history_bp = Blueprint('history', __name__, url_prefix='/history')
logger = logging.getLogger(__name__)


@history_bp.route('/')
@login_required
def view_history():
    """Display prediction history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = PredictionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(PredictionHistory.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    predictions = pagination.items
    
    # Calculate statistics
    total_predictions = PredictionHistory.query.filter_by(user_id=current_user.id).count()
    positive_count = PredictionHistory.query.filter_by(
        user_id=current_user.id, prediction=1
    ).count()
    
    avg_glucose = db.session.query(func.avg(PredictionHistory.glucose))\
        .filter_by(user_id=current_user.id).scalar() or 0
    avg_bmi = db.session.query(func.avg(PredictionHistory.bmi))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    stats = {
        'total': total_predictions,
        'positive': positive_count,
        'negative': total_predictions - positive_count,
        'avg_glucose': round(avg_glucose, 2),
        'avg_bmi': round(avg_bmi, 2)
    }
    
    return render_template('history/predictions.html',
                          predictions=predictions,
                          pagination=pagination,
                          stats=stats)


@history_bp.route('/detail/<int:prediction_id>')
@login_required
def prediction_detail(prediction_id):
    """View detailed prediction information"""
    prediction = PredictionHistory.query.filter_by(
        id=prediction_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('history/detail.html', prediction=prediction)


@history_bp.route('/trends')
@login_required
def trends():
    """Display trend analysis dashboard with visualizations"""
    predictions = PredictionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(PredictionHistory.created_at).all()
    
    if not predictions:
        return render_template('history/trends.html', chart_html='', stats={})
    
    try:
        # Prepare data for trend chart
        dates = [p.created_at.strftime('%Y-%m-%d') for p in predictions]
        glucose_values = [p.glucose or 0 for p in predictions]
        bmi_values = [p.bmi or 0 for p in predictions]
        
        # Create multi-line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates, y=glucose_values,
            mode='lines+markers',
            name='Glucose Level (mg/dL)',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates, y=bmi_values,
            mode='lines+markers',
            name='BMI (kg/m²)',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Health Metrics Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Value',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            font=dict(size=12)
        )
        
        chart_html = fig.to_html(include_plotlyjs='cdn', div_id='trend_chart')
        
        # Calculate trend statistics
        stats = {
            'total_predictions': len(predictions),
            'positive_results': sum(1 for p in predictions if p.prediction == 1),
            'avg_glucose': round(sum(glucose_values) / len(glucose_values), 2),
            'avg_bmi': round(sum(bmi_values) / len(bmi_values), 2),
            'max_glucose': max(glucose_values),
            'min_glucose': min(glucose_values),
            'max_bmi': max(bmi_values),
            'min_bmi': min(bmi_values)
        }
        
        return render_template('history/trends.html', chart_html=chart_html, stats=stats)
    
    except Exception as e:
        logger.error(f"Error generating trends: {e}")
        return render_template('history/trends.html', chart_html='', stats={})


@history_bp.route('/export/csv')
@login_required
def export_csv():
    """Export prediction history as CSV"""
    try:
        predictions = PredictionHistory.query.filter_by(user_id=current_user.id)\
            .order_by(PredictionHistory.created_at.desc()).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Date', 'Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness',
            'Insulin', 'BMI', 'DPF', 'Age', 'Prediction', 'Confidence (%)', 'Notes'
        ])
        
        # Data rows
        for pred in predictions:
            writer.writerow([
                pred.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                pred.pregnancies,
                pred.glucose,
                pred.blood_pressure,
                pred.skin_thickness,
                pred.insulin,
                pred.bmi,
                pred.dpf,
                pred.age,
                'Positive' if pred.prediction == 1 else 'Negative',
                f"{pred.confidence:.2f}",
                pred.notes or ''
            ])
        
        # Create BytesIO object
        output.seek(0)
        mem = BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        logger.info(f"CSV exported for user: {current_user.username}")
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'diabetes_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return jsonify({'error': 'Failed to export CSV'}), 500


@history_bp.route('/export/pdf')
@login_required
def export_pdf():
    """Export prediction history as PDF report"""
    try:
        predictions = PredictionHistory.query.filter_by(user_id=current_user.id)\
            .order_by(PredictionHistory.created_at.desc()).all()
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Diabetes Prediction History Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"User: {current_user.first_name} {current_user.last_name}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics
        story.append(Paragraph("Summary Statistics", heading_style))
        
        total_predictions = len(predictions)
        positive_count = sum(1 for p in predictions if p.prediction == 1)
        negative_count = total_predictions - positive_count
        
        avg_glucose = sum(p.glucose or 0 for p in predictions) / total_predictions if predictions else 0
        avg_bmi = sum(p.bmi or 0 for p in predictions) / total_predictions if predictions else 0
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Predictions', str(total_predictions)],
            ['Positive Results', str(positive_count)],
            ['Negative Results', str(negative_count)],
            ['Average Glucose (mg/dL)', f"{avg_glucose:.2f}"],
            ['Average BMI (kg/m²)', f"{avg_bmi:.2f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recent predictions
        story.append(Paragraph("Recent Predictions", heading_style))
        
        if predictions:
            pred_data = [['Date', 'Glucose', 'BMI', 'Age', 'Result', 'Confidence']]
            
            for pred in predictions[:10]:  # Last 10 predictions
                pred_data.append([
                    pred.created_at.strftime('%Y-%m-%d %H:%M'),
                    f"{pred.glucose:.1f}",
                    f"{pred.bmi:.1f}",
                    str(pred.age),
                    'Positive' if pred.prediction == 1 else 'Negative',
                    f"{pred.confidence:.1f}%"
                ])
            
            pred_table = Table(pred_data, colWidths=[1.2*inch, 0.9*inch, 0.8*inch, 0.7*inch, 1*inch, 0.8*inch])
            pred_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(pred_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"PDF exported for user: {current_user.username}")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'diabetes_predictions_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({'error': 'Failed to export PDF'}), 500


@history_bp.route('/api/data')
@login_required
def get_history_data():
    """API endpoint to get history data as JSON"""
    try:
        predictions = PredictionHistory.query.filter_by(user_id=current_user.id)\
            .order_by(PredictionHistory.created_at.desc()).all()
        
        return jsonify([pred.to_dict() for pred in predictions])
    
    except Exception as e:
        logger.error(f"History API error: {e}")
        return jsonify({'error': str(e)}), 500
