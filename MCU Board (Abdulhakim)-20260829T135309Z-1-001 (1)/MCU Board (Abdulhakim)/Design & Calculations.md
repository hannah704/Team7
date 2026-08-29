###Design notes & calculations 
------------------------------
##Design notes 

-designed the board around instructables https://www.instructables.com/ATmega-DIP40-Minimal-Board/ design , the difference being that ATMEGA8A-PU is a DIP28 ic , which made it easier 
to route on 1 layer , but used female pin headers instead to be as close to an UNO as possible , left the ISP programming header away to not complicate the routing process even more
than it is 

-Placed each decoupling capacitor as close to the required trace as the layout allows ( +5v and gnd on the , avcc and gnd , aref and gnd ) as the official datasheet says https://www.alldatasheet.com/datasheet-pdf/pdf/313648/ATMEL/ATmega8A-PU.html

-Made all sensors except the IMU external ( the current and voltage sensor are on the power input itself , they do not need to be on the MCU board nor they need to be physically stable , while the IMU actually needs to be 
stable on the board to give stable readings while the car is moving , it cannot be just jumpered put like that on the car )

-did not design the sensors from scratch ( i didn't think it was possible to pull that off in one week , nor had the time to ) ( except the voltage sensor which is quite literally 2 resistors ) and bought them already built 


------------------------------------------------------------------------------------------------------------------
##Calculations 

-------------------starting with the sensors-----------------------------

-used the ACS712 5A current sensor , as we will be using a 4-motor chasis , each motor could pull minimally 200mA https://makerselectronics.com/product/dc-geared-wired-motor-dual-shaft-wh/ , for a max safety margin we could say it could pull 400mA , so 4x400 = 1.6 amps 
say the mcu board and the motor driver's internal components both could pull max of 400mA , so combined it will be a max of 2A , we are extremely safe using it

-for the voltage sensor , we will be using 2 resistors , 1k and 10k , so VIN>10K>MCU PIN>1K>GND , so the ratio for it will be 1/11 of the actual input voltage , very safe even if we use 4 LI batteries (4V max x 4 = 16 , 
16/11 about 1.46V , very safe and below the 5V max pin Voltage ) , we will also be using a 100nF ceramic cap from the mcu pin to GND to filter out the noise of the supply so we get a semi stable VIN for the divider.
   
-----------------Power input-------------------------

-used a simple LDO regulator (LM7805) to regulate the input voltage and considering the max VIN it could get is 16V we are very safe , it can also take up to 1.5A while the MCU Board could pull
at max 200mA so we are far below the limits , used a bulk 100uF cap on the VIN as that VIN is in parallel with the motors , so we get a clean , smoothed out DC voltage on the reg , 100uF is the common practical choice 
used a 10uF on the output voltage for better transient response , supplies current spikes ( if did happen ) fully and fast enough , chose it way above the datasheet's 0.1uF for this purpose , this is an MCU board after all we need stable output Voltage
went even after https://www.rs-online.com/designspark/reference-design-of-arduino-nano-3-0 's 4.7uF to make 100% sure the board works under any condition

-used a normal terminal block for the input , bulky and reliable , way more than needed specifications to be absoloutly fine , also for simple 2 wire connection instead of a jack

-LED indicator used a normal red LED with a simple 330ohm , 5/330 = about 15mA , safe and reliable for a 20mA max , good bright

----------------------MCU-----------------------------

-Power delivery comes from the decoupled voltage from the regulator , and used the standard 100nF decoupling cap that is used in almost every Embedded systems design https://www.es.co.th/Schemetic/PDF/ARMB-0022.PDF , https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/_images/esp32-sche-core.png
https://www.instructables.com/Custom-STM32-Boards-From-Scratch-the-Complete-Guid/ , as close as possible to the power pin 
also used a one on the AREF pin cause thats the reference voltage pin , we need to stabilize it as much as possible , also used a one on the AVCC pin to protect the analog supply from digital noise 
used a 10uH inductor through the AVCC to filter out noise , we need the ADC reference to be as stable as it can be , 10uH being the recommended datasheet value and a standard recommendation overall
used an external crystal 16mhz as its the maximum for the ATMEGA8A-PU as the data sheet suggests , caps value is determined by CL = C/2 + Cstray , the crystal itself needs 20pF load capacitance 
i chose the standard for all arduino boards which is 22pF caps , so 22 + about 2-4 stray capacitace = 24-26pF which is fine for a breakout board like this https://www.instructables.com/ATmega-DIP40-Minimal-Board/
used a standard 100nF decoupling cap on the pushbutton RESET to avoid repeated RESETS with one push https://hackaday.com/2015/12/09/embed-with-elliot-debounce-your-noisy-buttons-part-i/

-------------------Copper (Traces and polygons)------------
For all signals , used 0.7mm traces , formula for current I = k × ΔT^0.44 × A^0.725 , makers does not specify copper thickness so we go with the default 35um , area is 0.7x39.37x1.378 (all in mills) = 37.98mil , temp rise is the default 10C
so we get about 1.85A current capacity for each trace , WAY MORE than needed for mcu pins (20mA) but i did not chose it for current , i chose it for toner transfer safety , 0.7mm is the default successful for hand fabrication (worked with it before)
also big traces mean less resistance , which exactly is what we need on signals , we want the full voltage to transfer , no dropout as much as possible
For all power , used 1.4mm and 1.2mm , same calculations just swap the 0.7mm we get about 3A for each , ALSO WAY more than we need , but to differentiate it from signals , better voltage transfer , toner transfer safety
used polygon pours on the VIN and and GND on the terminal block , better voltage transfer and less mechanical stress on a pour instead of just a trace , also its a standard for power inputs 
used polygon pours on GND inside the board as much as i could ( the layout allowed for only one ) as that is the standard ( could have gone with a full ground pour but it destroyed my first design during fabrication )
 
  

