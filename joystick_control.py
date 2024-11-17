import serial
import time

# Configuración del puerto serie
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)  

# Configuración de la zona muerta
DEAD_ZONE = 10  # Rango en el que se ignoran los pequeños cambios 

# Últimos valores válidos (para evitar fluctuaciones menores)
last_x = 518  # Valor neutro aproximado del eje X
last_y = 497  # Valor neutro aproximado del eje Y

def read_joystick():
    global last_x, last_y  # Usamos variables globales para conservar el último estado
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        try:
            xValue, yValue, buttonY, buttonB, buttonA, buttonX, buttonSELECT = map(int, data.split(","))
            
            # Filtro de zona muerta para X
            if abs(xValue - last_x) > DEAD_ZONE:  # Si el cambio es mayor que la zona muerta
                last_x = xValue  # Actualiza el último valor válido
            else:
                xValue = last_x  # Usa el último valor válido

            # Filtro de zona muerta para Y
            if abs(yValue - last_y) > DEAD_ZONE:  # Si el cambio es mayor que la zona muerta
                last_y = yValue  # Actualiza el último valor válido
            else:
                yValue = last_y  # Usa el último valor válido

            # Retorna los valores filtrados
            return {
                "x": xValue,
                "y": yValue,
                "buttonY": buttonY,
                "buttonB": buttonB,
                "buttonA": buttonA,
                "buttonX": buttonX,
                "buttonSELECT": buttonSELECT,
            }
        except ValueError:
            print("Error al procesar los datos del joystick.")
            return None
    return None


  


