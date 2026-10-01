from app import create_app
from app.models.models import (
    db, User, CompanySetting, Category, Brand, Location, 
    Supplier, Product, PurchaseOrder, PurchaseItem
)
from app.utils.kardex import register_movement

app = create_app()

def run_seed():
    with app.app_context():
        # Clean and create tables
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(username='admin').first():
            print("Base de datos ya cuenta con datos.")
            return

        print("Iniciando carga de datos iniciales...")

        # 1. Company Setting
        company = CompanySetting(
            company_name="AutoRepuestos San Jorge S.A.S.",
            nit="901.458.789-3",
            phone="+57 (601) 745-8899",
            email="contacto@autorepuestossanjorge.com",
            address="Av. Industrial # 45-20, Zona Bodegas",
            currency_symbol="$"
        )
        db.session.add(company)

        # 2. Users
        admin_user = User(
            username='admin',
            full_name='Javier Triana (Administrador)',
            email='admin@almacen.com',
            role='admin',
            active=True
        )
        admin_user.set_password('admin123')

        almacen_user = User(
            username='almacen',
            full_name='Rodrigo Martínez (Jefe Bodega)',
            email='bodega@almacen.com',
            role='almacenista',
            active=True
        )
        almacen_user.set_password('almacen123')

        consult_user = User(
            username='consulta',
            full_name='Mariana Vélez (Asesora Mostrador)',
            email='ventas@almacen.com',
            role='consultor',
            active=True
        )
        consult_user.set_password('consulta123')

        db.session.add_all([admin_user, almacen_user, consult_user])
        db.session.flush()

        # 3. Categories
        cat_frenos = Category(code="FRN", name="Sistema de Frenos", description="Discos, pastillas, bandas y mordazas")
        cat_motor = Category(code="MOT", name="Sistema de Motor", description="Pistones, empaquetaduras, válvulas, bujías")
        cat_susp = Category(code="SUS", name="Suspensión y Dirección", description="Amortiguadores, terminales, tijeras, rótulas")
        cat_filtros = Category(code="FLT", name="Filtros y Mantenimiento", description="Filtros de aceite, aire, cabina y combustible")
        cat_elec = Category(code="ELE", name="Sistema Eléctrico", description="Alternadores, arrancadores, sensores y bobinas")
        
        db.session.add_all([cat_frenos, cat_motor, cat_susp, cat_filtros, cat_elec])
        db.session.flush()

        # 4. Brands
        b_brembo = Brand(name="Brembo", country="Italia", description="Sistemas de frenado de alto rendimiento")
        b_bosch = Brand(name="Bosch", country="Alemania", description="Tecnología automotriz integral y encendido")
        b_denso = Brand(name="Denso", country="Japón", description="Equipo original de encendido y sensores")
        b_monroe = Brand(name="Monroe", country="EE.UU.", description="Líder en amortiguadores y suspensión")
        b_mann = Brand(name="Mann-Filter", country="Alemania", description="Filtración automotriz de primera calidad")
        b_ngk = Brand(name="NGK", country="Japón", description="Bujías y cables de alta gama")

        db.session.add_all([b_brembo, b_bosch, b_denso, b_monroe, b_mann, b_ngk])
        db.session.flush()

        # 5. Locations
        loc_1 = Location(name="Bodega Principal", aisle="A1", shelf="01", bin="A", description="Zona de Frenos pesados")
        loc_2 = Location(name="Bodega Principal", aisle="A1", shelf="02", bin="B", description="Frenos ligeros y pastillas")
        loc_3 = Location(name="Bodega Principal", aisle="B2", shelf="01", bin="A", description="Módulo de Filtración")
        loc_4 = Location(name="Bodega Principal", aisle="C1", shelf="03", bin="C", description="Estantería de Encendido Eléctrico")
        loc_5 = Location(name="Bodega Secundaria", aisle="S1", shelf="01", bin="A", description="Suspensión y Amortiguadores")

        db.session.add_all([loc_1, loc_2, loc_3, loc_4, loc_5])
        db.session.flush()

        # 6. Suppliers
        sup_1 = Supplier(
            nit_ruc="900.234.567-8",
            name="Distribuidora Nacional de Autopartes S.A.",
            contact_name="Andrés Ospina",
            phone="+57 310 445 7788",
            email="ventas@disnacional.com",
            address="Carrera 28 # 12-40",
            city="Bogotá"
        )
        sup_2 = Supplier(
            nit_ruc="890.765.432-1",
            name="Importadora de Frenos y Suspensión Ltda.",
            contact_name="Claudia Rentería",
            phone="+57 320 889 1234",
            email="crenteria@frenosysusp.com",
            address="Calle 10 # 65-18",
            city="Medellín"
        )
        sup_3 = Supplier(
            nit_ruc="901.123.987-4",
            name="Sistemas Eléctricos del Valle",
            contact_name="Germán Morales",
            phone="+57 315 678 9012",
            email="pedidos@sevalle.com.co",
            address="Av. 4 Norte # 24N-10",
            city="Cali"
        )

        db.session.add_all([sup_1, sup_2, sup_3])
        db.session.flush()

        # 7. Products catalog
        products_data = [
            {
                "sku": "FRN-PST-001",
                "barcode": "7701234567891",
                "oem_reference": "04465-02220",
                "name": "Pastillas de Freno Delanteras Cerámica Toyota Corolla",
                "category_id": cat_frenos.id,
                "brand_id": b_brembo.id,
                "location_id": loc_2.id,
                "unit_measure": "JGO",
                "min_stock": 6,
                "max_stock": 40,
                "cost_price": 95000.0,
                "sale_price": 145000.0,
                "initial_stock": 18
            },
            {
                "sku": "FRN-DSC-002",
                "barcode": "7701234567892",
                "oem_reference": "43512-02250",
                "name": "Disco de Freno Ventilado Delantero 275mm",
                "category_id": cat_frenos.id,
                "brand_id": b_brembo.id,
                "location_id": loc_1.id,
                "unit_measure": "PAR",
                "min_stock": 4,
                "max_stock": 25,
                "cost_price": 180000.0,
                "sale_price": 270000.0,
                "initial_stock": 8
            },
            {
                "sku": "FLT-ACT-101",
                "barcode": "7701234567893",
                "oem_reference": "W712/75",
                "name": "Filtro de Aceite Blindado Mann W712",
                "category_id": cat_filtros.id,
                "brand_id": b_mann.id,
                "location_id": loc_3.id,
                "unit_measure": "UN",
                "min_stock": 15,
                "max_stock": 120,
                "cost_price": 24000.0,
                "sale_price": 38000.0,
                "initial_stock": 3
            }, # BAJO MINIMO INTENCIONAL
            {
                "sku": "FLT-AIR-102",
                "barcode": "7701234567894",
                "oem_reference": "C26013",
                "name": "Filtro de Aire Motor Panel Rectangular",
                "category_id": cat_filtros.id,
                "brand_id": b_mann.id,
                "location_id": loc_3.id,
                "unit_measure": "UN",
                "min_stock": 8,
                "max_stock": 50,
                "cost_price": 32000.0,
                "sale_price": 52000.0,
                "initial_stock": 22
            },
            {
                "sku": "MOT-BUJ-201",
                "barcode": "7701234567895",
                "oem_reference": "ILKAR7B11",
                "name": "Bujía Láser Iridio NGK Larga Duración",
                "category_id": cat_motor.id,
                "brand_id": b_ngk.id,
                "location_id": loc_4.id,
                "unit_measure": "UN",
                "min_stock": 20,
                "max_stock": 150,
                "cost_price": 38000.0,
                "sale_price": 58000.0,
                "initial_stock": 0
            }, # AGOTADO INTENCIONAL
            {
                "sku": "SUS-AMT-301",
                "barcode": "7701234567896",
                "oem_reference": "72691",
                "name": "Amortiguador Delantero a Gas OESpectrum",
                "category_id": cat_susp.id,
                "brand_id": b_monroe.id,
                "location_id": loc_5.id,
                "unit_measure": "UN",
                "min_stock": 4,
                "max_stock": 20,
                "cost_price": 210000.0,
                "sale_price": 315000.0,
                "initial_stock": 6
            },
            {
                "sku": "ELE-BOB-401",
                "barcode": "7701234567897",
                "oem_reference": "0986221057",
                "name": "Bobina de Encendido Electrónico Directo Bosch",
                "category_id": cat_elec.id,
                "brand_id": b_bosch.id,
                "location_id": loc_4.id,
                "unit_measure": "UN",
                "min_stock": 5,
                "max_stock": 30,
                "cost_price": 115000.0,
                "sale_price": 175000.0,
                "initial_stock": 12
            },
            {
                "sku": "ELE-ALT-402",
                "barcode": "7701234567898",
                "oem_reference": "104210-4490",
                "name": "Alternador 12V 90A Polea Desacoplable Denso",
                "category_id": cat_elec.id,
                "brand_id": b_denso.id,
                "location_id": loc_4.id,
                "unit_measure": "UN",
                "min_stock": 2,
                "max_stock": 10,
                "cost_price": 540000.0,
                "sale_price": 790000.0,
                "initial_stock": 2
            } # BAJO MINIMO
        ]

        created_products = []
        for p_info in products_data:
            init_qty = p_info.pop("initial_stock")
            product = Product(**p_info)
            db.session.add(product)
            db.session.flush()

            if init_qty > 0:
                register_movement(
                    product_id=product.id,
                    movement_type="entrada_compra",
                    quantity=init_qty,
                    unit_cost=product.cost_price,
                    reference_doc="INVENTARIO-INICIAL-2026",
                    notes="Carga física inicial del almacén",
                    user_id=admin_user.id
                )
            created_products.append(product)

        # 8. Demo Purchase Order (Approved state ready to receive)
        order = PurchaseOrder(
            order_number="OC-202610-0001",
            supplier_id=sup_1.id,
            status="aprobada",
            notes="Reabastecimiento urgente de filtros y pastillas",
            created_by_id=admin_user.id
        )
        db.session.add(order)
        db.session.flush()

        item1 = PurchaseItem(
            purchase_id=order.id,
            product_id=created_products[2].id, # Filtro aceite
            quantity=50,
            unit_cost=23500.0,
            total_cost=50 * 23500.0
        )
        item2 = PurchaseItem(
            purchase_id=order.id,
            product_id=created_products[4].id, # Bujías agotadas
            quantity=40,
            unit_cost=37000.0,
            total_cost=40 * 37000.0
        )
        db.session.add_all([item1, item2])
        order.total_amount = item1.total_cost + item2.total_cost

        db.session.commit()
        print("¡Datos de prueba sembrados exitosamente!")

if __name__ == '__main__':
    run_seed()
