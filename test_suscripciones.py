import pytest
from procesador_pagos import procesar_pago

# R1: Saldo insuficiente (Independiente de lo demás)
def test_ts_01_pago_rechazado_por_saldo_insuficiente():
    # Saldo (50) < Costo (100)
    resultado = procesar_pago(50, True, True, False, 100)
    assert resultado == "PAGO_RECHAZADO"

# R2: Cuenta bloqueada (Teniendo saldo)
def test_ts_01_pago_rechazado_por_cuenta_inactiva():
    # cuenta_activa = False
    resultado = procesar_pago(200, True, False, False, 100)
    assert resultado == "PAGO_RECHAZADO"

# R3: Caso exitoso Usuario VIP
def test_ts_02_pago_exitoso_usuario_vip_todo_valido():
    # VIP, con saldo, activa y tarjeta vigente
    resultado = procesar_pago(200, True, True, False, 100)
    assert resultado == "PAGO_EXITOSO"

# R4: Caso exitoso Usuario Estándar
def test_ts_02_pago_exitoso_usuario_estandar_todo_valido():
    # No VIP, con saldo, activa y tarjeta vigente
    resultado = procesar_pago(200, False, True, False, 100)
    assert resultado == "PAGO_EXITOSO"

# R5: Regla Especial VIP - Tarjeta Vencida
def test_ts_03_pago_vip_tarjeta_vencida_pasa_con_advertencia():
    # VIP, con saldo y activa, pero tarjeta vencida
    resultado = procesar_pago(200, True, True, True, 100)
    assert resultado == "PAGO_CON_ADVERTENCIA"

# R6: Usuario Estándar - Tarjeta Vencida (Rechazo)
def test_ts_03_pago_estandar_tarjeta_vencida_rechazado():
    # No VIP, con saldo y activa, pero tarjeta vencida
    resultado = procesar_pago(200, False, True, True, 100)
    assert resultado == "PAGO_RECHAZADO"