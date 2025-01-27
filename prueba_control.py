import serial

# Configuración del puerto serial (ajusta 'COM3' según el puerto que estés utilizando)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

print("Esperando datos del Arduino... Presiona Ctrl+C para detener el programa.")

try:
    while True:
        if arduino.in_waiting > 0:  # Verifica si hay datos en el buffer serial
            # Leer datos del puerto serial
            data = arduino.readline().decode('utf-8').strip()
            
            # Mostrar los datos en la terminal
            print(f"Datos recibidos: {data}")
except KeyboardInterrupt:
    print("Programa terminado.")
finally:
    arduino.close()
