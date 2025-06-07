from flask import Blueprint, render_template, send_from_directory, redirect, url_for
from app.admin.helpers import load_content

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    content=load_content()
    return render_template('index.html', content=content['home'])

@main_bp.route('/home')
def redirect_home():
    return redirect(url_for('main.home'))

@main_bp.route('/about')
def about():
    content=load_content()
    return render_template('about.html', content=content['about'])

@main_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@main_bp.route('/terms-of-service')
def terms_of_service():
    return render_template('terms-of-service.html')

@main_bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

@main_bp.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')