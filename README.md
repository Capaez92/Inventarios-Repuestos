# AutoStock Pro - Sistema de Gestión de Inventarios de Repuestos

Sistema integral de gestión de inventarios y control de almacén para repuestos automotrices e industriales desarrollado en Python con Flask.

---

## 🚀 Características Principales

- **Catálogo de Repuestos:**
  - Registro con SKU, código de barras, referencia OEM, marca, categoría y ubicación física en almacén (bodega, pasillo, estante y gaveta).
  - Alertas automáticas de bajo stock y agotamiento.
- **Kárdex & Control de Costos:**
  - Trazabilidad completa de movimientos (*entradas por compra, salidas por venta, entregas a taller, ajustes positivos y negativos*).
  - Recálculo dinámico automático del **Costo Promedio Ponderado (CPP)**.
- **Órdenes de Compra y Proveedores:**
  - Gestión del ciclo de vida de compras (*borrador, aprobada, recibida, cancelada*).
  - Actualización automática de inventario y costos al recibir mercancía.
- **Seguridad y Auditoría:**
  - Control de acceso por roles: `admin`, `almacenista` y `consultor`.
  - Bitácora de auditoría detallada de operaciones realizadas por usuario.
- **Reportes y Exportación:**
  - Exportación de inventario valorizado y movimientos en **Excel (`.xlsx`)** y **PDF**.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.10+, Flask 3.x
- **Base de Datos & ORM:** Flask-SQLAlchemy, SQLite (o PostgreSQL mediante `DATABASE_URL`)
- **Autenticación:** Flask-Login con hashing Werkzeug
- **Reportes:** `openpyxl`, `ReportLab`
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, DataTables

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd inventarios-repuestos
```

### 2. Crear y activar entorno virtual
En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos (SQLite o Supabase)
Por defecto, la aplicación utiliza SQLite local. Para conectar con **Supabase (PostgreSQL en la nube)**:

1. Crea un proyecto en [Supabase](https://supabase.com).
2. Ve a **Project Settings -> Database -> Connection String -> URI** (selecciona el modo *Transaction* o *Session*).
3. Crea un archivo `.env` en la raíz del proyecto (puedes basarte en `.env.example`):
   ```env
   DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
4. (Opcional) Si deseas migrar los datos locales que tienes en SQLite hacia Supabase, ejecuta:
   ```bash
   python migrate_to_supabase.py
   ```
   O para iniciar una base de datos limpia con datos de muestra:
   ```bash
   python seed.py
   ```

### 5. Iniciar la aplicación
En Windows, puedes ejecutar directamente:
```cmd
iniciar_sistema.bat
```
O mediante terminal:
```bash
python run.py
```

La aplicación estará disponible en: [http://127.0.0.1:8090](http://127.0.0.1:8090)

---

## 👤 Usuarios de Demostración

| Usuario | Contraseña | Rol | Permisos |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Administrador | Acceso total al sistema y configuraciones |
| `almacen` | `almacen123` | Almacenista | Gestión de productos, compras y movimientos |
| `consulta` | `consulta123` | Consultor | Consulta y lectura de catálogo e inventario |

---

## 🧪 Pruebas
Para ejecutar las pruebas del sistema:
```bash
python test_app.py
```
