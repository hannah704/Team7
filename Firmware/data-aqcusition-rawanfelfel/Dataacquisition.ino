// I2C library - this lets the Arduino "talk" to sensors over just 2 wires (SDA and SCL)
#include <Wire.h>

const byte MPU6050_ADDRESS = 0x68; // the "address" of the MPU6050 sensor on the I2C wires, so the Arduino knows which device it's talking to

int16_t Rax, Ray, Raz; // "raw" accelerometer readings (X, Y, Z) - straight from the sensor, not converted into real units yet
int16_t Rgx, Rgy, Rgz; // "raw" gyroscope readings (X, Y, Z) - also straight from the sensor, not converted yet

float ax, ay, az; // the final accelerometer readings, in real units (g's), after cleaning up the raw values
float gx, gy, gz; // the final gyroscope readings, in real units (degrees per second), after cleaning up the raw values

// Every sensor has a tiny built-in error even when it's sitting still, called "bias" or "offset"
// These numbers were measured beforehand (by reading the sensor at rest) and are subtracted later
// so that 0 really means 0, instead of some small leftover number
const float AX_OFFSET = 148.66;
const float AY_OFFSET = -80.82;
const float AZ_OFFSET = 948.22;

const float GX_OFFSET = 283.06;
const float GY_OFFSET = 214.34;
const float GZ_OFFSET = 132.27;

const int VOLTAGE_PIN = PC1;              // which pin the battery voltage sensor is connected to
const float VOLTAGE_DIVIDER_RATIO = 11;   // the voltage sensor scales the real battery voltage down by this much, so we multiply back up to get the true value
const float ADC_REFERENCE = 5.0;          // the Arduino's analog pins measure voltage between 0 and this reference value

const int CURRENT_PIN = PC0;                 // which pin the current sensor is connected to
const float ZERO_CURRENT_VOLTAGE = 2.5;      // the voltage the current sensor outputs when there is 0 A flowing 
const float ACS712_SENSITIVITY = 0.185;      // how many volts the current sensor's output changes for every 1 A of current (from its datasheet)

// Reads the battery voltage and converts it into a real voltage number
float readVoltage()
{
  int adcValue = analogRead(VOLTAGE_PIN);                      // read the raw number (0-1023) the Arduino sees on this pin
  float adcVoltage = (adcValue * ADC_REFERENCE) / 1023.0;      // convert that raw number into an actual voltage 
  float batteryVoltage = adcVoltage * VOLTAGE_DIVIDER_RATIO;   // scale it back up, since the divider circuit shrank the real battery voltage
  return batteryVoltage;                                       // send this final voltage value back 
}

// Reads the current sensor and converts it into a real current number
float readCurrent()
{
  int adcValue = analogRead(CURRENT_PIN);                              // read the raw number (0-1023) the Arduino sees on this pin
  float sensorVoltage = (adcValue * ADC_REFERENCE) / 1023.0;           // convert that raw number into an actual voltage 
  float current = (sensorVoltage - ZERO_CURRENT_VOLTAGE) / ACS712_SENSITIVITY; // read accurate current
  return current;                                                      // send this final current value back 
}

// Talks to the MPU6050 sensor and fills in ax, ay, az, gx, gy, gz with fresh readings
void readMPU6050()
{
  Wire.beginTransmission(MPU6050_ADDRESS);  // start talking to the sensor
  Wire.write(0x3B);                          // tell the sensor: "I want to start reading from register 0x3B" (where the motion data begins)
  Wire.endTransmission(false);               // send that request, but keep the connection open for the next step

  Wire.requestFrom(MPU6050_ADDRESS, 14);     // ask the sensor for the next 14 bytes of data (accelerometer + temperature + gyroscope, all packed together)

  if (Wire.available() >= 14)  // only continue if all 14 bytes have actually arrived
  {
    // Each reading is sent as 2 bytes (a "high" byte and a "low" byte), so we combine them into one number
    Rax = (Wire.read() << 8) | Wire.read(); // raw acceleration on the X axis
    Ray = (Wire.read() << 8) | Wire.read(); // raw acceleration on the Y axis
    Raz = (Wire.read() << 8) | Wire.read(); // raw acceleration on the Z axis

    Wire.read(); // this pair of bytes is the sensor's internal temperature reading
    Wire.read(); // we're not using it, so just read and throw it away to stay in sync with the data

    Rgx = (Wire.read() << 8) | Wire.read(); // raw rotation speed around the X axis
    Rgy = (Wire.read() << 8) | Wire.read(); // raw rotation speed around the Y axis
    Rgz = (Wire.read() << 8) | Wire.read(); // raw rotation speed around the Z axis

    // Subtract each sensor's resting-state error (offset), measured earlier
    float calibratedRax = Rax - AX_OFFSET;
    float calibratedRay = Ray - AY_OFFSET;
    float calibratedRaz = Raz - AZ_OFFSET;

    float calibratedRgx = Rgx - GX_OFFSET;
    float calibratedRgy = Rgy - GY_OFFSET;
    float calibratedRgz = Rgz - GZ_OFFSET;

    // Divide by the sensor's scale factor to turn the raw numbers into real units (g's for acceleration)
    ax = calibratedRax / 16384.0;
    ay = calibratedRay / 16384.0;
    az = calibratedRaz / 16384.0;

    // Divide by the sensor's scale factor to turn the raw numbers into real units (degrees/second for rotation)
    gx = calibratedRgx / 131.0;
    gy = calibratedRgy / 131.0;
    gz = calibratedRgz / 131.0;
  }
}

void setup()
{
  Serial.begin(9600); // start communication with the computer (Serial Monitor) at 9600 baud
  Wire.begin();        // start the I2C connection so we can talk to the MPU6050

  // Wake the MPU6050 up - by default it powers on in "sleep mode" and won't send data until told otherwise
  Wire.beginTransmission(MPU6050_ADDRESS); // start talking to the sensor
  Wire.write(0x6B);                         // register 0x6B is the sensor's power management setting
  Wire.write(0x00);                         // writing 0 here tells it "wake up, stop sleeping"
  Wire.endTransmission();                   // send that instruction

  Serial.println("System Started"); // print a message so we know setup finished successfully
}

void loop()
{
  readMPU6050(); // get the latest accelerometer + gyroscope readings

  float voltage = readVoltage(); // get the latest battery voltage reading
  float current = readCurrent(); // get the latest current reading

  // Print everything on one line, one labeled value at a time, so it's easy to read on the Serial Monitor
  Serial.print("V: ");
  Serial.print(voltage, 2); // print with 2 decimal places

  Serial.print(" V, I: ");
  Serial.print(current, 2); // print with 2 decimal places

  Serial.print(" A, AX: ");
  Serial.print(ax, 3); // print with 3 decimal places

  Serial.print(", AY: ");
  Serial.print(ay, 3);

  Serial.print(", AZ: ");
  Serial.print(az, 3);

  Serial.print(", GX: ");
  Serial.print(gx, 3);

  Serial.print(", GY: ");
  Serial.print(gy, 3);

  Serial.print(", GZ: ");
  Serial.println(gz, 3); // println ends the line, so the next reading starts fresh below it

  delay(500); // wait half a second before taking the next set of readings
}
