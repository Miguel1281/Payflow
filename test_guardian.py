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

def test_corte_de_caja_genera_reporte_y_reinicia():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_gasto(200.0)
    guardian.alertas.append("Alerta simulada")

    reporte = guardian.ejecutar_corte_de_caja()

    assert reporte["saldo_final"] == 800.0
    assert reporte["estado_final"] == "Saludable"
    assert len(reporte["alertas_mes"]) == 1

    assert len(guardian.alertas) == 0