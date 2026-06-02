class CalculadoraInversiones:
    """
    Capa Inferior: Esta clase representa nuestro motor de cálculo matemático.
    Se encarga de procesar de forma aislada las ecuaciones financieras y sus 
    validaciones numéricas elementales sin intervenir en las decisiones de estado.
    """

    def calcular_rendimiento(self, capital: float, meses: int, perfil_riesgo: str) -> float: 
        # Valido el requerimiento R3: compruebo que el capital a invertir no sea un monto negativo.
        if capital < 0:
            # Si el monto es negativo, interrumpo el flujo lanzando una excepción controlada de tipo ValueError.
            raise ValueError("No se permiten montos negativos")
            
        # Aplico la segunda restricción de R3: el plazo de la inversión (n) no puede ser inferior a 1 año (12 meses).
        if meses < 12:
            # Levanto una excepción si el usuario ingresa un periodo de tiempo menor al mínimo permitido.
            raise ValueError("El plazo mínimo es de 1 año (12 meses)")
             
        # Implemento el requerimiento R2 utilizando un operador ternario para definir la tasa de interés anual (r).
        # Asigno 5% (0.05) si el perfil es de Bajo riesgo ('B') o 12% (0.12) si es de Alto riesgo ('A').
        tasa_anual = 0.05 if perfil_riesgo == 'B' else 0.12
        
        # Convierto la tasa de interés anual a una tasa mensual efectiva dividiéndola entre 12, ya que el plazo se mide en meses.
        r = tasa_anual / 12  
         
        # Implemento la fórmula matemática de interés compuesto estipulada en el requerimiento R1: A = P(1 + r)^n.
        # Donde 'capital' es P, 'r' es la tasa mensual que calculé arriba y 'meses' es el exponente temporal n.
        monto_final = capital * ((1 + r) ** meses)
        
        # Retorno el interés compuesto total calculado (A) para que pueda ser empaquetado por la capa de integración.
        return monto_final
    

class GestorEstados:
    """
    Capa Superior: Esta clase gestiona de forma exclusiva el ciclo de vida, los estados 
    del sistema y el cumplimiento estricto de las políticas comerciales de la plataforma.
    """
    def __init__(self, saldo_actual: float, antiguedad_meses: int):
        # Almaceno de forma local el saldo actual de la cuenta para evaluar los límites de descapitalización.
        self.saldo_actual = saldo_actual
        # Almaceno la antigüedad de la cuenta del usuario para aplicar filtros de seguridad en perfiles de riesgo.
        self.antiguedad_meses = antiguedad_meses
        # Dando cumplimiento al requerimiento R4, defino que todo el flujo del sistema arranca en el estado DISPONIBLE.
        self.estado = "DISPONIBLE" 

    def determinar_estado(self, monto_inversion: float) -> str:
        # Establezco el punto de decisión calculando de manera precisa el umbral equivalente al 50% del saldo actual.
        umbral = self.saldo_actual * 0.5
        
        # Evalúo el requerimiento R5: verifico si el monto que se planea invertir supera estrictamente el umbral del 50%.
        if monto_inversion > umbral:
            # Si compromete más de la mitad del saldo disponible, muto el sistema al estado INVERSION_RIESGOSA.
            self.estado = "INVERSION_RIESGOSA"
        # Manejo la contraparte de R5 incluyendo nuestro acuerdo técnico para el caso límite exacto del 50% (monto <= umbral).
        else:
            # Si el monto es menor o igual a la mitad del dinero disponible, transiciono el sistema a INVERSION_ESTABLE.
            self.estado = "INVERSION_ESTABLE"
            
        # Devuelvo la cadena con el nuevo estado del sistema para que sea procesada en el resumen de integración.
        return self.estado

    def validar_perfil(self, perfil_riesgo: str) -> bool:
        # Implemento la restricción de perfil detallada en el requerimiento R6.
        # Evalúo simultáneamente si la cuenta califica como CUENTA_NUEVA (< 3 meses) y si se seleccionó el perfil de Alto Riesgo ('A').
        if self.antiguedad_meses < 3 and perfil_riesgo == 'A':
            # Bloqueo la operación arrojando un ValueError si un usuario nuevo intenta operar fuera de su límite permitido.
            raise ValueError("Cuenta nueva no puede elegir Alto Riesgo")
        # Si la validación pasa con éxito, devuelvo True confirmando la compatibilidad de la cuenta con el perfil de inversión.
        return True
    

