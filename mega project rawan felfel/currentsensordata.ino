const int CURRENT_PIN = A1;

const float ADC_REFERENCE = 5.0;
const float ZERO_CURRENT_VOLTAGE = 2.5;
const float ACS712_SENSITIVITY = 0.185;

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  int adcValue = analogRead(CURRENT_PIN);

  float sensorVoltage =
      (adcValue * ADC_REFERENCE) / 1023.0;

  float current =
      (sensorVoltage - ZERO_CURRENT_VOLTAGE)
      / ACS712_SENSITIVITY;

  Serial.print("I:");
  Serial.println(current);

  delay(100);
}
