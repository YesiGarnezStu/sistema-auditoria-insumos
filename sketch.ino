// Definir los pines de los LEDs
const int led1 = 32;
const int led2 = 33;

void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
  // Encender el LED 1 y apagar el LED 2
  digitalWrite(led1, HIGH);
  digitalWrite(led2, LOW);
  delay(1000); // Esperar un segundo

  // Apagar el LED 1 y encender el LED 2
  digitalWrite(led1, LOW);
  digitalWrite(led2, HIGH);
  delay(1000); // Esperar un segundo
}
