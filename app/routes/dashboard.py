from flask import Blueprint, render_template
from flask_login import login_required
from app.models.models import Product, InventoryMovement, Category, Supplier, PurchaseOrder
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    total_products = Product.query.count()
    low_stock_products = Product.query.filter(Product.current_stock <= Product.min_stock).all()
    out_of_stock_count = Product.query.filter(Product.current_stock <= 0).count()
    
    # Total valuation
    products = Product.query.all()
    total_valuation = sum((p.current_stock or 0) * (p.cost_price or 0.0) for p in products)
    total_items = sum(p.current_stock or 0 for p in products)
    
    recent_movements = InventoryMovement.query.order_by(InventoryMovement.created_at.desc()).limit(8).all()
    pending_purchases = PurchaseOrder.query.filter_by(status='aprobada').count()

    # Category chart data
    categories = Category.query.all()
    cat_labels = [c.name for c in categories]
    cat_counts = [len(c.products) for c in categories]

    # Movements distribution
    movements_summary = db.session.query(
        InventoryMovement.movement_type, 
        func.count(InventoryMovement.id)
    ).group_by(InventoryMovement.movement_type).all()
    
    mov_labels = [m[0].replace('_', ' ').title() for m in movements_summary]
    mov_counts = [m[1] for m in movements_summary]

    return render_template(
        'dashboard/index.html',
        total_products=total_products,
        low_stock_count=len(low_stock_products),
        out_of_stock_count=out_of_stock_count,
        total_valuation=total_valuation,
        total_items=total_items,
        recent_movements=recent_movements,
        low_stock_products=low_stock_products[:5],
        pending_purchases=pending_purchases,
        cat_labels=cat_labels,
        cat_counts=cat_counts,
        mov_labels=mov_labels,
        mov_counts=mov_counts
    )
from app.models.models import db
