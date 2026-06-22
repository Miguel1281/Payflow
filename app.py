from flask import Flask, render_template, request, redirect, url_for, flash
from guardian import PayFlowGuardian

app = Flask(__name__)
# Clave secreta necesaria para mostrar mensajes temporales (alertas/errores)
app.secret_key = 'payflow_secreto_super_seguro'

# Instancia global para simular la sesión (En un entorno real usaríamos base de datos)
guardian_app = None

@app.route('/')
def index():
    # Renderiza la vista pasando la instancia actual de PayFlow
    return render_template('index.html', guardian=guardian_app)

@app.route('/iniciar', methods=['POST'])
def iniciar():
    global guardian_app
    try:
        pmt = float(request.form.get('pmt'))
        if pmt <= 0:
            flash("El PMT debe ser mayor a 0.", "error")
        else:
            guardian_app = PayFlowGuardian(pmt)
            flash("Sistema inicializado correctamente con éxito.", "success")
    except ValueError:
        flash("Por favor, ingresa un monto numérico válido.", "error")
    return redirect(url_for('index'))

@app.route('/accion/<tipo>', methods=['POST'])
def accion(tipo):
    global guardian_app
    if not guardian_app:
        flash("Primero debes inicializar el Presupuesto (PMT).", "error")
        return redirect(url_for('index'))
        
    try:
        if tipo == 'ahorro':
            monto = float(request.form.get('monto'))
            guardian_app.configurar_ahorro(monto)
            flash("Meta de ahorro configurada y procesada.", "success")
            
        elif tipo == 'suscripcion_futura':
            monto = float(request.form.get('monto'))
            guardian_app.registrar_suscripcion_futura(monto)
            flash("Suscripción futura registrada en pendiente.", "success")
            
        elif tipo == 'gasto_regular':
            monto = float(request.form.get('monto'))
            guardian_app.registrar_gasto(monto)
            flash("Gasto regular deducido del saldo.", "success")
            
        elif tipo == 'gasto_ocio':
            monto = float(request.form.get('monto'))
            promedio = float(request.form.get('promedio'))
            guardian_app.registrar_gasto_ocio(monto, promedio)
            flash("Gasto de ocio evaluado y registrado.", "success")
            
        elif tipo == 'cobro_suscripcion':
            costo = float(request.form.get('costo'))
            # Capturamos los checkboxes (si están marcados llegan como 'on')
            es_vip = request.form.get('es_vip') == 'on'
            cuenta_activa = request.form.get('cuenta_activa') == 'on'
            tarjeta_vencida = request.form.get('tarjeta_vencida') == 'on'
            
            resultado = guardian_app.ejecutar_cobro_suscripcion(costo, es_vip, cuenta_activa, tarjeta_vencida)
            flash(f"Resultado del cobro: {resultado}", "info")
            
        elif tipo == 'corte_caja':
            reporte = guardian_app.ejecutar_corte_de_caja()
            mensaje = (f"Corte de Caja realizado. Saldo final: ${reporte['saldo_final']:.2f} | "
                       f"Estado final: {reporte['estado_final']} | "
                       f"Alertas en el mes: {len(reporte['alertas_mes'])}")
            flash(mensaje, "success")
            
    # Gracias al TDD, sabemos que guardian lanza ValueError al romper reglas de negocio
    except ValueError as e:
        flash(f"Regla de Negocio: {str(e)}", "error")
    except Exception as e:
        flash("Entrada inválida o error en el formulario.", "error")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)