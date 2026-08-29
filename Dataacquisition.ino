#include <Wire.h>

const byte MPU6050_ADDRESS = 0x68;

int16_t Rax, Ray, Raz;
int16_t Rgx, Rgy, Rgz;

float ax, ay, az;
float gx, gy, gz;

const float AX_OFFSET = 148.66;
const float AY_OFFSET = -80.82;
const float AZ_OFFSET = 948.22;

const float GX_OFFSET = 283.06;
const float GY_OFFSET = 214.34;
const float GZ_OFFSET = 132.27;

const int VOLTAGE_PIN = PC1 ;
const float VOLTAGE_DIVIDER_RATIO = 11 ;
const float ADC_REFERENCE = 5.0;

const int CURRENT_PIN = PC0 ;
const float ZERO_CURRENT_VOLTAGE = 2.5;
const float ACS712_SENSITIVITY = 0.185;

float readVoltage()
{
  int adcValue = analogRead(VOLTAGE_PIN);
  float adcVoltage = (adcValue * ADC_REFERENCE) / 1023.0;
  float batteryVoltage = adcVoltage * VOLTAGE_DIVIDER_RATIO;
  return batteryVoltage;
}

float readCurrent()
{
  int adcValue = analogRead(CURRENT_PIN);
  float sensorVoltage = (adcValue * ADC_REFERENCE) / 1023.0;
  float current = (sensorVoltage - ZERO_CURRENT_VOLTAGE) / ACS712_SENSITIVITY;
  return current;
}

void readMPU6050()
{
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU6050_ADDRESS, 14);

  if (Wire.available() >= 14)
  {
    Rax = (Wire.read() << 8) | Wire.read();
    Ray = (Wire.read() << 8) | Wire.read();
    Raz = (Wire.read() << 8) | Wire.read();

    Wire.read();
    Wire.read();

    Rgx = (Wire.read() << 8) | Wire.read();
    Rgy = (Wire.read() << 8) | Wire.read();
    Rgz = (Wire.read() << 8) | Wire.read();

    float calibratedRax = Rax - AX_OFFSET;
    float calibratedRay = Ray - AY_OFFSET;
    float calibratedRaz = Raz - AZ_OFFSET;

    float calibratedRgx = Rgx - GX_OFFSET;
    float calibratedRgy = Rgy - GY_OFFSET;
    float calibratedRgz = Rgz - GZ_OFFSET;

    ax = calibratedRax / 16384.0;
    ay = calibratedRay / 16384.0;
    az = calibratedRaz / 16384.0;

    gx = calibratedRgx / 131.0;
    gy = calibratedRgy / 131.0;
    gz = calibratedRgz / 131.0;
  }
}

void setup()
{
  Serial.begin(9600);
  Wire.begin();

  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  Serial.println("System Started");
}

void loop()
{
  readMPU6050();

  float voltage = readVoltage();
  float current = readCurrent();

  Serial.print("V: ");
  Serial.print(voltage, 2);

  Serial.print(" V, I: ");
  Serial.print(current, 2);

  Serial.print(" A, AX: ");
  Serial.print(ax, 3);

  Serial.print(", AY: ");
  Serial.print(ay, 3);

  Serial.print(", AZ: ");
  Serial.print(az, 3);

  Serial.print(", GX: ");
  Serial.print(gx, 3);

  Serial.print(", GY: ");
  Serial.print(gy, 3);

  Serial.print(", GZ: ");
  Serial.println(gz, 3);

  delay(500);
}