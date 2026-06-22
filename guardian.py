from procesador_pagos import procesar_pago

class PayFlowGuardian:
    def __init__(self, pmt: float):
        self.pmt = pmt
        self.saldo_actual = pmt
        self.estado = "Saludable"
        self.alertas = []
        self.suscripciones_pendientes = 0.0
        self.proyeccion_variables = 0.0
        self.gastos_variables_mes = 0.0

    def establecer_proyeccion_variables(self, monto: float):
        self.proyeccion_variables = monto

    def registrar_gasto(self, monto: float):
        self.saldo_actual -= monto
        self.gastos_variables_mes += monto
        self._actualizar_estado()

    def configurar_ahorro(self, meta_ahorro: float):
        if self.pmt < meta_ahorro:
            self.estado = "Alerta de Déficit"
        else:
            self.saldo_actual -= meta_ahorro
            self._actualizar_estado()

    def registrar_suscripcion_futura(self, monto: float):
        self.suscripciones_pendientes += monto

    def registrar_gasto_ocio(self, monto: float, promedio_historico: float):
        if monto < 0:
            raise ValueError("El gasto de ocio no puede ser negativo")

        limite_maximo = promedio_historico * 1.5

        if monto > limite_maximo:
            raise ValueError("El gasto excede el rango histórico razonable")

        self.saldo_actual -= monto
        self._actualizar_estado()

        if self.saldo_actual < self.suscripciones_pendientes:
            self.alertas.append(
                "ADVERTENCIA: El gasto compromete el pago de suscripciones futuras"
            )

    def ejecutar_cobro_suscripcion(
        self,
        costo: float,
        es_vip: bool,
        cuenta_activa: bool,
        tarjeta_vencida: bool
    ):
        if costo > self.suscripciones_pendientes:
            raise ValueError("No hay suscripciones pendientes por ese monto")

        resultado = procesar_pago(
            self.saldo_actual,
            es_vip,
            cuenta_activa,
            tarjeta_vencida,
            costo
        )

        if resultado == "PAGO_EXITOSO":
            self.saldo_actual -= costo
            self.suscripciones_pendientes -= costo
            self._actualizar_estado()
            return "Éxito"

        elif resultado == "PAGO_CON_ADVERTENCIA":
            self.saldo_actual -= costo
            self.suscripciones_pendientes -= costo
            self._actualizar_estado()
            self.alertas.append(
                "Se cobró suscripción con advertencia (Tarjeta Vencida - Beneficio VIP)"
            )
            return "Advertencia"

        else:
            self.alertas.append(
                f"Fallo al cobrar suscripción de ${costo} "
                "(Revisar fondos o estado de cuenta)"
            )
            return "Fallido"

    def ejecutar_corte_de_caja(self):
        diferencia = self.proyeccion_variables - self.gastos_variables_mes

        reporte = {
            "saldo_final": self.saldo_actual,
            "estado_final": self.estado,
            "alertas_mes": list(self.alertas),
            "reporte_variabilidad": {
                "proyectado": self.proyeccion_variables,
                "ejecutado": self.gastos_variables_mes,
                "diferencia": diferencia
            }
        }

        self.alertas.clear()
        self.suscripciones_pendientes = 0.0
        self.proyeccion_variables = 0.0
        self.gastos_variables_mes = 0.0

        return reporte

    def _actualizar_estado(self):
        limite_riesgo = self.pmt * 0.10

        if self.saldo_actual <= 0:
            self.estado = "Crítico"
        elif self.saldo_actual <= limite_riesgo:
            self.estado = "En Riesgo"
        else:
            self.estado = "Saludable"