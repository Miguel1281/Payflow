def validar_transferencia(monto: float, hora_transferencia: int, tipo_cuenta_destino: str, token_activo: bool = False) -> str:
    estado_aprobado = "APROBADA"
    estado_rechazado = "RECHAZADA_POR_POLÍTICA"

    # Regla 3: Mismo banco
    if tipo_cuenta_destino == "Misma":
        return estado_aprobado

    # Regla 1: Horario para cuentas de Crédito
    if tipo_cuenta_destino == "Crédito":
        if 9 <= hora_transferencia <= 18:
            return estado_aprobado
        return estado_rechazado

    # Regla 2: Montos y Token para cuentas de Débito
    if tipo_cuenta_destino == "Débito":
        if monto <= 5000:
            return estado_aprobado
        elif monto > 5000 and token_activo:
            return estado_aprobado
        return estado_rechazado

    # Fail-Safe: Rechazo por defecto para casos no contemplados
    return estado_rechazado