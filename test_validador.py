from validador_spei import validar_transferencia

def test_transferencia_misma_cuenta():
    resultado = validar_transferencia(10000.0, 23, "Misma", False)
    assert resultado == "APROBADA"

def test_transferencia_credito_horario_valido():
    resultado = validar_transferencia(2500.0, 10, "Crédito", False)
    assert resultado == "APROBADA"

def test_transferencia_credito_horario_invalido():
    resultado = validar_transferencia(2500.0, 19, "Crédito", False)
    assert resultado == "RECHAZADA_POR_POLÍTICA"

def test_transferencia_debito_monto_valido():
    resultado = validar_transferencia(4000.0, 14, "Débito", False)
    assert resultado == "APROBADA"

def test_transferencia_debito_excede_monto_sin_token():
    resultado = validar_transferencia(6500.0, 14, "Débito", False)
    assert resultado == "RECHAZADA_POR_POLÍTICA"

def test_transferencia_debito_excede_monto_con_token():
    resultado = validar_transferencia(6500.0, 14, "Débito", True)
    assert resultado == "APROBADA"