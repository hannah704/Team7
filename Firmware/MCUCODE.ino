#include <SoftwareSerial.h>
#include <Wire.h>

SoftwareSerial BT(10, 11);
#define size 15
#define lost_connection 5000

char command_Buffer[size];   // a temporary holding area with size 15 elements (15 empty boxes), where iam going to fill it with the letters of an incoming moving command, one at a time

uint8_t command_length = 0;
// Its job is to keep count: how many of those 15 boxes have already filled? It starts at 0 because when the chip first turns on, nothing has arrived yet
// the uint8_t : u = unsigned (meaning: no negative numbers allowed, only zero and positive), int = integer (a whole number, no decimals), 8 = 8 bits of memory, t = type (just a naming convention, means "this is a type")
// this is a built in, fixed command which says that : store in command_length a whole number, 0 or positive only, stored using exactly 8 bits of memory

unsigned long lastCommandTime = 0; // it remembers at what moment in time (measured in milliseconds from the chip turned on) we last received a full, complete command from the station

bool stop_the_motor = false;


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

const int VOLTAGE_PIN = PC1;
const float VOLTAGE_DIVIDER_RATIO = 11;
const float ADC_REFERENCE = 5.0;

const int CURRENT_PIN = PC0;
const float ZERO_CURRENT_VOLTAGE = 2.5;
const float ACS712_SENSITIVITY = 0.185;

#define sensor_interval 500          // how often (ms) we read + send sensor data
unsigned long lastSensorTime = 0;    // non-blocking replacement for the old delay(500)

// Function prototypes to inform the compiler before loop() calls them
void handleCommand(char *line);
void executeMove(char *dir, int speed);
void stopMotors();
void readMPU6050();
float readVoltage();
float readCurrent();
void readAndSendSensors();

void setup()
{
  Serial.begin(9600);
  BT.begin(9600);

  Wire.begin();
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  Serial.println("System Started");
}

void loop() {
  while(BT.available())
  // this loop works and read each letter arrived from HC-05 when the answer of the question : { are there any letters that have arrived from HC-05 ? } isn't zero or false
  {
    char c = BT.read();  // grabs exactly one waiting letter (the next one in line) and save it, every time this while loop starts, c becomes the next letter that arrived

    if (c == '\n')  // checks if the letter sent is a new line or not, which an indicator of where the line ends
    // If c is this newline (\n), we go into this block, which means a full command has just finished arriving
    {
      command_Buffer[command_length] = '\0'; //this means add '/0' to the end of the command we just checked it finished, the '/0' tells any code that later reads command_Buffer: this is where the actual text ends and don't look any further
      if(command_length > 0)
      // This checks that if we actually collect at least one real character before the newline arrived
      {
        handleCommand(command_Buffer);
        lastCommandTime = millis();   // remember when we last heard from the GUI and gives us how many milliseconds since the chip turned on, to remember exactly when this command arrived
      }
      command_length = 0;

    } else if (c != '\r') // the \r is called carriage return --> which means read the line after me from the start (like the old typewriters)
    // if the command contain /r at its end ignore it, it doesn't a character will be saved in c
    {
      if (command_length < size - 1)            // must check that my command_length is much smaller than the available size in the array of command_Buffer
      {
        command_Buffer[command_length++] = c;   // means add this new character which saved in c (after we checked it is not \n or \r ) to a new empty box in the command_Buffer
      } else // what if the command sent is too long (more than 15 characters) ? --> then ignore it and reset the command_length to 0 which will start typing in command_Buffer from 1st element
       {
        command_length = 0;
      }
    }
  }

  // safety check --> if too long has passed since the last command, force stop
  if (millis() - lastCommandTime > lost_connection)
  // This part runs every single time the loop starts, not just when letter arrives
  // [millis() - lastCommandTime] --> calculates how much time has passed since the last full command we received.
  // If that gap is bigger than [lost_connection] which = 1 second , then it calls stopMotors to stop the car
  {
    if(!stop_the_motor)
    {
      stopMotors();
      stop_the_motor = true;
    }
  } else
  {
      stop_the_motor = false;
  }

  // --- DAQ: read sensors and send to station on a timer, without blocking the command loop above ---
  if (millis() - lastSensorTime >= sensor_interval)
  {
    readAndSendSensors();
    lastSensorTime = millis();
  }

} // Fixed: Added missing closing brace for loop()

