import time
import random

# DATOS DEL PRODUCTO (Input)
producto = "Aspiradora TurboCar Pro"
dolor_cliente = "Auto sucio y poco tiempo"

print(f"--- INICIANDO MOTOR DE IA PARA: {producto} ---")
print("1. Escaneando tendencias en TikTok y Reels...")
time.sleep(2) # Simula tiempo de pensamiento
print("   > Tendencia detectada: #CarHacks (Visual Satisfactory)")
print("   > Tendencia detectada: #ASMRCleaning")

print("\n2. Analizando competencia en Chile...")
time.sleep(1)
print("   > Precio promedio detectado: $29.990")
print("   > Oportunidad: Vender a $24.990 (Oferta agresiva)")

print("\n3. Generando Guiones de Anuncios Virales...")
time.sleep(2)

# Simulación de generación de contenido
guiones = [
    f"Opción 1 (Humor): ¿Tu auto parece basurero? {producto} lo limpia en 10 seg.",
    f"Opción 2 (ASMR): Solo escucha el sonido de la potencia. Satisfacción pura con {producto}.",
    f"Opción 3 (Urgencia): ¡Últimas unidades! No pagues $30mil, lleva la {producto} hoy."
]

print("\n--- RESULTADOS GENERADOS POR IA ---")
for guion in guiones:
    print(f"[IA COPY]: {guion}")

print("\nGuardando reporte en 'estrategia.txt'...")
with open("estrategia.txt", "w", encoding="utf-8") as f:
    f.write(f"Estrategia generada para {producto}\n")
    for guion in guiones:
        f.write(guion + "\n")

print("¡Listo! Automatización completada.")