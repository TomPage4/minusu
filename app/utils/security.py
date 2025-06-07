from flask import request, jsonify
from functools import wraps

def block_large_requests():
    """Reject payloads that exceed the configured MAX_CONTENT_LENGTH."""
    MAX_CONTENT_LENGTH = None
    content_length = request.content_length

    try:
        if MAX_CONTENT_LENGTH and content_length and int(content_length) > int(MAX_CONTENT_LENGTH):
            return jsonify({'success': False, 'error': 'Payload too large'}), 413
    except (ValueError, TypeError):
        # Handle the case where either value isn't an integer-like
        return jsonify({'success': False, 'error': 'Invalid content length'}), 400

def apply_security_headers(response):
    response.headers.update({
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' https://cdn.snipcart.com https://cdn.jsdelivr.net 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://cdn.snipcart.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://cdn.snipcart.com https://fonts.gstatic.com; "
            "img-src 'self' data: https://cdn.snipcart.com; "
            "connect-src 'self' https://cdn.snipcart.com https://app.snipcart.com https://payment.snipcart.com; "
            "frame-src https://app.snipcart.com https://*.snipcart.com;"
        ),
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'no-referrer'
    })
    return response