#include <Wire.h>
#include <SparkFun_u-blox_GNSS_Arduino_Library.h> // Include SparkFun u-blox GNSS library
SFE_UBLOX_GNSS myGNSS; // Create a GNSS object

// Callback function to process and print GNSS PVT (Position, Velocity, Time) data
void printPVTdata(UBX_NAV_PVT_data_t ubxDataStruct)
{
    Serial.println(); // Print a new line for better readability

    // Print the milliseconds part of the time of week (iTOW)
    unsigned long millisecs = ubxDataStruct.iTOW % 1000;
    if (millisecs < 100) Serial.print(F("0")); // Add leading zeros to maintain format
    if (millisecs < 10) Serial.print(F("0"));
    Serial.print(millisecs);
    Serial.print(F(","));

    // Print latitude
    long latitude = ubxDataStruct.lat;
    Serial.print(latitude);

    // Print longitude
    long longitude = ubxDataStruct.lon;
    Serial.print(F(","));
    Serial.print(longitude);
    
    // Print height above mean sea level (hMSL)
    long hMSL = ubxDataStruct.hMSL;
    Serial.print(F(","));
    Serial.print(hMSL);
    
    // Print velocity in the North direction (velN)
    long velN = ubxDataStruct.velN;
    Serial.print(F(","));
    Serial.print(velN);
    
    // Print velocity in the East direction (velE)
    long velE = ubxDataStruct.velE;
    Serial.print(F(","));
    Serial.print(velE);
    
    // Print velocity in the Down direction (velD)
    long velD = ubxDataStruct.velD;
    Serial.print(F(","));
    Serial.print(velD);

    // Print heading of motion (heading)
    long heading = ubxDataStruct.headMot;
    Serial.print(F(","));
    Serial.print(heading);
    
    // Print the number of satellites used in the navigation solution (SV)
    int SV = ubxDataStruct.numSV;
    Serial.print(F(","));
    Serial.print(SV);
}

void setup()
{
  Serial.begin(115200); // Start serial communication at 115200 baud
  while (!Serial); // Wait for the user to open the terminal

  Wire.begin(); // Start I2C communication

  // Connect to the u-blox GNSS module using I2C
  if (myGNSS.begin() == false)
  {
    // If the connection fails, enter an infinite loop
    while (1);
  }

  // Set GNSS communication to output only UBX protocol (disable NMEA)
  myGNSS.setI2COutput(COM_TYPE_UBX); 

  // Save communication port settings to flash and battery-backed RAM (BBR)
  myGNSS.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT);

  // Set the GNSS navigation frequency to 20 Hz (20 position updates per second)
  myGNSS.setNavigationFrequency(20);

  // Enable automatic NAV PVT messages and set the callback function to printPVTdata
  myGNSS.setAutoPVTcallback(&printPVTdata);
}

void loop()
{
  // Check for the arrival of new GNSS data and process it
  myGNSS.checkUblox();

  // Check if any callbacks are waiting to be processed
  myGNSS.checkCallbacks();
}
