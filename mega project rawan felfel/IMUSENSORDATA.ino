#include <Wire.h>

const byte MPU6050_ADDRESS = 0x68;
int16_t ax;
int16_t ay;
int16_t az;
int16_t gx;
int16_t gy;
int16_t gz;

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
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDRESS,14);
  ax = (Wire.read() << 8) | Wire.read();
  ay = (Wire.read() << 8) | Wire.read();
  az = (Wire.read() << 8) | Wire.read();
  Wire.read();
  Wire.read();
  gx = (Wire.read() << 8) | Wire.read();
  gy = (Wire.read() << 8) | Wire.read();
  gz = (Wire.read() << 8) | Wire.read();
  Serial.print("AX:");
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


