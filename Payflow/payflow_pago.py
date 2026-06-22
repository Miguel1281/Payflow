import time

def validar_disponibilidad(saldo, monto_total):
    return saldo >= monto_total

def calcular_balance(saldo, monto, comision):
    return saldo - monto - comision

def generar_comprobante(concepto):
    timestamp = int(time.time())
    return f"PAGO-{concepto}{timestamp}"

def procesar_pago(cuenta, concepto, monto_fijo):
    conceptos_validos = ["Renta", "Internet", "Luz"]
    comision_fija = 15.0
    
    if concepto not in conceptos_validos:
        return {"estado": "Rechazado", "folio": None}
        
    monto_total_requerido = monto_fijo + comision_fija
    
    if validar_disponibilidad(cuenta["saldo_disponible"], monto_total_requerido):
        # REPARACIÓN TDD: Cambiamos el 0 por 'comision_fija'
        nuevo_saldo = calcular_balance(cuenta["saldo_disponible"], monto_fijo, comision_fija)
        cuenta["saldo_disponible"] = nuevo_saldo
        
        folio_generado = generar_comprobante(concepto)
        return {"estado": "Éxito", "folio": folio_generado}
    else:
        # Emitir mensaje de fondos insuficientes
        return {"estado": "Fondos Insuficientes", "folio": None}