void handleCommand(char *line)
{
  if (line[0] == 'M' && line[1] == ',') // the command will be in like of (M,FL,2\n) or (M,F,2\n)
  // where M --> means Move, FL--> Forward Left & F--> Forward, 2--> the speed we want
  {

  char dir[3] = {0, 0, 0};   // it creates an array where its elements initially are 0
  uint8_t i = 2;
  uint8_t d = 0;

  while (line[i] != ',' && line[i] != '\0' && d < 2)
  // i = 2 then in the example i put line[i] = line[2] = F, then it is not a comma or '\0', d = 0 initially
  {
    dir[d] = line[i]; // this means that put 'F' as the dir [0] so now dir = {'F',0,0}
    d++;
    i++;
    // now d = 1 and i = 3 , if the loop runs again dir will be = {'F', 'L', 0}, and when it runs again i will be i = ',' which make the conditions of if is false
    // now dir will give value "FL"
  }
    int speed = 0;
    if (line[i] == ',') // after the loop finished, the i =','
    {
      speed = atoi(&line[i+1]);
      // atoi--> built in C function, converts the string (which is the speed value) into a real integer
    }
  executeMove(dir, speed);
  }
}

void executeMove(char *dir, int speed)
// strcmp--> means string compare, it compares the value of dir (which determined in the handleCommand function) with the string i give it
// but important note i discovered and cause error to me, strcmp returns 0 if the two strings are matching, and will turns +ve or *ve number if they are not matching
{
  if (speed == 0)
  {
    // will be modified
  } else if (speed == 3)
  {
    Serial.println("Low Speed");
  } else if (speed == 6)
  {
    Serial.println("Medium Speed");
  } else if (speed == 9)
  {
    Serial.println("High Speed");
  }


  if (strcmp(dir, "F") == 0)
  {
    Serial.println("Moving Forward");
    // Will be filled Later
  } else if (strcmp(dir, "B") == 0)
  {
    Serial.println("Moving Backward");
    // Will be filled Later
  } else if (strcmp(dir, "L") == 0)
  {
    Serial.println("Moving Left");
    // Will be filled Later
  } else if (strcmp(dir, "R") == 0)
  {
    Serial.println("Moving Right");
    // Will be filled Later
  } else if (strcmp(dir, "FL") == 0)
  {
    Serial.println("Moving Forward-Left");
    // Will be filled Later
  } else if (strcmp(dir, "FR") == 0)
  {
    Serial.println("Moving Forward-Right");
    // Will be filled Later
  } else if (strcmp(dir, "BL") == 0)
  {
    Serial.println("Moving Backward-Left");
    // Will be filled Later
  } else if (strcmp(dir, "BR") == 0)
  {
    Serial.println("Moving Backward-Right");
    // Will be filled Later
  } else if (strcmp(dir, "S") == 0)
  {
    Serial.println("STOP!!");
    // Will be filled Later
  } else {

  }

}

void stopMotors()
{
  executeMove("S",0);
}

// ---------------- DAQ (sensor) functions ----------------

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

void readAndSendSensors()
{
  readMPU6050();

  float voltage = readVoltage();
  float current = readCurrent();

  
  BT.print("I: ");
  BT.print(current, 2);

  BT.print(" A, V: ");
  BT.print(voltage, 2);

  BT.print(" V, AX: ");
  BT.print(ax, 3);

  BT.print(", AY: ");
  BT.print(ay, 3);

  BT.print(", AZ: ");
  BT.print(az, 3);

  BT.print(", GX: ");
  BT.print(gx, 3);

  BT.print(", GY: ");
  BT.print(gy, 3);

  BT.print(", GZ: ");
  BT.println(gz, 3);

  // Same line, also printed to the USB Serial Monitor for local debugging.
  Serial.print("I: ");
  Serial.print(current, 2);

  Serial.print(" A, V: ");
  Serial.print(voltage, 2);

  Serial.print(" V, AX: ");
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
}
