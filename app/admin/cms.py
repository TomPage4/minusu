import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from markupsafe import escape
from flask_login import login_required

from app.admin.helpers import (
    load_content, save_content, update_content_with_form_data,
    allowed_file, IMAGE_UPLOAD_FOLDER
)

try:
    from app.ecommerce.helpers import load_products, save_products
except ImportError:
    pass

cms_bp = Blueprint('cms', __name__)

# Max lengths for text fields
MAX_NAME_LENGTH = 255
MAX_DESC_LENGTH = 1000
MAX_CATEGORY_LENGTH = 100

def validate_price(value):
    try:
        val = float(value)
        return val if val >= 0 else None
    except (ValueError, TypeError):
        return None

def validate_text(value, max_length):
    if value and isinstance(value, str):
        return escape(value.strip())[:max_length]
    return ""

@cms_bp.route('/admin')
@login_required
def admin_dashboard():
    content = load_content()
    pages = list(content.keys())
    try:
        if load_products():
            pages.append('products')
    except:
        pass
    return render_template('admin/cms_dashboard.html', pages=pages)

@cms_bp.route('/admin/dashboard')
@login_required
def redirect_dashboard():
    return redirect(url_for('cms.admin_dashboard'))

@cms_bp.route('/admin/<page>', methods=['GET', 'POST'])
@login_required
def edit_page(page):
    content = load_content()

    if page not in content:
        flash("Invalid page.", "error")
        return redirect(url_for('cms.admin_dashboard'))

    if request.method == 'POST':
        content = update_content_with_form_data(request, content)
        save_content(content)
        flash("Page updated successfully.", "success")
        return redirect(url_for('cms.edit_page', page=page))

    return render_template('admin/cms.html', content={page: content[page]})

@cms_bp.route('/admin/products/delete/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not re.fullmatch(r'[a-z0-9\-]{6,}', product_id):
        flash("Invalid product ID.", "error")
        return redirect(...)
    products = load_products()
    products = [p for p in products if p['id'] != product_id]
    save_products(products)
    flash("Product deleted successfully.", "success")
    return redirect(url_for('cms.edit_products'))

@cms_bp.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    current_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    products = load_products()
    categories = sorted(set(p.get("category", "") for p in products if p.get("category")))

    if request.method == 'POST':
        name = validate_text(request.form.get('name'), max_length=MAX_NAME_LENGTH)
        price = validate_price(request.form.get('price'))
        description = validate_text(request.form.get('description'), max_length=MAX_DESC_LENGTH)

        if not name or price is None:
            flash("Invalid input. Please check all fields.", "error")
            return redirect(url_for('cms.add_product'))

        base_name = name.lower().replace(" ", "-")
        unique_id = f"{base_name}-{uuid.uuid4().hex[:6]}"

        category = request.form.get('category')
        if category == 'other':
            category = validate_text(request.form.get('custom_category'), max_length=MAX_CATEGORY_LENGTH)

        image_filename = ""
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            image_filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(IMAGE_UPLOAD_FOLDER, image_filename)
            file.save(file_path)

        new_product = {
            "id": unique_id,
            "name": name,
            "price": price,
            "description": description,
            "image": image_filename,
            "category": category
        }

        products.append(new_product)
        save_products(products)
        flash("Product added successfully.", "success")
        return redirect(url_for('cms.edit_products'))

    return render_template('admin/add-product.html', categories=categories)

@cms_bp.route('/admin/products', methods=['GET', 'POST'])
@login_required
def edit_products():
    current_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    products = load_products()

    if request.method == 'POST':
        for product in products:
            product_id = product['id']

            for field in ['name', 'price', 'description']:
                form_key = f"{product_id}.{field}"
                if form_key in request.form:
                    raw_value = request.form[form_key]
                    if 'price' in field:
                        try:
                            value = round(float(raw_value), 2)
                            product[field] = value
                        except ValueError:
                            flash(f"Invalid value for {field}: {raw_value}", "error")
                    else:
                        max_length = MAX_DESC_LENGTH if field == 'description' else MAX_NAME_LENGTH
                        product[field] = validate_text(raw_value, max_length=max_length)

            file_key = f"{product_id}.image"
            if file_key in request.files:
                file = request.files[file_key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower()
                    new_filename = f"{uuid.uuid4().hex}.{ext}"
                    file_path = os.path.join(IMAGE_UPLOAD_FOLDER, new_filename)
                    file.save(file_path)
                    product['image'] = new_filename

        save_products(products)
        flash("Products updated successfully.", "success")
        return redirect(url_for('cms.edit_products'))

    return render_template('admin/products.html', products=products)