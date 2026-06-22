from flask import Flask, render_template, request, redirect, url_for, flash
from guardian import PayFlowGuardian

app = Flask(__name__)
app.secret_key = 'payflow_secreto_super_seguro'

guardian_app = None

@app.route('/')
def index():
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
            flash("Sistema inicializado en estado 'Configuración de Fondos'.", "success")
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
            if guardian_app.estado == "Alerta de Déficit":
                flash("Alerta de Déficit activada: El capital de ahorro no podrá cumplirse.", "error")
            else:
                flash("Meta de ahorro configurada y procesada correctamente.", "success")
            
        elif tipo == 'proyeccion_variables':
            monto = float(request.form.get('monto'))
            guardian_app.establecer_proyeccion_variables(monto)
            flash("Proyección de gastos variables establecida.", "success")
            
        elif tipo == 'suscripcion_futura':
            monto = float(request.form.get('monto'))
            nombre = request.form.get('nombre')
            guardian_app.registrar_suscripcion_futura(monto, nombre if nombre else None)
            flash(f"Suscripción '{nombre or 'Fija'}' registrada como Pendiente.", "success")

        elif tipo == 'pago_servicio':
            concepto = request.form.get('concepto')
            monto = float(request.form.get('monto'))
            
            # Llamamos a nuestro nuevo método (ahora admite cualquier texto)
            resultado = guardian_app.pagar_servicio(concepto, monto)
            
            flash(f"Pago de '{concepto}' procesado. Estado: {resultado['estado']} | Folio: {resultado['folio']}", "success")
        elif tipo == 'gasto_ocio':
            monto = float(request.form.get('monto'))
            promedio = float(request.form.get('promedio'))
            confirmar = request.form.get('confirmar_interactivo') == 'on'
            
            try:
                guardian_app.registrar_gasto_ocio(monto, promedio, confirmar)
                flash("Gasto de ocio aprobado y registrado.", "success")
            except PermissionError as e:
                # Se captura la alerta estructural y se solicita interactividad
                return render_template('index.html', 
                                       guardian=guardian_app, 
                                       solicitar_confirmacion_ocio=True,
                                       ocio_monto=monto,
                                       ocio_promedio=promedio,
                                       msg_advertencia=str(e))
            
        elif tipo == 'cobro_suscripcion':
            costo = float(request.form.get('costo'))
            nombre = request.form.get('nombre_sub')
            es_vip = request.form.get('es_vip') == 'on'
            cuenta_activa = request.form.get('cuenta_activa') == 'on'
            tarjeta_vencida = request.form.get('tarjeta_vencida') == 'on'
            
            resultado = guardian_app.ejecutar_cobro_suscripcion(
                costo, es_vip, cuenta_activa, tarjeta_vencida, nombre if nombre else None
            )
            flash(f"Procesador de Pagos ejecutado. Resultado: {resultado}", "info")
            
        elif tipo == 'corte_caja':
            reporte = guardian_app.ejecutar_corte_de_caja()
            var = reporte['reporte_variabilidad']
            mensaje = (f"Corte de Caja ejecutado. Las suscripciones regresaron a 'Pendiente'. "
                       f"Diferencia de Variabilidad: ${var['diferencia']:.2f}")
            flash(mensaje, "success")
            
    except ValueError as e:
        flash(f"Regla de Negocio Bloqueada: {str(e)}", "error")
    except Exception:
        flash("Error general en el procesamiento de la petición.", "error")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)