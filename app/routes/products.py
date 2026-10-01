import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.models import db, Product, Category, Brand, Location, InventoryMovement
from app.utils.decorators import stock_manager_required
from app.utils.audit import log_audit
from app.utils.kardex import register_movement

products_bp = Blueprint('products', __name__, url_prefix='/products')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@products_bp.route('/')
@login_required
def index():
    filter_type = request.args.get('filter', 'all')
    category_id = request.args.get('category_id', type=int)

    query = Product.query
    if filter_type == 'low':
        query = query.filter(Product.current_stock <= Product.min_stock)
    elif filter_type == 'out':
        query = query.filter(Product.current_stock <= 0)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        'products/index.html',
        products=products,
        categories=categories,
        current_filter=filter_type,
        current_category=category_id
    )

@products_bp.route('/<int:product_id>')
@login_required
def detail(product_id):
    product = Product.query.get_or_404(product_id)
    movements = product.movements.order_by(InventoryMovement.created_at.desc()).limit(50).all()
    return render_template('products/detail.html', product=product, movements=movements)

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def create():
    if request.method == 'POST':
        sku = request.form.get('sku', '').strip()
        barcode = request.form.get('barcode', '').strip() or None
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        oem_ref = request.form.get('oem_reference', '').strip()
        category_id = request.form.get('category_id', type=int)
        brand_id = request.form.get('brand_id', type=int) or None
        location_id = request.form.get('location_id', type=int) or None
        unit_measure = request.form.get('unit_measure', 'UN')
        min_stock = request.form.get('min_stock', type=int) or 5
        max_stock = request.form.get('max_stock', type=int) or 100
        cost_price = request.form.get('cost_price', type=float) or 0.0
        sale_price = request.form.get('sale_price', type=float) or 0.0
        initial_stock = request.form.get('initial_stock', type=int) or 0

        # Check SKU uniqueness
        if Product.query.filter_by(sku=sku).first():
            flash(f"El código SKU '{sku}' ya está registrado.", 'danger')
            return redirect(url_for('products.create'))

        # Image upload
        image_filename = 'default_part.png'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                safe_name = secure_filename(f"{sku}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name))
                image_filename = safe_name

        product = Product(
            sku=sku,
            barcode=barcode,
            name=name,
            description=description,
            oem_reference=oem_ref,
            category_id=category_id,
            brand_id=brand_id,
            location_id=location_id,
            unit_measure=unit_measure,
            min_stock=min_stock,
            max_stock=max_stock,
            current_stock=0, # Updated via initial movement
            cost_price=cost_price,
            sale_price=sale_price,
            image_path=image_filename
        )
        db.session.add(product)
        db.session.flush()

        if initial_stock > 0:
            register_movement(
                product_id=product.id,
                movement_type='ajuste_positivo',
                quantity=initial_stock,
                unit_cost=cost_price,
                reference_doc='INVENTARIO-INICIAL',
                notes='Carga de inventario inicial',
                user_id=current_user.id
            )

        db.session.commit()
        log_audit('CREAR', 'Repuestos', f"Se creó el repuesto {product.sku} - {product.name}")
        flash(f"Repuesto '{product.name}' registrado exitosamente.", 'success')
        return redirect(url_for('products.detail', product_id=product.id))

    categories = Category.query.order_by(Category.name).all()
    brands = Brand.query.order_by(Brand.name).all()
    locations = Location.query.all()
    return render_template('products/form.html', product=None, categories=categories, brands=brands, locations=locations)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.barcode = request.form.get('barcode', '').strip() or None
        product.oem_reference = request.form.get('oem_reference', '').strip()
        product.description = request.form.get('description', '').strip()
        product.category_id = request.form.get('category_id', type=int)
        product.brand_id = request.form.get('brand_id', type=int) or None
        product.location_id = request.form.get('location_id', type=int) or None
        product.unit_measure = request.form.get('unit_measure', 'UN')
        product.min_stock = request.form.get('min_stock', type=int) or 5
        product.max_stock = request.form.get('max_stock', type=int) or 100
        product.sale_price = request.form.get('sale_price', type=float) or 0.0

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                safe_name = secure_filename(f"{product.sku}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name))
                product.image_path = safe_name

        db.session.commit()
        log_audit('ACTUALIZAR', 'Repuestos', f"Se actualizó la información de {product.sku}")
        flash(f"Repuesto '{product.name}' actualizado.", 'success')
        return redirect(url_for('products.detail', product_id=product.id))

    categories = Category.query.order_by(Category.name).all()
    brands = Brand.query.order_by(Brand.name).all()
    locations = Location.query.all()
    return render_template('products/form.html', product=product, categories=categories, brands=brands, locations=locations)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
@stock_manager_required
def delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.current_stock > 0:
        flash(f"No se puede eliminar un artículo con existencias activas ({product.current_stock} un). Realice una salida o ajuste primero.", 'danger')
        return redirect(url_for('products.detail', product_id=product.id))
    
    sku = product.sku
    name = product.name
    db.session.delete(product)
    db.session.commit()
    log_audit('ELIMINAR', 'Repuestos', f"Se eliminó el repuesto {sku} - {name}")
    flash(f"Repuesto '{name}' eliminado del catálogo.", 'info')
    return redirect(url_for('products.index'))

@products_bp.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    products = Product.query.filter(
        (Product.name.ilike(f'%{q}%')) |
        (Product.sku.ilike(f'%{q}%')) |
        (Product.barcode.ilike(f'%{q}%')) |
        (Product.oem_reference.ilike(f'%{q}%'))
    ).limit(15).all()

    return jsonify([{
        'id': p.id,
        'sku': p.sku,
        'name': p.name,
        'stock': p.current_stock,
        'unit': p.unit_measure,
        'cost': p.cost_price,
        'sale_price': p.sale_price,
        'location': p.location.full_location if p.location else 'Sin ubicación'
    } for p in products])
