# Importamos ambos procesadores y les damos un "apodo" (alias) para que no choquen
from procesador_pagos import procesar_pago as procesador_suscripciones
from payflow_pago import procesar_pago as procesador_servicios

class PayFlowGuardian:
    def __init__(self, pmt: float):
        self.pmt = pmt
        self.saldo_actual = pmt
        self.estado = "Configuración de Fondos"
        self.alertas = []
        self.suscripciones = []
        self.proyeccion_variables = 0.0
        self.gastos_variables_mes = 0.0

    @property
    def suscripciones_pendientes(self):
        return sum(sub["costo"] for sub in self.suscripciones if sub["estado"] == "Pendiente")

    def establecer_proyeccion_variables(self, monto: float):
        self.proyeccion_variables = monto

    def registrar_gasto(self, monto: float):
        self.saldo_actual -= monto
        self.gastos_variables_mes += monto
        self._actualizar_estado()

    def pagar_servicio(self, concepto: str, monto: float):
        cuenta_mock = {"saldo_disponible": self.saldo_actual}
        saldo_anterior = self.saldo_actual
        
        resultado = procesador_servicios(cuenta_mock, concepto, monto)
        
        if resultado["estado"] == "Éxito":
            self.saldo_actual = cuenta_mock["saldo_disponible"]
            descuento_total = saldo_anterior - self.saldo_actual
            
            self.gastos_variables_mes += descuento_total
            self._actualizar_estado()
            return resultado
        elif resultado["estado"] == "Fondos Insuficientes":
            raise ValueError(f"Fondos insuficientes para cubrir el servicio '{concepto}' y su comisión.")
        else:
            raise ValueError(f"Servicio '{concepto}' rechazado en la pasarela.")

    def configurar_ahorro(self, meta_ahorro: float):
        if self.pmt < meta_ahorro:
            self.estado = "Alerta de Déficit"
            self.alertas.append("Las metas de ahorro no podrán cumplirse este mes debido a un presupuesto mensual insuficiente.")
        else:
            self.saldo_actual -= meta_ahorro
            self._actualizar_estado()

    def registrar_suscripcion_futura(self, monto: float, nombre: str = None):
        if not nombre:
            nombre = f"Suscripción #{len(self.suscripciones) + 1}"
        self.suscripciones.append({
            "nombre": nombre,
            "costo": monto,
            "estado": "Pendiente"
        })

    def registrar_gasto_ocio(self, monto: float, promedio_historico: float, confirmar: bool = False):
        if monto < 0:
            raise ValueError("El gasto de ocio no puede ser negativo")

        limite_maximo = promedio_historico * 1.5
        if monto > limite_maximo:
            raise ValueError("El gasto excede el rango histórico razonable")

        if self.saldo_actual - monto < self.suscripciones_pendientes:
            msg_advertencia = "ADVERTENCIA: El gasto compromete el pago de suscripciones futuras. El pago de su suscripción de mañana podría no poder realizarse si procede con el gasto actual."
            
            if not confirmar:
                raise PermissionError(msg_advertencia)
                
            if msg_advertencia not in self.alertas:
                self.alertas.append(msg_advertencia)

        self.saldo_actual -= monto
        self._actualizar_estado()

    def ejecutar_cobro_suscripcion(self, costo: float, es_vip: bool, cuenta_activa: bool, tarjeta_vencida: bool, nombre: str = None):
        sub_a_pagar = None
        if nombre:
            for sub in self.suscripciones:
                if sub["nombre"].lower() == nombre.lower() and sub["estado"] == "Pendiente":
                    sub_a_pagar = sub
                    break
        else:
            for sub in self.suscripciones:
                if sub["costo"] == costo and sub["estado"] == "Pendiente":
                    sub_a_pagar = sub
                    break

        if not sub_a_pagar:
            raise ValueError("No hay suscripciones pendientes con ese monto o nombre especificado.")

        # Aquí usamos el alias del procesador de suscripciones (el que valida VIP y tarjetas)
        resultado = procesador_suscripciones(
            self.saldo_actual,
            es_vip,
            cuenta_activa,
            tarjeta_vencida,
            sub_a_pagar["costo"]
        )

        if resultado == "PAGO_EXITOSO":
            self.saldo_actual -= sub_a_pagar["costo"]
            sub_a_pagar["estado"] = "Pagada"
            self._actualizar_estado()
            return "Éxito"
        elif resultado == "PAGO_CON_ADVERTENCIA":
            self.saldo_actual -= sub_a_pagar["costo"]
            sub_a_pagar["estado"] = "Pagada"
            self._actualizar_estado()
            self.alertas.append(f"Se cobró la suscripción '{sub_a_pagar['nombre']}' con advertencia (Tarjeta Vencida - Beneficio VIP).")
            return "Advertencia"
        else:
            nuevo_estado = "Suspendida" if not cuenta_activa else "Vencida"
            sub_a_pagar["estado"] = nuevo_estado
            self.alertas.append(f"Fallo al cobrar suscripción de '{sub_a_pagar['nombre']}' (${sub_a_pagar['costo']}) (Revisar fondos o estado de cuenta).")
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
            },
            "estado_suscripciones_al_corte": [dict(s) for s in self.suscripciones]
        }

        for sub in self.suscripciones:
            sub["estado"] = "Pendiente"

        self.alertas.clear()
        self.proyeccion_variables = 0.0
        self.gastos_variables_mes = 0.0
        self.estado = "Configuración de Fondos"
        return reporte

    def _actualizar_estado(self):
        limite_riesgo = self.pmt * 0.10

        if self.saldo_actual <= 0:
            self.estado = "Crítico"
        elif self.saldo_actual <= limite_riesgo:
            self.estado = "En Riesgo"
        else:
            if self.estado != "Alerta de Déficit":
                self.estado = "Saludable"