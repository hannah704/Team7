#include <Wire.h>

const byte MPU6050_ADDRESS = 0x68;

const int VOLTAGE_PIN = A0;
const int CURRENT_PIN = A1;

const float VOLTAGE_DIVIDER_RATIO = 11;
const float ADC_REFERENCE = 5.0;
const float ZERO_CURRENT_VOLTAGE = 2.5;
const float ACS712_SENSITIVITY = 0.185;

int16_t ax;
int16_t ay;
int16_t az;
int16_t gx;
int16_t gy;
int16_t gz;

float readVoltage()
{
  int adcValue = analogRead(VOLTAGE_PIN);

  float adcVoltage =
      (adcValue * ADC_REFERENCE) / 1023.0;

  float batteryVoltage =
      adcVoltage * VOLTAGE_DIVIDER_RATIO;

  return batteryVoltage;
}

void setup()
{
  Serial.begin(9600);

  Wire.begin();

  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
}

void loop()
{
  float voltage = readVoltage();

  int currentADC = analogRead(CURRENT_PIN);

  float sensorVoltage =
      (currentADC * ADC_REFERENCE) / 1023.0;

  float current =
      (sensorVoltage - ZERO_CURRENT_VOLTAGE)
      / ACS712_SENSITIVITY;

  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU6050_ADDRESS, (byte)14);

  ax = (Wire.read() << 8) | Wire.read();
  ay = (Wire.read() << 8) | Wire.read();
  az = (Wire.read() << 8) | Wire.read();

  Wire.read();
  Wire.read();

  gx = (Wire.read() << 8) | Wire.read();
  gy = (Wire.read() << 8) | Wire.read();
  gz = (Wire.read() << 8) | Wire.read();

  Serial.print("V:");
  Serial.print(voltage);

  Serial.print(",I:");
  Serial.print(current);

  Serial.print(",AX:");
  Serial.print(ax);

  Serial.print(",AY:");
  Serial.print(ay);

  Serial.print(",AZ:");
  Serial.print(az);

  Serial.print(",GX:");
  Serial.print(gx);

  Serial.print(",GY:");
  Serial.print(gy);

  Serial.print(",GZ:");
  Serial.println(gz);

  delay(100);
}
