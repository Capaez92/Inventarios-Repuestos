import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    print(f"\n=======================================================")
    print(f"  AutoStock Pro - Sistema de Inventarios de Repuestos")
    print(f"  Servidor iniciado en: http://127.0.0.1:{port}")
    print(f"  Auto-recarga habilitada: Se reinicia automáticamente con cualquier cambio.")
    print(f"=======================================================\n")
    # debug=True y use_reloader=True aseguran que cualquier cambio en código o plantillas reinicie el servidor de inmediato
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
