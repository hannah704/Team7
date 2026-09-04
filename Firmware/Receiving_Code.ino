#include <SoftwareSerial.h>
SoftwareSerial BT(10, 11);
#define size 15
#define lost_connection 5000

char command_Buffer[size];   // a temporary holding area with size 15 elements (15 empty boxes), where iam going to fill it with the letters of an incoming moving command, one at a time[cite: 1]

uint8_t command_length = 0;          //[cite: 1]
// Its job is to keep count: how many of those 15 boxes have already filled? It starts at 0 because when the chip first turns on, nothing has arrived yet[cite: 1]
// the uint8_t : u = unsigned (meaning: no negative numbers allowed, only zero and positive), int = integer (a whole number, no decimals), 8 = 8 bits of memory, t = type (just a naming convention, means "this is a type")[cite: 1]
// this is a built in, fixed command which says that : store in command_length a whole number, 0 or positive only, stored using exactly 8 bits of memory[cite: 1]

unsigned long lastCommandTime = 0; // it remembers at what moment in time (measured in milliseconds from the chip turned on) we last received a full, complete command from the station[cite: 1]

bool stop_the_motor = false; //[cite: 1]

// Function prototypes to inform the compiler before loop() calls them
void handleCommand(char *line);
void executeMove(char *dir, int speed);
void stopMotors();

void setup()
{
  Serial.begin(9600); //[cite: 1]
  BT.begin(9600);
}

void loop() {
  while(BT.available()) 
// this loop works and read each letter arrived from HC-05 when the answer of the question : { are there any letters that have arrived from HC-05 ? } isn't zero or false[cite: 1]
  {
    char c = BT.read();  // grabs exactly one waiting letter (the next one in line) and save it, every time this while loop starts, c becomes the next letter that arrived[cite: 1]
    
    if (c == '\n')  // checks if the letter sent is a new line or not, which an indicator of where the line ends[cite: 1] 
// If c is this newline (\n), we go into this block, which means a full command has just finished arriving[cite: 1]
    {
      command_Buffer[command_length] = '\0'; //this means add '/0' to the end of the command we just checked it finished, the '/0' tells any code that later reads command_Buffer: this is where the actual text ends and don't look any further[cite: 1]
      if(command_length > 0)
      // This checks that if we actually collect at least one real character before the newline arrived[cite: 1]
      {
        handleCommand(command_Buffer); //[cite: 1]
        lastCommandTime = millis();   // remember when we last heard from the GUI and gives us how many milliseconds since the chip turned on, to remember exactly when this command arrived[cite: 1]
      }
      command_length = 0; //[cite: 1]
      
    } else if (c != '\r') // the \r is called carriage return --> which means read the line after me from the start (like the old typewriters)[cite: 1]
    // if the command contain /r at its end ignore it, it doesn't a character will be saved in c[cite: 1] 
    {
      if (command_length < size - 1)            // must check that my command_length is much smaller than the available size in the array of command_Buffer[cite: 1]
      {
        command_Buffer[command_length++] = c;   // means add this new character which saved in c (after we checked it is not \n or \r ) to a new empty box in the command_Buffer[cite: 1]
      } else // what if the command sent is too long (more than 15 characters) ? --> then ignore it and reset the command_length to 0 which will start typing in command_Buffer from 1st element[cite: 1]
       {
        command_length = 0; //[cite: 1]
      }
    }
  }
  
  // safety check --> if too long has passed since the last command, force stop[cite: 1]
  if (millis() - lastCommandTime > lost_connection) 
  // This part runs every single time the loop starts, not just when letter arrives[cite: 1]
  // [millis() - lastCommandTime] --> calculates how much time has passed since the last full command we received.[cite: 1]
  // If that gap is bigger than [lost_connection] which = 1 second , then it calls stopMotors to stop the car[cite: 1]
  {
    if(!stop_the_motor) //[cite: 1]
    {
      stopMotors(); //[cite: 1]
      stop_the_motor = true; //[cite: 1]
    }
  } else
  {
      stop_the_motor = false; //[cite: 1]
  }
  

} // Fixed: Added missing closing brace for loop()[cite: 1]

void handleCommand(char *line)
{
  if (line[0] == 'M' && line[1] == ',') // the command will be in like of (M,FL,2\n) or (M,F,2\n)[cite: 1]
  // where M --> means Move, FL--> Forward Left & F--> Forward, 2--> the speed we want[cite: 1]
  {
   
  char dir[3] = {0, 0, 0};   // it creates an array where its elements initially are 0[cite: 1]
  uint8_t i = 2;             //[cite: 1]
  uint8_t d = 0;             //[cite: 1]

  while (line[i] != ',' && line[i] != '\0' && d < 2) //[cite: 1]
  // i = 2 then in the example i put line[i] = line[2] = F, then it is not a comma or '\0', d = 0 initially[cite: 1] 
  {
    dir[d] = line[i]; // this means that put 'F' as the dir [0] so now dir = {'F',0,0}[cite: 1]
    d++;  //[cite: 1]
    i++; //[cite: 1]
    // now d = 1 and i = 3 , if the loop runs again dir will be = {'F', 'L', 0}, and when it runs again i will be i = ',' which make the conditions of if is false[cite: 1]
    // now dir will give value "FL"[cite: 1]
  }
    int speed = 0; //[cite: 1]
    if (line[i] == ',') // after the loop finished, the i =','[cite: 1]
    {
      speed = atoi(&line[i+1]); //[cite: 1]
      // atoi--> built in C function, converts the string (which is the speed value) into a real integer[cite: 1]
    }
  executeMove(dir, speed); //[cite: 1]
  }
}

void executeMove(char *dir, int speed)
// strcmp--> means string compare, it compares the value of dir (which determined in the handleCommand function) with the string i give it[cite: 1]
// but important note i discovered and cause error to me, strcmp returns 0 if the two strings are matching, and will turns +ve or *ve number if they are not matching[cite: 1]
{
  if (speed == 0) //[cite: 1]
  {
    // will be modified[cite: 1]
  } else if (speed == 3) //[cite: 1]
  {
    Serial.println("Low Speed"); //[cite: 1]
  } else if (speed == 6) //[cite: 1]
  {
    Serial.println("Medium Speed"); //[cite: 1]
  } else if (speed == 9) //[cite: 1]
  {
    Serial.println("High Speed"); //[cite: 1]
  }


  if (strcmp(dir, "F") == 0) //[cite: 1]
  {
    Serial.println("Moving Forward"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "B") == 0) //[cite: 1]
  {
    Serial.println("Moving Backward"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "L") == 0) //[cite: 1]
  {
    Serial.println("Moving Left"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "R") == 0) //[cite: 1]
  {
    Serial.println("Moving Right"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "FL") == 0) //[cite: 1]
  {
    Serial.println("Moving Forward-Left"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "FR") == 0) //[cite: 1]
  {
    Serial.println("Moving Forward-Right"); //[cite: 1]
    // Will be filled Later[cite: 1] 
  } else if (strcmp(dir, "BL") == 0) //[cite: 1]
  {
    Serial.println("Moving Backward-Left"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "BR") == 0) //[cite: 1]
  {
    Serial.println("Moving Backward-Right"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else if (strcmp(dir, "S") == 0) //[cite: 1]
  {
    Serial.println("STOP!!"); //[cite: 1]
    // Will be filled Later[cite: 1]
  } else {

  }

}

void stopMotors() //[cite: 1]
{
  executeMove("S",0); //[cite: 1]
}