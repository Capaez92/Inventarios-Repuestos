import os
import sys
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

def migrate():
    print("=======================================================")
    print("  Migrador de Datos: SQLite -> Supabase (PostgreSQL)")
    print("=======================================================\n")

    target_url = os.environ.get('DATABASE_URL')
    if not target_url or 'sqlite' in target_url:
        print("[!] ERROR: No se encontró una DATABASE_URL de Supabase/PostgreSQL configurada en el archivo .env")
        print("    Asegúrate de agregar en tu archivo .env la línea:")
        print("    DATABASE_URL=postgresql://postgres.xxx:password@aws-0-xx.pooler.supabase.com:6543/postgres\n")
        return

    print(f"[*] Conectando a Supabase con la URL configurada...")

    from app import create_app
    from app.models.models import (
        db, User, CompanySetting, Category, Brand, Location, 
        Supplier, Product, PurchaseOrder, PurchaseItem, 
        InventoryMovement, AuditLog
    )
    import sqlite3

    sqlite_path = os.path.join(os.path.dirname(__file__), 'instance', 'inventarios.db')
    if not os.path.exists(sqlite_path):
        print(f"[!] No se encontró el archivo local SQLite en {sqlite_path}")
        return

    # Iniciar contexto con la base de datos destino (Supabase)
    app = create_app()
    with app.app_context():
        print("[*] Creando estructura de tablas en Supabase...")
        db.create_all()
        print("[+] Estructura de tablas lista en Supabase.")

        # Conectar a SQLite origen
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Company Setting
        cursor.execute("SELECT * FROM company_settings")
        for row in cursor.fetchall():
            if not CompanySetting.query.get(row['id']):
                c = CompanySetting(
                    id=row['id'], company_name=row['company_name'], nit=row['nit'],
                    phone=row['phone'], email=row['email'], address=row['address'],
                    currency_symbol=row['currency_symbol'], logo_path=row['logo_path']
                )
                db.session.merge(c)
        db.session.commit()
        print("[+] Configuración de empresa sincronizada.")

        # 2. Categories
        cursor.execute("SELECT * FROM categories")
        for row in cursor.fetchall():
            if not Category.query.filter_by(code=row['code']).first():
                c = Category(id=row['id'], code=row['code'], name=row['name'], description=row['description'])
                db.session.merge(c)
        db.session.commit()
        print("[+] Categorías sincronizadas.")

        # 3. Brands
        cursor.execute("SELECT * FROM brands")
        for row in cursor.fetchall():
            if not Brand.query.filter_by(name=row['name']).first():
                b = Brand(id=row['id'], name=row['name'], country=row['country'], description=row['description'])
                db.session.merge(b)
        db.session.commit()
        print("[+] Marcas sincronizadas.")

        # 4. Locations
        cursor.execute("SELECT * FROM locations")
        for row in cursor.fetchall():
            if not Location.query.get(row['id']):
                loc = Location(
                    id=row['id'], name=row['name'], aisle=row['aisle'],
                    shelf=row['shelf'], bin=row['bin'], description=row['description']
                )
                db.session.merge(loc)
        db.session.commit()
        print("[+] Ubicaciones sincronizadas.")

        # 5. Suppliers
        cursor.execute("SELECT * FROM suppliers")
        for row in cursor.fetchall():
            if not Supplier.query.filter_by(nit_ruc=row['nit_ruc']).first():
                s = Supplier(
                    id=row['id'], nit_ruc=row['nit_ruc'], name=row['name'],
                    contact_name=row['contact_name'], phone=row['phone'],
                    email=row['email'], address=row['address'], city=row['city'],
                    active=bool(row['active'])
                )
                db.session.merge(s)
        db.session.commit()
        print("[+] Proveedores sincronizados.")

        # 6. Users
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            if not User.query.filter_by(username=row['username']).first():
                u = User(
                    id=row['id'], username=row['username'], password_hash=row['password_hash'],
                    full_name=row['full_name'], email=row['email'], role=row['role'],
                    active=bool(row['active'])
                )
                db.session.merge(u)
        db.session.commit()
        print("[+] Usuarios sincronizados.")

        # 7. Products
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            if not Product.query.filter_by(sku=row['sku']).first():
                p = Product(
                    id=row['id'], sku=row['sku'], barcode=row['barcode'],
                    oem_reference=row['oem_reference'], name=row['name'],
                    description=row['description'], category_id=row['category_id'],
                    brand_id=row['brand_id'], location_id=row['location_id'],
                    unit_measure=row['unit_measure'], min_stock=row['min_stock'],
                    max_stock=row['max_stock'], current_stock=row['current_stock'],
                    cost_price=row['cost_price'], sale_price=row['sale_price'],
                    image_path=row['image_path'], status=row['status']
                )
                db.session.merge(p)
        db.session.commit()
        print("[+] Catálogo de productos sincronizado.")

        # 8. Purchase Orders & Items
        cursor.execute("SELECT * FROM purchase_orders")
        for row in cursor.fetchall():
            if not PurchaseOrder.query.filter_by(order_number=row['order_number']).first():
                po = PurchaseOrder(
                    id=row['id'], order_number=row['order_number'], supplier_id=row['supplier_id'],
                    status=row['status'], total_amount=row['total_amount'], notes=row['notes'],
                    created_by_id=row['created_by_id']
                )
                db.session.merge(po)
        db.session.commit()

        cursor.execute("SELECT * FROM purchase_items")
        for row in cursor.fetchall():
            if not PurchaseItem.query.get(row['id']):
                pi = PurchaseItem(
                    id=row['id'], purchase_id=row['purchase_id'], product_id=row['product_id'],
                    quantity=row['quantity'], unit_cost=row['unit_cost'],
                    total_cost=row['total_cost'], received_qty=row['received_qty']
                )
                db.session.merge(pi)
        db.session.commit()
        print("[+] Órdenes de compra sincronizadas.")

        # 9. Inventory Movements (Kardex)
        cursor.execute("SELECT * FROM inventory_movements")
        for row in cursor.fetchall():
            if not InventoryMovement.query.get(row['id']):
                im = InventoryMovement(
                    id=row['id'], movement_type=row['movement_type'], product_id=row['product_id'],
                    quantity=row['quantity'], previous_stock=row['previous_stock'],
                    new_stock=row['new_stock'], unit_cost=row['unit_cost'],
                    reference_doc=row['reference_doc'], notes=row['notes'],
                    created_by_id=row['created_by_id']
                )
                db.session.merge(im)
        db.session.commit()
        print("[+] Movimientos de Kárdex sincronizados.")

        # 10. Audit Logs
        cursor.execute("SELECT * FROM audit_logs")
        for row in cursor.fetchall():
            if not AuditLog.query.get(row['id']):
                al = AuditLog(
                    id=row['id'], user_id=row['user_id'], action=row['action'],
                    module=row['module'], details=row['details'], ip_address=row['ip_address']
                )
                db.session.merge(al)
        db.session.commit()
        print("[+] Bitácora de auditoría sincronizada.")

        # Ajustar secuencias en PostgreSQL
        try:
            from sqlalchemy import text
            tables = [
                ('users', 'id'), ('company_settings', 'id'), ('categories', 'id'),
                ('brands', 'id'), ('locations', 'id'), ('suppliers', 'id'),
                ('products', 'id'), ('purchase_orders', 'id'), ('purchase_items', 'id'),
                ('inventory_movements', 'id'), ('audit_logs', 'id')
            ]
            for table, col in tables:
                db.session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), coalesce(max({col}), 1)) FROM {table};"))
            db.session.commit()
            print("[+] Secuencias e IDs autoincrementables sincronizados.")
        except Exception as e:
            print(f"[*] Ajuste de secuencias omitido o no requerido: {e}")

        conn.close()
        print("\n=======================================================")
        print("  ¡MIGRACIÓN A SUPABASE COMPLETADA EXITOSAMENTE!")
        print("=======================================================\n")

if __name__ == '__main__':
    migrate()
