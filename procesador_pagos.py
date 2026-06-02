def procesar_pago(saldo, es_vip, cuenta_activa, tarjeta_vencida, costo):
    if saldo < costo or not cuenta_activa:
        return "PAGO_RECHAZADO"
    
    if tarjeta_vencida:
        return "PAGO_CON_ADVERTENCIA" if es_vip else "PAGO_RECHAZADO"
            
    return "PAGO_EXITOSO"