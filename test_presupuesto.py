import pytest
from presupuesto import validar_presupuesto

def test_valores_negativos():
    with pytest.raises(ValueError):
        validar_presupuesto(-100, 10, 10, 10, 10)

@pytest.mark.parametrize("pmt, ahorro, serv, susc, ocio, estado_esp, alerta_esp", [
    (50, 100, 50, 50, 50, "EJERCICIO_DEFICIT", []),              
    (120, 100, 50, 50, 50, "EJERCICIO_DEFICIT", ["Déficit detectado en Servicios"]), 
    (170, 100, 50, 50, 50, "EJERCICIO_DEFICIT", ["Déficit detectado en Suscripciones"]), 
    (220, 100, 50, 50, 50, "EJERCICIO_DEFICIT", ["Déficit detectado en Ocio"]), 
    (300, 100, 50, 50, 50, "EJERCICIO", [])                     
])
def test_prioridades_presupuesto(pmt, ahorro, serv, susc, ocio, estado_esp, alerta_esp):
    estado, alertas = validar_presupuesto(pmt, ahorro, serv, susc, ocio)
    assert estado == estado_esp
    assert alertas == alerta_esp