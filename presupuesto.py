def validar_presupuesto(pmt, ahorro_meta, serv_hist, susc_fijas, ocio_hist):
    inputs = [pmt, ahorro_meta, serv_hist, susc_fijas, ocio_hist]
    if any(n < 0 for n in inputs) or pmt == 0:
        raise ValueError("Los importes deben ser positivos y el PMT mayor a cero.")

    alertas = []
    saldo = pmt

    if saldo < ahorro_meta:
        return "EJERCICIO_DEFICIT", alertas
    
    saldo -= ahorro_meta

    if saldo < serv_hist:
        alertas.append("Déficit detectado en Servicios")
        return "EJERCICIO_DEFICIT", alertas
    
    saldo -= serv_hist

    if saldo < susc_fijas:
        alertas.append("Déficit detectado en Suscripciones")
        return "EJERCICIO_DEFICIT", alertas
    
    saldo -= susc_fijas

    if saldo < ocio_hist:
        alertas.append("Déficit detectado en Ocio")
        return "EJERCICIO_DEFICIT", alertas

    return "EJERCICIO", alertas