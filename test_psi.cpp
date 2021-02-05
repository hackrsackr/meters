#include "OTA.h"
#include "credentials.h"
#include <Wire.h>
#include <Adafruit_ADS1015.h>

Adafruit_ADS1115 ads(0x48);

const int sensors = 4;
const int max_size = 10;

char keys [sensors] [max_size] = {{ "adc0" }, { "adc1" },{ "adc2" },{ "adc3" },};
int adc [sensors] = {};
float values [sensors] = {};

char sps [sensors] [max_size] = {{ "sp0" }, { "sp1" },{ "sp2" },{ "sp3" },};
float setpoints[sensors] = {};

int rpins [sensors] = {2, 14, 12, 13}; //D4, D5, D6, D7

void setup() {
  for (int i = 0; i < sensors; i++) { 
    pinMode(rpins[i], OUTPUT);
    digitalWrite(rpins[i], HIGH); 
 }
  Serial.begin(115200);
  Serial.println("Booting");
  setupOTA("spunder", mySSID, myPASSWORD);
  ads.begin(); 
}


void get_setpoints() {
  float vols[] = {2.5, 2.5 ,3.0, 1.7}; //desired co2 in vols
  float tempc = 25.0;
  float tempf = (tempc * 1.8) + 32.0;
  
  for (int i = 0; i < sensors; i++) { 
    setpoints[i] = (-16.669 - (.0101059 * tempf)) + (.00116512 * (tempf * tempf)) + (.173354 * tempf * vols[i]) + (4.24267 * vols[i]) - (.0684226 * (vols[i] * vols[i]));
  }
}


void get_adc() { 
  get_setpoints();

  for (int i = 0; i < sensors; i++){
    adc[i] = ads.readADC_SingleEnded(i);
  }
}


void get_psi() {
  get_adc();
   
  for (int i = 0; i < sensors; i++) {  
    if(i == 2) {
      values[i] = (adc[i] - 2750) / (17200.0 + 2750.0) * 27.0;  
    } else {
        values[i] =  (adc[i] - 2750) / (17200.0 + 2750.0) * 60.0;
    }
  }
}    


void test_psi() {
  get_psi();
  Serial.print("{");
  
  for (int i = 0; i < sensors; i++) {
    Serial.print("\"");
    Serial.print(sps[i]);
    Serial.print("\": ");
    Serial.print(setpoints[i]);

    Serial.print(", ");

    Serial.print("\"");
    Serial.print(keys[i]);
    Serial.print("\": ");
    Serial.print(values[i]);

    if(i < (sensors-1)) {
      Serial.print(", ");
    }
      
    if (values[i] > setpoints[i]) {
     digitalWrite(rpins[i], LOW);
     delay(250);
     digitalWrite(rpins[i], HIGH);
    }
  }
  
  Serial.println("}");
}
  
void loop() {
  ArduinoOTA.handle();
  test_psi();
  delay(5000);
}
