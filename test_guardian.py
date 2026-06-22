import pytest
from guardian import PayFlowGuardian

def test_estado_inicial_saludable():
    guardian = PayFlowGuardian(pmt=1000.0)
    assert guardian.estado == "Saludable"

@pytest.mark.parametrize("gasto, saldo_esperado, estado_esperado", [
    (899.0, 101.0, "Saludable"),
    (900.0, 100.0, "En Riesgo"),
    (901.0, 99.0, "En Riesgo"),
    (1000.0, 0.0, "Crítico")
])
def test_transiciones_de_estado_frontera(gasto, saldo_esperado, estado_esperado):
    guardian = PayFlowGuardian(pmt=1000.0)

    guardian.registrar_gasto(gasto)

    assert guardian.saldo_actual == saldo_esperado
    assert guardian.estado == estado_esperado

def test_configuracion_ahorro_exitoso():
    guardian = PayFlowGuardian(pmt=1000.0)

    guardian.configurar_ahorro(200.0)

    assert guardian.saldo_actual == 800.0
    assert guardian.estado == "Saludable"

def test_configuracion_ahorro_genera_alerta_deficit():
    guardian = PayFlowGuardian(pmt=1000.0)

    guardian.configurar_ahorro(1100.0)

    assert guardian.estado == "Alerta de Déficit"

def test_registrar_ocio_rechaza_monto_negativo():
    guardian = PayFlowGuardian(pmt=1000.0)

    with pytest.raises(ValueError, match="El gasto de ocio no puede ser negativo"):
        guardian.registrar_gasto_ocio(monto=-50.0, promedio_historico=200.0)

def test_registrar_ocio_rechaza_exceso_historico():
    guardian = PayFlowGuardian(pmt=1000.0)

    with pytest.raises(ValueError, match="El gasto excede el rango histórico razonable"):
        guardian.registrar_gasto_ocio(monto=350.0, promedio_historico=200.0)

def test_registrar_ocio_exitoso():
    guardian = PayFlowGuardian(pmt=1000.0)

    guardian.registrar_gasto_ocio(monto=250.0, promedio_historico=200.0)

    assert guardian.saldo_actual == 750.0

def test_registrar_ocio_advierte_riesgo_suscripciones():
    guardian = PayFlowGuardian(pmt=1000.0)

    guardian.registrar_suscripcion_futura(300.0)

    guardian.registrar_gasto_ocio(monto=800.0, promedio_historico=1000.0)

    assert guardian.saldo_actual == 200.0

    assert "ADVERTENCIA: El gasto compromete el pago de suscripciones futuras" in guardian.alertas

def test_cobro_suscripcion_excede_pendientes_lanza_error():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    with pytest.raises(
        ValueError,
        match="No hay suscripciones pendientes por ese monto"
    ):
        guardian.ejecutar_cobro_suscripcion(600.0, False, True, False)

def test_cobro_suscripcion_exitoso():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(
        500.0,
        False,
        True,
        False
    )

    assert resultado == "Éxito"
    assert guardian.saldo_actual == 500.0
    assert guardian.suscripciones_pendientes == 0.0

def test_cobro_suscripcion_con_advertencia_vip():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(
        500.0,
        True,
        True,
        True
    )

    assert resultado == "Advertencia"
    assert guardian.saldo_actual == 500.0
    assert guardian.suscripciones_pendientes == 0.0
    assert len(guardian.alertas) == 1
    assert "Tarjeta Vencida" in guardian.alertas[0]

def test_cobro_suscripcion_fallido():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(
        500.0,
        False,
        False,
        False
    )

    assert resultado == "Fallido"
    assert guardian.saldo_actual == 1000.0
    assert guardian.suscripciones_pendientes == 500.0
    assert len(guardian.alertas) == 1
    assert "Fallo al cobrar" in guardian.alertas[0]

def test_corte_de_caja_genera_reporte_y_reinicia():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_gasto(200.0)
    guardian.alertas.append("Alerta simulada")

    reporte = guardian.ejecutar_corte_de_caja()

    assert reporte["saldo_final"] == 800.0
    assert reporte["estado_final"] == "Saludable"
    assert len(reporte["alertas_mes"]) == 1

    assert len(guardian.alertas) == 0

def test_corte_de_caja_incluye_reporte_variabilidad():
    guardian = PayFlowGuardian(pmt=5000.0)

    guardian.establecer_proyeccion_variables(1000.0)

    guardian.registrar_gasto(400.0)
    guardian.registrar_gasto(700.0)

    reporte = guardian.ejecutar_corte_de_caja()

    assert reporte["reporte_variabilidad"]["proyectado"] == 1000.0
    assert reporte["reporte_variabilidad"]["ejecutado"] == 1100.0
    assert reporte["reporte_variabilidad"]["diferencia"] == -100.0