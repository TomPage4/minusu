from flask import Blueprint, request, jsonify, current_app, render_template
from flask_mail import Message
from datetime import datetime
import re
import bleach

from .. import mail, limiter

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET'])
def show_contact_form():
    return render_template('contact.html')


@contact_bp.route('/contact', methods=['POST'])
@limiter.limit('3/hour')  # ⛔️ Limit only POSTs
def handle_contact_submission():
    if request.form.get('referral_code'):
        return jsonify({'success': False, 'message': 'Spam detected'}), 400

    name = bleach.clean(request.form.get('name', '').strip())
    email = bleach.clean(request.form.get('email', '').strip())
    message = bleach.clean(request.form.get('message', '').strip())

    if not name or not re.match(r"^[a-zA-Z\s'-]+$", name):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({'success': False, 'error': 'Invalid email'}), 400

    if any(char in email for char in ['\n', '\r']) or any(char in name for char in ['\n', '\r']):
        return jsonify({'success': False, 'error': 'Header injection detected'}), 400

    if not message or len(message) > 1000:
        return jsonify({'success': False, 'error': 'Invalid message'}), 400

    msg = Message(
        subject=f"New Contact from {name}",
        sender=current_app.config['MAIL_SENDER'],
        recipients=[current_app.config['MAIL_RECEIVER']],
        reply_to=email,
        body=(
            f"📥 You've received a new message from your website contact form:\n\n"
            f"🧑 Name: {name}\n"
            f"📧 Email: {email}\n"
            f"🕒 Received: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            f"💬 Message:\n"
            f"{'-' * 40}\n"
            f"{message}\n"
            f"{'-' * 40}\n"
        )
    )

    try:
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

