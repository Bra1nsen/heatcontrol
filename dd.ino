#include <cactus_io_BME280_SPI.h>
#include <SPI.h>


#define BME_SCK 13     // Serial Clock
#define BME_MISO 11    // Serial Data In
#define BME_MOSI 12    // Serial Data Out
#define BME_CS 10      // Chip Select

BME280_SPI bme(BME_CS,BME_MOSI,BME_MISO,BME_SCK); // BME280_SPI bme(BME_CS); (SPI)

#include "TimerOne.h"
#include <math.h>

#define WindSensorPin (2) // The pin location of the anemometer sensor
#define WindVanePin (A4) // The pin the wind vane sensor is connected to
#define VaneOffset 0; // define the anemometer offset from magnetic north

int VaneValue; // raw analog value from wind vane
int Direction; // translated 0 - 360 direction
int CalDirection; // converted value with offset applied
int LastValue; // last direction value

volatile bool IsSampleRequired; // this is set true every 2.5s. Get wind speed
volatile unsigned int TimerCount; // used to determine 2.5sec timer count
volatile unsigned long Rot; // cup rotation counter used in interrupt routine
volatile unsigned long Rotations; 
volatile unsigned long ContactBounceTime; // Timer to avoid contact bounce in isr

float WindSpeed; // speed miles per hour




void setup() {

  Serial.begin(9600);
  pinMode(WindSensorPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(WindSensorPin), isr_rotation, FALLING);

  LastValue = 0;

  IsSampleRequired = false;

  TimerCount = 0;
  


  
  //Serial.println("Bosch BME280 Pressure - Humidity - Temp Sensor | cactus.io");
  //Serial.println("Speed (MPH)\tKnots\tDirection\tStrength");


  if (!bme.begin()) {
  Serial.println("Could not find a valid BME280 sensor, check wiring!");
  while (1);
  }

  bme.setTempCal(-1);// Sensor was reading high so offset by 1 degree C

  Serial.println("Rotations\tVaneValue\tDirection\tPressure\tHumdity\t\tTemp\t\tTemp");
}

void loop() {
 
  
  Rotations = 0; 
  sei(); // Enables interrupts
  delay (3000); // Wait 3 seconds to average
  cli(); // Disable interrupts

// convert to mp/h using the formula V=P(2.25/T)
// V = P(2.25/3) = P * 0.75

  WindSpeed = Rotations * 0.75;

  bme.readSensor();

  float temp_c = bme.getTemperature_C();
  float hum = bme.getHumidity();
  float pres = bme.getPressure_MB();
  float temp_f = bme.getTemperature_F();

  VaneValue = analogRead(A4);
  Direction = map(VaneValue, 0, 1023, 0, 359);
  CalDirection = Direction + VaneOffset;


  if(CalDirection > 360)
  CalDirection = CalDirection - 360;

  if(CalDirection < 0)
  CalDirection = CalDirection + 360;

  if (Direction == 360) Direction = 0;

  //char buffer[70];
  //sprintf{buffer, "Pressure %d mb
  Serial.print(Rotations); Serial.print("\t\t");
  Serial.print(VaneValue); Serial.print("\t\t");
  Serial.print(CalDirection); Serial.print(" °\t\t");
  Serial.print(pres); Serial.print(" mb\t"); // Pressure in millibars
  Serial.print(hum); Serial.print(" %\t\t");
  Serial.print(temp_c); Serial.print(" *C\t");
  Serial.print(temp_f); Serial.println(" *F\t");






  // Add a 2 second delay.
  delay(3000); //just here to slow down the output.
}


// This is the function that the interrupt calls to increment the rotation count
void isr_rotation () {

  if ((millis() - ContactBounceTime) > 15 ) { // debounce the switch contact.
    Rotations++;
    ContactBounceTime = millis();
}
}
