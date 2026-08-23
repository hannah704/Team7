const int VOLTAGE_PIN = A0;

// i will change this later 
const float VOLTAGE_DIVIDER_RATIO = 2.0;
// i will change this later 

const float ADC_REFERENCE = 5.0;
// i will change this later 

// a function  that reads the adc value and returns the real voltage value 
float readVoltage()
{
  int adcValue = analogRead(VOLTAGE_PIN);
// this equation turns the adc digital number to a voltage number  
  float adcVoltage =
      (adcValue * ADC_REFERENCE) / 1023.0;
// this equation undo the voltage divider 
  float batteryVoltage =
      adcVoltage * VOLTAGE_DIVIDER_RATIO;

  return batteryVoltage;
}

// a function to start serial communication 
void setup()
{
  Serial.begin(9600);
}

// a loop to keep reading the voltage value when it changes 
void loop()
{
  float voltage = readVoltage();
 Serial.print("V:");
 Serial.println(voltage);

  delay(1000);
}
