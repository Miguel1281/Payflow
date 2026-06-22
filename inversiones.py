class CalculadoraInversiones:

    def calcular_rendimiento(self, capital: float, meses: int, perfil_riesgo: str) -> float:
        if capital < 0:
            raise ValueError("No se permiten montos negativos")

        if meses < 12:
            raise ValueError("El plazo mínimo es de 1 año (12 meses)")

        tasa_anual = 0.05 if perfil_riesgo == 'B' else 0.12
        r = tasa_anual / 12

        monto_final = capital * ((1 + r) ** meses)

        return monto_final


class GestorEstados:

    def __init__(self, saldo_actual: float, antiguedad_meses: int):
        self.saldo_actual = saldo_actual
        self.antiguedad_meses = antiguedad_meses
        self.estado = "DISPONIBLE"

    def determinar_estado(self, monto_inversion: float) -> str:
        umbral = self.saldo_actual * 0.5

        if monto_inversion > umbral:
            self.estado = "INVERSION_RIESGOSA"
        else:
            self.estado = "INVERSION_ESTABLE"

        return self.estado

    def validar_perfil(self, perfil_riesgo: str) -> bool:
        if self.antiguedad_meses < 3 and perfil_riesgo == 'A':
            raise ValueError("Cuenta nueva no puede elegir Alto Riesgo")

        return True


class IntegradorInversiones:

    def __init__(self, saldo_actual: float, antiguedad_meses: int):
        self.saldo_actual = saldo_actual
        self.gestor = GestorEstados(saldo_actual, antiguedad_meses)
        self.calculadora = CalculadoraInversiones()

    def procesar_inversion(self, monto_inversion: float, meses: int, perfil_riesgo: str) -> dict:
        if self.saldo_actual < monto_inversion:
            return {"estado_autorizacion": "RECHAZADA", "folio_aprobacion": None}

        try:
            self.gestor.validar_perfil(perfil_riesgo)
        except ValueError:
            return {"estado_autorizacion": "RECHAZADA", "folio_aprobacion": None}

        nuevo_estado = self.gestor.determinar_estado(monto_inversion)
        monto_final = self.calculadora.calcular_rendimiento(monto_inversion, meses, perfil_riesgo)

        cod_perfil = perfil_riesgo
        cod_estado = 'E' if nuevo_estado == "INVERSION_ESTABLE" else 'R'
        folio = f"{cod_perfil}{cod_estado}-{round(monto_final)}"

        return {
            "estado_autorizacion": "AUTORIZADA",
            "monto_final": monto_final,
            "nuevo_estado": nuevo_estado,
            "folio_aprobacion": folio
        }