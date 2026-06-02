import pytest
from inversiones import CalculadoraInversiones
from inversiones import GestorEstados
from inversiones import IntegradorInversiones

class TestCapaInferior:
    # --- PRUEBAS PARA R1 y R2 ---
    def test_calculo_rendimiento_bajo_riesgo(self):
        calc = CalculadoraInversiones()
        capital = 1000
        meses = 12
        perfil = 'B' # Bajo riesgo (5% anual)
        
        resultado = calc.calcular_rendimiento(capital, meses, perfil)
        
        assert round(resultado, 2) == 1051.16

    def test_calculo_rendimiento_alto_riesgo(self):
        calc = CalculadoraInversiones()
        resultado = calc.calcular_rendimiento(1000, 12, 'A')
        assert round(resultado, 2) == 1126.83

    # --- PRUEBAS PARA R3 ---
    def test_validacion_monto_negativo_lanza_error(self):
        calc = CalculadoraInversiones()
        with pytest.raises(ValueError, match="No se permiten montos negativos"):
            calc.calcular_rendimiento(-500, 12, 'B')

    def test_validacion_plazo_menor_un_ano_lanza_error(self):
        calc = CalculadoraInversiones()
        with pytest.raises(ValueError, match="El plazo mínimo es de 1 año"):
            calc.calcular_rendimiento(1000, 11, 'A')

class TestCapaSuperior:
    # --- PRUEBAS PARA R4 ---
    def test_estado_inicial_disponible(self):
        gestor = GestorEstados(saldo_actual=1000, antiguedad_meses=5)
        assert gestor.estado == "DISPONIBLE"

    # --- PRUEBAS PARA R5 ---
    def test_cambio_estado_inversion_estable(self):
        gestor = GestorEstados(saldo_actual=1000, antiguedad_meses=5)
        # Inversión de exactamente el 50% o menos
        nuevo_estado = gestor.determinar_estado(monto_inversion=500)
        assert nuevo_estado == "INVERSION_ESTABLE"
        assert gestor.estado == "INVERSION_ESTABLE"

    def test_cambio_estado_inversion_riesgosa(self):
        gestor = GestorEstados(saldo_actual=1000, antiguedad_meses=5)
        # Inversión mayor al 50%
        nuevo_estado = gestor.determinar_estado(monto_inversion=501)
        assert nuevo_estado == "INVERSION_RIESGOSA"

    # --- PRUEBAS PARA R6 ---
    def test_restriccion_perfil_cuenta_nueva_rechaza_alto_riesgo(self):
        gestor = GestorEstados(saldo_actual=1000, antiguedad_meses=2) 
        with pytest.raises(ValueError, match="Cuenta nueva no puede elegir Alto Riesgo"):
            gestor.validar_perfil(perfil_riesgo='A')
            
    def test_restriccion_perfil_cuenta_nueva_permite_bajo_riesgo(self):
        gestor = GestorEstados(saldo_actual=1000, antiguedad_meses=2)
        resultado = gestor.validar_perfil(perfil_riesgo='B')
        assert resultado is True

class TestCapaMediaIntegracion:
    def test_inversion_autorizada_estable_bajo_riesgo(self):
        integrador = IntegradorInversiones(saldo_actual=5000, antiguedad_meses=12)
        
        resultado = integrador.procesar_inversion(monto_inversion=1000, meses=12, perfil_riesgo='B')
        
        assert resultado["estado_autorizacion"] == "AUTORIZADA"
        assert resultado["nuevo_estado"] == "INVERSION_ESTABLE"
        assert resultado["folio_aprobacion"] == "BE-1051"

    def test_inversion_autorizada_riesgosa_alto_riesgo(self):
        integrador = IntegradorInversiones(saldo_actual=5000, antiguedad_meses=12)
        resultado = integrador.procesar_inversion(monto_inversion=3000, meses=12, perfil_riesgo='A')
        
        assert resultado["estado_autorizacion"] == "AUTORIZADA"
        assert resultado["nuevo_estado"] == "INVERSION_RIESGOSA"
        assert resultado["folio_aprobacion"] == "AR-3380"

    # --- PRUEBAS PARA RECHAZOS (Condición de Disparo) ---
    def test_inversion_rechazada_saldo_insuficiente(self):
        integrador = IntegradorInversiones(saldo_actual=1000, antiguedad_meses=12)
        resultado = integrador.procesar_inversion(monto_inversion=2000, meses=12, perfil_riesgo='B')
        
        assert resultado["estado_autorizacion"] == "RECHAZADA"
        assert resultado["folio_aprobacion"] is None

    def test_inversion_rechazada_cuenta_nueva_alto_riesgo(self):
        integrador = IntegradorInversiones(saldo_actual=5000, antiguedad_meses=2)
        resultado = integrador.procesar_inversion(monto_inversion=1000, meses=12, perfil_riesgo='A')
        
        assert resultado["estado_autorizacion"] == "RECHAZADA"
        assert resultado["folio_aprobacion"] is None