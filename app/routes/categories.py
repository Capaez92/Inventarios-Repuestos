from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.models import db, Category, Brand, Location
from app.utils.decorators import stock_manager_required
from app.utils.audit import log_audit

categories_bp = Blueprint('categories', __name__, url_prefix='/catalogs')

@categories_bp.route('/')
@login_required
def index():
    categories = Category.query.order_by(Category.name).all()
    brands = Brand.query.order_by(Brand.name).all()
    locations = Location.query.order_by(Location.name).all()
    return render_template('categories/index.html', categories=categories, brands=brands, locations=locations)

@categories_bp.route('/category/add', methods=['POST'])
@login_required
@stock_manager_required
def add_category():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if Category.query.filter_by(code=code).first():
        flash(f"El código de categoría '{code}' ya existe.", 'danger')
        return redirect(url_for('categories.index'))

    cat = Category(code=code, name=name, description=description)
    db.session.add(cat)
    db.session.commit()
    log_audit('CREAR', 'Categorías', f"Nueva categoría: {name} ({code})")
    flash(f"Categoría '{name}' creada con éxito.", 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/brand/add', methods=['POST'])
@login_required
@stock_manager_required
def add_brand():
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()
    description = request.form.get('description', '').strip()

    if Brand.query.filter_by(name=name).first():
        flash(f"La marca '{name}' ya existe.", 'warning')
        return redirect(url_for('categories.index'))

    brand = Brand(name=name, country=country, description=description)
    db.session.add(brand)
    db.session.commit()
    log_audit('CREAR', 'Marcas', f"Nueva marca: {name}")
    flash(f"Marca '{name}' agregada.", 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/location/add', methods=['POST'])
@login_required
@stock_manager_required
def add_location():
    name = request.form.get('name', '').strip()
    aisle = request.form.get('aisle', '').strip()
    shelf = request.form.get('shelf', '').strip()
    bin_pos = request.form.get('bin', '').strip()
    description = request.form.get('description', '').strip()

    loc = Location(name=name, aisle=aisle, shelf=shelf, bin=bin_pos, description=description)
    db.session.add(loc)
    db.session.commit()
    log_audit('CREAR', 'Ubicaciones', f"Nueva ubicación: {loc.full_location}")
    flash(f"Ubicación '{loc.full_location}' registrada.", 'success')
    return redirect(url_for('categories.index'))
