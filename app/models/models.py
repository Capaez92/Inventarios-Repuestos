from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), default='almacenista')  # admin, almacenista, consultor
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def can_manage_stock(self):
        return self.role in ['admin', 'almacenista']

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    country = db.Column(db.String(60))
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='brand', lazy=True)

    def __repr__(self):
        return f'<Brand {self.name}>'


class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False) # Ej: Bodega Principal
    aisle = db.Column(db.String(20)) # Pasillo
    shelf = db.Column(db.String(20)) # Estante
    bin = db.Column(db.String(20))   # Gaveta / Posición
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='location', lazy=True)

    @property
    def full_location(self):
        parts = [self.name]
        if self.aisle: parts.append(f"Pasillo {self.aisle}")
        if self.shelf: parts.append(f"Estante {self.shelf}")
        if self.bin: parts.append(f"Gaveta {self.bin}")
        return " - ".join(parts)


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    nit_ruc = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    city = db.Column(db.String(80))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchases = db.relationship('PurchaseOrder', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Supplier {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True) # Código parte
    barcode = db.Column(db.String(60), unique=True, index=True)
    oem_reference = db.Column(db.String(80)) # Referencia original OEM
    name = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    unit_measure = db.Column(db.String(20), default='UN') # UN, JGO, KIT, LT, MT
    min_stock = db.Column(db.Integer, default=5)
    max_stock = db.Column(db.Integer, default=100)
    current_stock = db.Column(db.Integer, default=0)
    
    cost_price = db.Column(db.Float, default=0.0) # Costo Promedio Ponderado
    sale_price = db.Column(db.Float, default=0.0)
    
    image_path = db.Column(db.String(255), default='default_part.png')
    status = db.Column(db.String(20), default='activo') # activo, inactivo, agotado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movements = db.relationship('InventoryMovement', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    purchase_items = db.relationship('PurchaseItem', backref='product', lazy=True)

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock

    @property
    def is_out_of_stock(self):
        return self.current_stock <= 0

    @property
    def total_cost_value(self):
        return (self.current_stock or 0) * (self.cost_price or 0.0)

    @property
    def total_sale_value(self):
        return (self.current_stock or 0) * (self.sale_price or 0.0)


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False) # Ej: OC-2026-0001
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='borrador') # borrador, aprobada, recibida, cancelada
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    received_at = db.Column(db.DateTime, nullable=True)

    created_by = db.relationship('User', foreign_keys=[created_by_id])
    items = db.relationship('PurchaseItem', backref='purchase_order', lazy=True, cascade='all, delete-orphan')


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    received_qty = db.Column(db.Integer, default=0)


class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    movement_type = db.Column(db.String(30), nullable=False) # entrada_compra, salida_venta, salida_taller, ajuste_positivo, ajuste_negativo
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    previous_stock = db.Column(db.Integer, nullable=False)
    new_stock = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0)
    reference_doc = db.Column(db.String(80)) # Factura, remisión, orden taller, etc.
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    created_by = db.relationship('User', foreign_keys=[created_by_id])


class CompanySetting(db.Model):
    __tablename__ = 'company_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), default='AutoPartes Pro - Almacén Central')
    nit = db.Column(db.String(50), default='900.123.456-7')
    phone = db.Column(db.String(50), default='+57 300 123 4567')
    email = db.Column(db.String(120), default='contacto@autopartespro.com')
    address = db.Column(db.String(200), default='Zona Industrial Principal - Manzana B Bodega 12')
    currency_symbol = db.Column(db.String(10), default='$')
    logo_path = db.Column(db.String(255), default='logo.png')


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False) # CREAR, ACTUALIZAR, ELIMINAR, ENTRADA, SALIDA
    module = db.Column(db.String(50), nullable=False) # Productos, Compras, Usuarios, etc.
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])
