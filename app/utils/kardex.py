from app.models.models import db, Product, InventoryMovement
from datetime import datetime

def register_movement(product_id, movement_type, quantity, unit_cost=None, reference_doc='', notes='', user_id=None):
    """
    Registra un movimiento en el Kárdex y actualiza las existencias y costos del producto.
    
    movement_type:
      - 'entrada_compra'
      - 'salida_venta'
      - 'salida_taller'
      - 'ajuste_positivo'
      - 'ajuste_negativo'
      - 'devolucion'
    """
    product = Product.query.get(product_id)
    if not product:
        raise ValueError(f"Producto con ID {product_id} no encontrado")

    quantity = int(quantity)
    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor a cero")

    previous_stock = product.current_stock or 0

    if movement_type in ['salida_venta', 'salida_taller', 'ajuste_negativo']:
        if previous_stock < quantity:
            raise ValueError(f"Stock insuficiente para '{product.name}'. Disponible: {previous_stock}, Requerido: {quantity}")
        new_stock = previous_stock - quantity
        movement_cost = product.cost_price or 0.0
    elif movement_type in ['entrada_compra', 'ajuste_positivo', 'devolucion']:
        new_stock = previous_stock + quantity
        cost_in = float(unit_cost) if unit_cost is not None else (product.cost_price or 0.0)
        movement_cost = cost_in
        
        # Recálculo de Costo Promedio Ponderado (CPP) si es entrada de compra o ajuste
        if new_stock > 0 and unit_cost is not None and unit_cost > 0:
            current_total_value = previous_stock * (product.cost_price or 0.0)
            incoming_total_value = quantity * float(unit_cost)
            product.cost_price = round((current_total_value + incoming_total_value) / new_stock, 2)
    else:
        raise ValueError(f"Tipo de movimiento '{movement_type}' no soportado")

    product.current_stock = new_stock
    
    # Actualizar estado según stock
    if new_stock <= 0:
        product.status = 'agotado'
    elif product.status == 'agotado':
        product.status = 'activo'

    movement = InventoryMovement(
        product_id=product.id,
        movement_type=movement_type,
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        unit_cost=movement_cost,
        reference_doc=reference_doc,
        notes=notes,
        created_by_id=user_id,
        created_at=datetime.utcnow()
    )

    db.session.add(movement)
    return movement
