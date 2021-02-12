#include "Wire.h"
#include "Adafruit_ADS1015.h"

#include "OTA.h"
#include "credentials.h"

//initiate adc driver as ads, 0x48 address to gnd.
Adafruit_ADS1115 ads(0x48);

const int meters = 4;
const int max_size = 6;

//list of data labels
char keys [meters] [max_size] = {{ "pH0" }, { "pH1" }, { "pH2" }, { "pH3" }, };
//list of adc raw data
int adc [meters] = {};
//list of processed data values
float values [meters] = {};

void setup() {
  //set name of board and setup serial, wifi, OTA, ads1115
  Serial.begin(115200);
  Serial.println("Booting");
  setupOTA("pH_meters", mySSID, myPASSWORD);
  ads.begin();  
}


void get_adc() {
  //get raw adc data and read it into adc[]
  for (int i = 0; i < meters; i++){
    adc[i] = ads.readADC_SingleEnded(i);
  }
}


void test_pH() {
  //sfgf
  float divisors [meters] = {1639.0, 1546.0, 1639.0, 1546.0};

  Serial.print("{");
  //convert raw adc data to processed value and assign them to values[]
  for (int i = 0; i < meters; i++){
    values[i] = (adc[i] / divisors[i]);
    //print keys and values
    Serial.print("\"");
    Serial.print(keys[i]);
    Serial.print("\": ");
    Serial.print(values[i]);
      //print comma seperators unless its the last item 
      if (i != (meters-1)) {
        Serial.print(", ");
      } else {
        //closing JSON bracket
        Serial.println("}");
        }
  } 
}


void loop () {
  get_adc();
  test_pH();
  delay(5000);
}
