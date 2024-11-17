// Pines del Joystick Shield
const int pinX = A0;  // Eje X del joystick (analógico)
const int pinY = A1;  // Eje Y del joystick (analógico)
const int buttonY = 2;  // Botón del joystick (digital)
const int buttonB = 3;  // Botón adicional 1
const int buttonA = 4;  // Botón adicional 2
const int buttonX = 5;  // Botón adicional 3
const int buttonSELECT = 6;  // Botón adicional 4

void setup() {
  // Configurar pines
  pinMode(buttonY, INPUT_PULLUP);         // Boton Y
  pinMode(buttonB, INPUT_PULLUP);         // Botón B
  pinMode(buttonA, INPUT_PULLUP);         // Botón A
  pinMode(buttonX, INPUT_PULLUP);         // Botón X
  pinMode(buttonSELECT, INPUT_PULLUP);    // Botón SELECT
  
  // Inicializar comunicación serial
  Serial.begin(9600);
}

void loop() {
  // Leer valores analógicos del joystick
  int xValue = analogRead(pinX);  // Leer el eje X
  int yValue = analogRead(pinY);  // Leer el eje Y
  
  // Leer estado de los botones
  bool isbuttonYPressed = !digitalRead(buttonY);  // Invertir porque se usa INPUT_PULLUP
  bool isButtonBPressed = !digitalRead(buttonB);
  bool isButtonAPressed = !digitalRead(buttonA);
  bool isButtonXPressed = !digitalRead(buttonX);
  bool isButtonSELECTPressed = !digitalRead(buttonSELECT);

  // Imprimir los valores en el monitor serial
  Serial.print("Eje X: ");
  Serial.print(xValue);
  Serial.print("\tEje Y: ");
  Serial.print(yValue);

  // Verificar botones
  if (isbuttonYPressed) {
    Serial.print("\tBotón Y: PRESIONADO");
  }
  if (isButtonBPressed) {
    Serial.print("\tBotón B: PRESIONADO");
  }
  if (isButtonAPressed) {
    Serial.print("\tBotón A: PRESIONADO");
  }
  if (isButtonXPressed) {
    Serial.print("\tBotón X: PRESIONADO");
  }
  if (isButtonSELECTPressed) {
    Serial.print("\tBotón SELECT: PRESIONADO");
  }

  Serial.println();  // Nueva línea para mayor claridad

  delay(100);  // Pausa para facilitar la lectura en el monitor serial
}

