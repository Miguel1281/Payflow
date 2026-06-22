import pytest
from guardian import PayFlowGuardian
from unittest.mock import patch


def test_estado_inicial_saludable():
    guardian = PayFlowGuardian(pmt=1000.0)
    assert guardian.estado == "Configuración de Fondos"

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
        guardian.registrar_gasto_ocio(monto=-50.0)

def test_registrar_ocio_rechaza_exceso_historico():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.historial_gastos_ocio = [200.0]

    with pytest.raises(ValueError, match="El gasto excede el rango histórico razonable"):
        guardian.registrar_gasto_ocio(monto=350.0)

def test_registrar_ocio_exitoso():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.historial_gastos_ocio = [200.0]

    guardian.registrar_gasto_ocio(monto=250.0)

    assert guardian.saldo_actual == 750.0
    assert len(guardian.historial_gastos_ocio) == 2

def test_registrar_ocio_advierte_riesgo_suscripciones():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(300.0)
    guardian.historial_gastos_ocio = [1000.0]

    with pytest.raises(PermissionError, match="ADVERTENCIA: El gasto compromete el pago de suscripciones futuras"):
        guardian.registrar_gasto_ocio(monto=800.0)

def test_cobro_suscripcion_excede_pendientes_lanza_error():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    with pytest.raises(
        ValueError,
        match="No hay suscripciones pendientes con ese monto o nombre especificado"
    ):
        guardian.ejecutar_cobro_suscripcion(600.0, False, True, False)

def test_cobro_suscripcion_exitoso():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(500.0, False, True, False)

    assert resultado == "Éxito"
    assert guardian.saldo_actual == 500.0
    assert guardian.suscripciones_pendientes == 0.0

def test_cobro_suscripcion_con_advertencia_vip():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(500.0, True, True, True)

    assert resultado == "Advertencia"
    assert guardian.saldo_actual == 500.0
    assert guardian.suscripciones_pendientes == 0.0
    assert len(guardian.alertas) == 1
    assert "Tarjeta Vencida" in guardian.alertas[0]

def test_cobro_suscripcion_fallido():
    guardian = PayFlowGuardian(pmt=1000.0)
    guardian.registrar_suscripcion_futura(500.0)

    resultado = guardian.ejecutar_cobro_suscripcion(500.0, False, False, False)

    assert resultado == "Fallido"
    assert guardian.saldo_actual == 1000.0
    
    assert guardian.suscripciones_pendientes == 0.0
    
    assert guardian.suscripciones[0]["estado"] == "Suspendida"
    
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

def test_init_pmt_invalido():
    with pytest.raises(ValueError, match="El Presupuesto Mensual Total \\(PMT\\) debe ser mayor a 0"):
        PayFlowGuardian(pmt=0.0)
        
    with pytest.raises(ValueError, match="El Presupuesto Mensual Total \\(PMT\\) debe ser mayor a 0"):
        PayFlowGuardian(pmt=-100.0)

def test_establecer_proyeccion_negativa():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="La proyección de variables no puede ser un monto negativo"):
        guardian.establecer_proyeccion_variables(-100.0)

def test_registrar_gasto_negativo():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="El gasto no puede ser negativo"):
        guardian.registrar_gasto(-50.0)

def test_pagar_servicio_monto_negativo():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="El monto a pagar por un servicio no puede ser negativo"):
        guardian.pagar_servicio("Agua", -20.0)

def test_configurar_ahorro_negativo():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="La meta de ahorro no puede ser negativa"):
        guardian.configurar_ahorro(-100.0)

def test_registrar_suscripcion_futura_negativa():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="El costo de la suscripción futura no puede ser negativo"):
        guardian.registrar_suscripcion_futura(-100.0, "Spotify")

def test_ejecutar_cobro_suscripcion_negativo():
    guardian = PayFlowGuardian(1000.0)
    with pytest.raises(ValueError, match="El monto exacto a cobrar no puede ser negativo"):
        guardian.ejecutar_cobro_suscripcion(-100.0, False, True, False)

def test_pagar_servicio_exitoso():
    guardian = PayFlowGuardian(1000.0)
    resultado = guardian.pagar_servicio("Luz", 100.0)
    
    assert resultado["estado"] == "Éxito"
    assert guardian.saldo_actual == 885.0
    assert guardian.gastos_variables_mes == 115.0

def test_pagar_servicio_fondos_insuficientes():
    guardian = PayFlowGuardian(100.0)
    with pytest.raises(ValueError, match="Fondos insuficientes para cubrir el servicio 'Luz' y su comisión"):
        guardian.pagar_servicio("Luz", 100.0)  

def test_pagar_servicio_rechazado_pasarela():
    guardian = PayFlowGuardian(1000.0)
    with patch('guardian.procesador_servicios', return_value={"estado": "Rechazado", "folio": None}):
        with pytest.raises(ValueError, match="Servicio 'Agua' rechazado en la pasarela"):
            guardian.pagar_servicio("Agua", 100.0)

def test_registrar_suscripcion_sin_nombre_genera_default():
    guardian = PayFlowGuardian(1000.0)
    guardian.registrar_suscripcion_futura(100.0) 
    assert guardian.suscripciones[0]["nombre"] == "Suscripción #1"

def test_ejecutar_cobro_busqueda_por_nombre():
    guardian = PayFlowGuardian(1000.0)
    guardian.registrar_suscripcion_futura(100.0, "Netflix")
    guardian.registrar_suscripcion_futura(100.0, "Spotify")
    
    resultado = guardian.ejecutar_cobro_suscripcion(100.0, False, True, False, nombre="  sPoTiFy  ")
    
    assert resultado == "Éxito"
    assert guardian.saldo_actual == 900.0
    assert guardian.suscripciones[1]["estado"] == "Pagada" 
    assert guardian.suscripciones[0]["estado"] == "Pendiente" 

def test_ejecutar_cobro_nombre_no_encontrado():
    guardian = PayFlowGuardian(1000.0)
    guardian.registrar_suscripcion_futura(100.0, "Netflix")
    
    with pytest.raises(ValueError, match="No hay suscripciones pendientes con ese monto o nombre especificado"):
        guardian.ejecutar_cobro_suscripcion(100.0, False, True, False, nombre="Disney")

def test_registrar_ocio_confirma_riesgo():
    guardian = PayFlowGuardian(1000.0)
    guardian.registrar_suscripcion_futura(300.0)
    
    guardian.registrar_gasto_ocio(monto=800.0, confirmar=True)
    
    assert guardian.saldo_actual == 200.0
    assert len(guardian.alertas) == 1
    assert "ADVERTENCIA:" in guardian.alertas[0]
    
    guardian.registrar_suscripcion_futura(100.0)
    guardian.registrar_gasto_ocio(monto=50.0, confirmar=True)
    assert len(guardian.alertas) == 1 

def test_promedio_historico_vacio():
    guardian = PayFlowGuardian(1000.0)
    assert guardian.promedio_historico_ocio == 0.0

def test_alerta_deficit_persiste_tras_gasto():
    guardian = PayFlowGuardian(1000.0)
    guardian.configurar_ahorro(1500.0)
    assert guardian.estado == "Alerta de Déficit"
    
    guardian.registrar_gasto(50.0) 
    assert guardian.estado == "Alerta de Déficit" # La alerta sobrevive