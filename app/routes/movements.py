from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import db, Product, InventoryMovement
from app.utils.decorators import stock_manager_required
from app.utils.kardex import register_movement
from app.utils.audit import log_audit

movements_bp = Blueprint('movements', __name__, url_prefix='/movements')

@movements_bp.route('/')
@login_required
def index():
    mov_type = request.args.get('type')
    product_id = request.args.get('product_id', type=int)

    query = InventoryMovement.query
    if mov_type:
        query = query.filter(InventoryMovement.movement_type == mov_type)
    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)

    movements = query.order_by(InventoryMovement.created_at.desc()).limit(150).all()
    products = Product.query.order_by(Product.name).all()

    return render_template(
        'movements/index.html',
        movements=movements,
        products=products,
        current_type=mov_type,
        current_product=product_id
    )

@movements_bp.route('/exit', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def stock_exit():
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', type=int)
        exit_type = request.form.get('exit_type', 'salida_venta')
        reference_doc = request.form.get('reference_doc', '').strip()
        notes = request.form.get('notes', '').strip()

        try:
            mov = register_movement(
                product_id=product_id,
                movement_type=exit_type,
                quantity=quantity,
                reference_doc=reference_doc,
                notes=notes,
                user_id=current_user.id
            )
            db.session.commit()
            log_audit('SALIDA', 'Inventario', f"Despacho de {quantity} un de {mov.product.sku}. Ref: {reference_doc}")
            flash(f"Salida de {quantity} unidades de '{mov.product.name}' registrada correctamente.", 'success')
            return redirect(url_for('movements.index'))
        except ValueError as e:
            flash(str(e), 'danger')

    products = Product.query.filter(Product.current_stock > 0).order_by(Product.name).all()
    return render_template('movements/exit.html', products=products)

@movements_bp.route('/adjust', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def stock_adjust():
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        adjust_type = request.form.get('adjust_type') # ajuste_positivo, ajuste_negativo
        quantity = request.form.get('quantity', type=int)
        reference_doc = request.form.get('reference_doc', '').strip()
        notes = request.form.get('notes', '').strip()

        if not notes:
            flash('Es obligatorio indicar el motivo/justificación del ajuste.', 'danger')
            return redirect(url_for('movements.stock_adjust'))

        try:
            mov = register_movement(
                product_id=product_id,
                movement_type=adjust_type,
                quantity=quantity,
                reference_doc=reference_doc or 'AJUSTE-MANUAL',
                notes=notes,
                user_id=current_user.id
            )
            db.session.commit()
            log_audit('AJUSTE', 'Inventario', f"Ajuste {adjust_type} por {quantity} un en {mov.product.sku}. Motivo: {notes}")
            flash(f"Ajuste registrado con éxito para '{mov.product.name}'.", 'success')
            return redirect(url_for('movements.index'))
        except ValueError as e:
            flash(str(e), 'danger')

    products = Product.query.order_by(Product.name).all()
    return render_template('movements/adjust.html', products=products)
