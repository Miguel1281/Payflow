import pytest
from payflow_pago import procesar_pago

def test_pago_exitoso():
    cuenta_usuario = {"id_usuario": 1, "saldo_disponible": 5000.0}
    
    resultado = procesar_pago(cuenta_usuario, concepto="Renta", monto_fijo=3500.0)
    
    assert resultado["estado"] == "Éxito"
    assert cuenta_usuario["saldo_disponible"] == 1485.0
    assert resultado["folio"].startswith("PAGO-Renta")

def test_saldo_insuficiente_comision():
    cuenta_usuario = {"id_usuario": 2, "saldo_disponible": 1010.0}
    
    # Cambiamos "Internet" por "Luz" para mantener la lógica original de rechazo intacta
    resultado = procesar_pago(cuenta_usuario, concepto="Luz", monto_fijo=1000.0)
    
    assert resultado["estado"] == "Fondos Insuficientes"
    assert cuenta_usuario["saldo_disponible"] == 1010.0

def test_concepto_invalido():
    cuenta_usuario = {"id_usuario": 3, "saldo_disponible": 5000.0}
    
    resultado = procesar_pago(cuenta_usuario, concepto="Gimnasio", monto_fijo=500.0)
    
    assert resultado["estado"] == "Rechazado"
    assert cuenta_usuario["saldo_disponible"] == 5000.0

def test_pago_internet_sin_comision():
    cuenta_usuario = {"id_usuario": 4, "saldo_disponible": 1000.0}
    
    resultado = procesar_pago(cuenta_usuario, concepto="Internet", monto_fijo=1000.0)
    
    assert resultado["estado"] == "Éxito"
    assert cuenta_usuario["saldo_disponible"] == 0.0
    assert resultado["folio"].startswith("PAGO-Internet")