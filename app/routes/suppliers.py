from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.models import db, Supplier
from app.utils.decorators import stock_manager_required
from app.utils.audit import log_audit

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
def index():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def create():
    if request.method == 'POST':
        nit_ruc = request.form.get('nit_ruc', '').strip()
        name = request.form.get('name', '').strip()
        contact_name = request.form.get('contact_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()

        if Supplier.query.filter_by(nit_ruc=nit_ruc).first():
            flash(f"El NIT/RUC '{nit_ruc}' ya se encuentra registrado.", 'danger')
            return redirect(url_for('suppliers.create'))

        supplier = Supplier(
            nit_ruc=nit_ruc,
            name=name,
            contact_name=contact_name,
            phone=phone,
            email=email,
            address=address,
            city=city
        )
        db.session.add(supplier)
        db.session.commit()
        log_audit('CREAR', 'Proveedores', f"Registrado proveedor {name} (NIT: {nit_ruc})")
        flash(f"Proveedor '{name}' creado correctamente.", 'success')
        return redirect(url_for('suppliers.index'))

    return render_template('suppliers/form.html', supplier=None)

@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
@stock_manager_required
def edit(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        supplier.name = request.form.get('name', '').strip()
        supplier.contact_name = request.form.get('contact_name', '').strip()
        supplier.phone = request.form.get('phone', '').strip()
        supplier.email = request.form.get('email', '').strip()
        supplier.address = request.form.get('address', '').strip()
        supplier.city = request.form.get('city', '').strip()
        supplier.active = bool(request.form.get('active'))

        db.session.commit()
        log_audit('ACTUALIZAR', 'Proveedores', f"Actualizado proveedor {supplier.name}")
        flash(f"Proveedor '{supplier.name}' actualizado.", 'success')
        return redirect(url_for('suppliers.index'))

    return render_template('suppliers/form.html', supplier=supplier)