class IntegradorInversiones:
    """
    Capa Media: Actúa como el puente o mediador central ("la rebanada intermedia").
    Orquesta la comunicación entre la lógica comercial superior y el motor de cálculo matemático inferior.
    """
    def __init__(self, saldo_actual: float, antiguedad_meses: int):
        # Mantengo una referencia local del saldo de la cuenta para realizar el control primario de fondos.
        self.saldo_actual = saldo_actual
        # Instancio los componentes de la Capa Superior para delegar de forma limpia el control de las políticas de estado.
        self.gestor = GestorEstados(saldo_actual, antiguedad_meses)
        # Instancio los componentes de la Capa Inferior para delegar todo el procesamiento y proyecciones matemáticas.
        self.calculadora = CalculadoraInversiones()

    def procesar_inversion(self, monto_inversion: float, meses: int, perfil_riesgo: str) -> dict:
        # Ejecuto la primera condición de autorización de R7: verificar si el saldo disponible cubre el capital (P).
        if self.saldo_actual < monto_inversion:
            # Aplico la condición de disparo: si los fondos son insuficientes, rechazo la transacción y anulo el folio.
            return {"estado_autorizacion": "RECHAZADA", "folio_aprobacion": None}
            
        # Abro un bloque de captura de excepciones para evaluar el segundo criterio de R7 (compatibilidad de perfil).
        try:
            # Invoco la lógica de la capa superior para asegurar que la antigüedad sea apta para el nivel de riesgo solicitado.
            self.gestor.validar_perfil(perfil_riesgo)
        # Si la capa superior detecta una infracción de perfil (cuenta nueva en alto riesgo), capturo la excepción arrojada.
        except ValueError:
             # Ejecuto de forma obligatoria la condición de disparo retornando el estado RECHAZADA y un folio nulo.
             return {"estado_autorizacion": "RECHAZADA", "folio_aprobacion": None}
             
        # Una vez que ambos criterios de R7 se cumplen simultáneamente, procedo con la ejecución coordinada del sistema.
        # Invoco al gestor de la capa superior para consolidar la transición del estado actual de la cuenta.
        nuevo_estado = self.gestor.determinar_estado(monto_inversion)
        # Invoco a la calculadora de la capa inferior pasándole los parámetros numéricos limpios para obtener la proyección.
        monto_final = self.calculadora.calcular_rendimiento(monto_inversion, meses, perfil_riesgo)
        
        # Arranco la construcción del folio requerida en R9. Extraigo el código del perfil (B o A) directo de la entrada.
        cod_perfil = perfil_riesgo 
        # Determino el código del estado ('E' para inversión estable o 'R' para riesgosa) mapeando la salida del gestor.
        cod_estado = 'E' if nuevo_estado == "INVERSION_ESTABLE" else 'R'
        # Ensamblo el string siguiendo el formato estricto <PERFIL><ESTADO>-<MONTO_FINAL_REDONDEADO> aplicando la función round().
        folio = f"{cod_perfil}{cod_estado}-{round(monto_final)}"
        
        # Concluyo el requerimiento R8 empaquetando y retornando el objeto de integración final con los datos de todas las capas.
        return {
            "estado_autorizacion": "AUTORIZADA",
            "monto_final": monto_final,
            "nuevo_estado": nuevo_estado,
            "folio_aprobacion": folio
        }