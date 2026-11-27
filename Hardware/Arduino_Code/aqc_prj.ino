#include <WiFi.h>
#include <HTTPClient.h>
#include "secrets.h"
//#include <LiquidCrystal.h>
#include <OneWire.h>
#include <DallasTemperature.h>


#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);




// Sensor Pins
#define TURBIDITY_PIN 36
#define PH_PIN        34
#define TDS_PIN       39
#define ONE_WIRE_BUS  15

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Calibration

const float PH7_VOLTAGE = 1.960;
const float PH4_VOLTAGE = 1.780;         //1.580;

const float PH7 = 7.00;
const float PH4 = 4.00;

float slope;


float tdsFactor = 0.5;

void setup()
{
  Serial.begin(9600);

  lcd.init();
 lcd.backlight();

  sensors.begin();

   analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  // Voltage-to-pH slope
  slope = (PH7 - PH4) /
          (PH7_VOLTAGE - PH4_VOLTAGE);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Water Quality");
  lcd.setCursor(0,1);
  lcd.print("Monitoring..");
  delay(1500);

  WiFi.begin(ssid,password);

  lcd.setCursor(0,1);
  lcd.print("Connecting WiFi");

  while(WiFi.status()!=WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("WiFi Connected");

  delay(2000);
}

void loop()
{
  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);

  // Turbidity

    int turbADC = analogRead(TURBIDITY_PIN);
    float turbVoltage = turbADC * 3.3 / 4095.0;
    
    Serial.print("Turbidity ADC = ");
    Serial.println(turbADC);
    
    Serial.print("Turbidity Voltage = ");
    Serial.println(turbVoltage, 3);
    float ntu;
    
    if(turbVoltage >= 2.8)
        ntu = 5;        // Pure Water
    else if(turbVoltage >= 2.5)
        ntu = 50;       // Slightly Cloudy
    else if(turbVoltage >= 2.2)
        ntu = 200;      // Moderate
    else if(turbVoltage >= 1.8)
        ntu = 1000;     // Dirty
    else
        ntu = 3000;     // Very Muddy


  // pH

  Serial.print("pH 7 Voltage = ");
  Serial.println(PH7_VOLTAGE, 3);

  Serial.print("pH 4 Voltage = ");
  Serial.println(PH4_VOLTAGE, 3);

  Serial.print("Slope = ");
  Serial.println(slope, 3);

  Serial.println("================================");

  long totalADC = 0;

  // Average 100 readings
  for (int i = 0; i < 100; i++) {

    totalADC += analogRead(PH_PIN);

    delay(10);
  }

  float adcValue = totalADC / 100.0;

  // Convert ADC to voltage
  float voltage = (adcValue / 4095.0) * 3.3;

  // ================================
  // CORRECT pH CALCULATION
  // ================================

//  float pHValue =
//      PH7 - ((PH7_VOLTAGE - voltage) * slope);
//
float pHValue =
    PH7 + ((voltage - PH7_VOLTAGE) * slope);


  // Limit pH
  if (pHValue < 0)
    pHValue = 0;

  if (pHValue > 14)
    pHValue = 14;

  // Display
  Serial.print("ADC = ");
  Serial.print(adcValue, 0);

  Serial.print(" | Voltage = ");
  Serial.print(voltage, 3);

  Serial.print(" V | pH = ");
  Serial.println(pHValue, 2);

  delay(1000);




  // TDS
  float tdsVoltage = readVoltage(TDS_PIN);

  float compensationCoefficient =
  1.0 + 0.02*(temperature - 25.0);

  float compensationVoltage =
  tdsVoltage / compensationCoefficient;

  float tdsValue =
  (133.42 * compensationVoltage *
   compensationVoltage *
   compensationVoltage
   -255.86 * compensationVoltage *
   compensationVoltage
   +857.39 * compensationVoltage)
   * tdsFactor;

  // WQI


float qPH  = max(0.0, 100.0 - abs(7.0 - pHValue) * 15.0);
float qTDS = max(0.0, 100.0 - (tdsValue / 10.0));
float qNTU = max(0.0, 100.0 - (ntu / 5.0));

float WQI = (0.4 * qPH) + (0.3 * qTDS) + (0.3 * qNTU);

  String waterCondition;

  if(WQI >= 95)
  {
      waterCondition = "PURE";
  }
  else if(WQI >= 85)
  {
      waterCondition = "EXCELLENT";
  }
  else if(WQI >= 70)
  {
      waterCondition = "GOOD";
  }
  else if(WQI >= 50)
  {
      waterCondition = "POOR";
  }
 
  else
  {
      waterCondition = "UNSAFE";
  }

  // LCD Display
  lcd.clear();

  lcd.setCursor(0,0);
  lcd.print("T:");
  lcd.print(temperature,1);
  lcd.print("C");

  lcd.setCursor(8,0);
  lcd.print("pH:");
  lcd.print(pHValue,1);

  lcd.setCursor(0,1);
  lcd.print("TDS:");
  lcd.print(tdsValue,0);
  lcd.print("ppm");

  lcd.setCursor(10,1);
  lcd.print("NTU:");
  lcd.print(ntu,0);
  delay(1000);
//  lcd.clear();
//  lcd.print("WQI:");
//  lcd.print(WQI,1);
//   lcd.setCursor(0,1);
//  lcd.print(waterCondition);
//  delay(3000);
  // Serial
  Serial.println("----------------------");
  Serial.print("Temp = ");
  Serial.println(temperature);

  Serial.print("pH = ");
  Serial.println(pHValue);

  Serial.print("TDS = ");
  Serial.println(tdsValue);

  Serial.print("NTU = ");
  Serial.println(ntu);

  Serial.print("WQI = ");
  Serial.println(WQI);
  Serial.print("Condition = ");
Serial.println(waterCondition);

  // ThingSpeak Upload
  if(WiFi.status()==WL_CONNECTED)
  {
    HTTPClient http;

    String url =
    "http://api.thingspeak.com/update?api_key=" +
    apiKey + 
    "&field1=" + String(pHValue) +
    "&field2=" + String(temperature) +
    "&field3=" + String(ntu) +
    "&field4=" + String(tdsValue) +
    "&field5=" + String(WQI);

    http.begin(url);

    int httpCode = http.GET();

    Serial.print("ThingSpeak Response: ");
    Serial.println(httpCode);

    http.end();
  }

  delay(15000); // ThingSpeak minimum 15 sec
}

float readVoltage(int pin)
{
  long sum = 0;

  for(int i=0;i<30;i++)
  {
    sum += analogRead(pin);
    delay(5);
  }

  float adc = sum/30.0;

  return adc*(3.3/4095.0);
}
