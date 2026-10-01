from app import create_app
from app.models.models import db, User, Product, InventoryMovement

def test_system():
    app = create_app()
    client = app.test_client()

    print("1. Probando ruta login (GET)...")
    res = client.get('/login')
    assert res.status_code == 200, f"Error en login: {res.status_code}"
    print("   -> OK (200)")

    print("2. Probando inicio de sesión con admin...")
    login_res = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert login_res.status_code == 200
    assert b'Panel de Control' in login_res.data
    print("   -> OK (Login exitoso y redirección al Dashboard)")

    print("3. Probando listado de productos...")
    res = client.get('/products/')
    assert res.status_code == 200
    assert b'FRN-PST-001' in res.data
    print("   -> OK (Catálogo cargado con repuestos)")

    print("4. Probando ruta de órdenes de compra...")
    res = client.get('/purchases/')
    assert res.status_code == 200
    assert b'OC-202610-0001' in res.data
    print("   -> OK (Órdenes de compra visualizadas)")

    print("5. Probando ruta Kárdex...")
    res = client.get('/movements/')
    assert res.status_code == 200
    assert b'INVENTARIO-INICIAL-2026' in res.data
    print("   -> OK (Kárdex con trazabilidad)")

    print("6. Probando generación de reporte Excel...")
    res = client.get('/reports/inventory/excel')
    assert res.status_code == 200
    assert len(res.data) > 1000
    print("   -> OK (Excel generado con éxito)")

    print("7. Probando generación de reporte PDF...")
    res = client.get('/reports/inventory/pdf')
    assert res.status_code == 200
    assert len(res.data) > 1000
    print("   -> OK (PDF generado con éxito)")

    print("\n¡TODAS LAS PRUEBAS FUNCIONARON SATISFACTORIAMENTE!")

if __name__ == '__main__':
    test_system()
