from flask import Blueprint, render_template, send_file, request
from flask_login import login_required
from app.models.models import Product, Category
from app.utils.reports import generate_inventory_excel, generate_inventory_pdf, generate_kardex_excel
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    products = Product.query.order_by(Product.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('reports/index.html', products=products, categories=categories)

@reports_bp.route('/inventory/excel')
@login_required
def inventory_excel():
    excel_stream = generate_inventory_excel()
    filename = f"Inventario_Valorizado_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

@reports_bp.route('/inventory/pdf')
@login_required
def inventory_pdf():
    pdf_stream = generate_inventory_pdf()
    filename = f"Inventario_Valorizado_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        pdf_stream,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=filename
    )

@reports_bp.route('/kardex/<int:product_id>/excel')
@login_required
def kardex_excel(product_id):
    excel_stream = generate_kardex_excel(product_id)
    product = Product.query.get_or_404(product_id)
    filename = f"Kardex_{product.sku}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )
