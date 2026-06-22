from guardian import PayFlowGuardian

def imprimir_encabezado():
    print("\n" + "=" * 50)
    print("PAYFLOW: GUARDIÁN DE SUSCRIPCIONES")
    print("=" * 50)

def mostrar_estado(guardian):
    print("\n--- ESTADO ACTUAL ---")
    print(f"Saldo Disponible: ${guardian.saldo_actual:.2f}")
    print(f"Suscripciones Pendientes: ${guardian.suscripciones_pendientes:.2f}")
    print(
        f"Gastos Variables (Ejecutado / Proyectado): "
        f"${guardian.gastos_variables_mes:.2f} / "
        f"${guardian.proyeccion_variables:.2f}"
    )
    print(f"Estado de Salud: {guardian.estado}")

    if guardian.alertas:
        print("\nALERTAS ACTIVAS:")
        for alerta in guardian.alertas:
            print(f" - {alerta}")

    print("---------------------\n")

def iniciar_cli():
    imprimir_encabezado()

    while True:
        try:
            pmt = float(input("Ingresa tu Presupuesto Mensual Total (PMT): $"))

            if pmt <= 0:
                print("El PMT debe ser mayor a 0.")
                continue

            break

        except ValueError:
            print("Por favor, ingresa un número válido.")

    guardian = PayFlowGuardian(pmt)

    while True:
        mostrar_estado(guardian)

        print("¿Qué operación deseas realizar?")
        print("1. Configurar Meta de Ahorro")
        print("2. Registrar Suscripción Futura (Fija)")
        print("3. Establecer Proyección de Gastos Variables")
        print("4. Registrar Gasto Regular")
        print("5. Registrar Gasto de Ocio")
        print("6. Ejecutar Cobro de Suscripción")
        print("7. Ejecutar Corte de Caja y Salir")

        opcion = input("\nElige una opción (1-7): ")

        try:
            if opcion == '1':
                monto = float(input("Monto de la meta de ahorro: $"))
                guardian.configurar_ahorro(monto)
                print("Ahorro configurado.")

            elif opcion == '2':
                monto = float(input("Costo de la suscripción futura: $"))
                guardian.registrar_suscripcion_futura(monto)
                print("Suscripción registrada.")

            elif opcion == '3':
                monto = float(
                    input(
                        "¿Cuánto proyectas gastar en servicios variables este mes?: $"
                    )
                )
                guardian.establecer_proyeccion_variables(monto)
                print("Proyección de variables establecida.")

            elif opcion == '4':
                monto = float(input("Monto del gasto regular: $"))
                guardian.registrar_gasto(monto)
                print("Gasto registrado y acumulado en variables.")

            elif opcion == '5':
                monto = float(input("Monto del gasto de ocio: $"))
                promedio = float(input("Tu promedio histórico para ocio es: $"))
                guardian.registrar_gasto_ocio(monto, promedio)
                print("Gasto de ocio registrado.")

            elif opcion == '6':
                if guardian.suscripciones_pendientes == 0:
                    print("No hay suscripciones pendientes por cobrar.")
                    continue

                print(
                    f"\nTienes ${guardian.suscripciones_pendientes} "
                    "en suscripciones."
                )

                monto_cobro = float(
                    input("¿Cuánto vas a procesar ahora?: $")
                )

                es_vip = input(
                    "¿El usuario es VIP? (s/n): "
                ).lower() == 's'

                cuenta_activa = input(
                    "¿La cuenta está activa? (s/n): "
                ).lower() == 's'

                tarjeta_vencida = input(
                    "¿La tarjeta está vencida? (s/n): "
                ).lower() == 's'

                resultado = guardian.ejecutar_cobro_suscripcion(
                    monto_cobro,
                    es_vip,
                    cuenta_activa,
                    tarjeta_vencida
                )

                print(f"Resultado del cobro: {resultado.upper()}")

            elif opcion == '7':
                print("\n" + "=" * 50)
                print("EJECUTANDO CORTE DE CAJA...")

                reporte = guardian.ejecutar_corte_de_caja()

                print(f"Saldo Final del Mes: ${reporte['saldo_final']:.2f}")
                print(f"Estado Final: {reporte['estado_final']}")
                print(
                    f"Alertas generadas en el mes: "
                    f"{len(reporte['alertas_mes'])}"
                )

                print("\nREPORTE DE VARIABILIDAD:")

                var = reporte["reporte_variabilidad"]

                print(f"   - Proyectado: ${var['proyectado']:.2f}")
                print(f"   - Ejecutado:  ${var['ejecutado']:.2f}")

                if var["diferencia"] < 0:
                    print(
                        f"   Gastaste "
                        f"${abs(var['diferencia']):.2f} "
                        f"MÁS de lo proyectado (Déficit)."
                    )

                elif var["diferencia"] > 0:
                    print(
                        f"   Ahorraste "
                        f"${var['diferencia']:.2f} "
                        f"sobre tu proyección (Superávit)."
                    )

                else:
                    print("   Gastaste exactamente lo proyectado.")

                print("=" * 50)
                print("Gracias por usar PayFlow Guardian!\n")

                break

            else:
                print("Opción no válida. Intenta de nuevo.")

        except ValueError as e:
            print(f"\nERROR DE REGLA DE NEGOCIO: {e}")

        except Exception:
            print("\nEntrada inválida. Usa el formato correcto.")

if __name__ == "__main__":
    iniciar_cli()