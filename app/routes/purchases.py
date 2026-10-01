from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models.models import db, PurchaseOrder, PurchaseItem, Supplier, Product
from app.utils.decorators import stock_manager_required
from app.utils.kardex import register_movement
from app.utils.audit import log_audit

purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')

@purchases_bp.route('/')
@login_required
def index():
    status = request.args.get('status')
    query = PurchaseOrder.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(PurchaseOrder.order_date.desc()).all()
    return render_template('purchases/index.html', orders=orders, current_status=status)

@purchases_bp.route('/create', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def create():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', type=int)
        notes = request.form.get('notes', '').strip()
        
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        unit_costs = request.form.getlist('unit_cost[]')

        if not product_ids:
            flash('Debe agregar al menos un repuesto a la orden de compra.', 'danger')
            return redirect(url_for('purchases.create'))

        # Generate order number: OC-YYYYMMDD-XXXX
        order_count = PurchaseOrder.query.count() + 1
        order_number = f"OC-{datetime.now().strftime('%Y%m')}-{order_count:04d}"

        total_amount = 0.0
        order = PurchaseOrder(
            order_number=order_number,
            supplier_id=supplier_id,
            notes=notes,
            created_by_id=current_user.id,
            status='borrador',
            total_amount=0.0
        )
        db.session.add(order)
        db.session.flush()

        for p_id, qty, cost in zip(product_ids, quantities, unit_costs):
            if not p_id or not qty or not cost:
                continue
            qty = int(qty)
            cost = float(cost)
            if qty > 0 and cost >= 0:
                item_total = qty * cost
                total_amount += item_total
                item = PurchaseItem(
                    purchase_id=order.id,
                    product_id=int(p_id),
                    quantity=qty,
                    unit_cost=cost,
                    total_cost=item_total
                )
                db.session.add(item)

        order.total_amount = round(total_amount, 2)
        db.session.commit()

        log_audit('CREAR', 'Compras', f"Creada orden de compra {order.order_number} por valor de ${order.total_amount:,.2f}")
        flash(f"Orden de compra {order.order_number} registrada en estado Borrador.", 'success')
        return redirect(url_for('purchases.detail', order_id=order.id))

    suppliers = Supplier.query.filter_by(active=True).order_by(Supplier.name).all()
    products = Product.query.order_by(Product.name).all()
    return render_template('purchases/create.html', suppliers=suppliers, products=products)

@purchases_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchases/detail.html', order=order)

@purchases_bp.route('/<int:order_id>/approve', methods=['POST'])
@login_required
@stock_manager_required
def approve(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status != 'borrador':
        flash('Solo se pueden aprobar órdenes en estado Borrador.', 'warning')
        return redirect(url_for('purchases.detail', order_id=order.id))

    order.status = 'aprobada'
    db.session.commit()
    log_audit('APROBAR', 'Compras', f"Orden {order.order_number} aprobada")
    flash(f"Orden {order.order_number} aprobada. Lista para recepción en bodega.", 'success')
    return redirect(url_for('purchases.detail', order_id=order.id))

@purchases_bp.route('/<int:order_id>/receive', methods=['POST'])
@login_required
@stock_manager_required
def receive(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status not in ['aprobada', 'borrador']:
        flash('Esta orden ya fue procesada o está cancelada.', 'warning')
        return redirect(url_for('purchases.detail', order_id=order.id))

    # Ingress each product into inventory
    for item in order.items:
        register_movement(
            product_id=item.product_id,
            movement_type='entrada_compra',
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            reference_doc=order.order_number,
            notes=f"Recepción de compra Proveedor: {order.supplier.name}",
            user_id=current_user.id
        )
        item.received_qty = item.quantity

    order.status = 'recibida'
    order.received_at = datetime.utcnow()
    db.session.commit()

    log_audit('RECEPCION', 'Compras', f"Recepción de mercancía orden {order.order_number}. Stock actualizado.")
    flash(f"¡Mercancía de la orden {order.order_number} ingresada al inventario satisfactoriamente!", 'success')
    return redirect(url_for('purchases.detail', order_id=order.id))

@purchases_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
@stock_manager_required
def cancel(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status == 'recibida':
        flash('No se puede cancelar una orden cuya mercancía ya fue recibida.', 'danger')
        return redirect(url_for('purchases.detail', order_id=order.id))

    order.status = 'cancelada'
    db.session.commit()
    log_audit('CANCELAR', 'Compras', f"Cancelada orden de compra {order.order_number}")
    flash(f"Orden {order.order_number} cancelada.", 'info')
    return redirect(url_for('purchases.detail', order_id=order.id))
