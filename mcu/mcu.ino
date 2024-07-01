#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Wire.h>

Servo servo1;  // Servo for "canned goods"
Servo servo2;  // Servo for "hygiene"
Servo servo3;  // Servo for "dry goods"
Servo servo4;  // Servo for "drinks"

const int servoPin1 = A1;
const int servoPin2 = A2;
const int servoPin3 = A3;
const int servoPin4 = A0;
const int irSensorPin1 = 2;
const int irSensorPin2 = 3;
const int irSensorPin3 = 4;
const int irSensorPin4 = 5;
const int openAngle = 0;    // Angle to open the servo
const int closeAngle = 90;  // Angle to close the servo

const unsigned long debounceDelay = 50;  // Debounce delay in milliseconds

bool servo1Open = false;  // Track the state of servo 1
bool servo2Open = false;  // Track the state of servo 2
bool servo3Open = false;  // Track the state of servo 3
bool servo4Open = false;  // Track the state of servo 4

unsigned long lastDebounceTime1 = 0;  // Last debounce time for IR sensor 1
unsigned long lastDebounceTime2 = 0;  // Last debounce time for IR sensor 2
unsigned long lastDebounceTime3 = 0;  // Last debounce time for IR sensor 3
unsigned long lastDebounceTime4 = 0;  // Last debounce time for IR sensor 4
// Item counts
int countCannedGoods = 0;
int countHygiene = 0;
int countDryGoods = 0;
int countDrinks = 0;

// Initialize the LCD with the I2C address 0x27
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Forward declaration of updateLCD function
void updateLCD();

void setup() {
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);

  servo1.write(closeAngle);  // Start with all servos closed
  servo2.write(closeAngle);
  servo3.write(closeAngle);
  servo4.write(closeAngle);

  pinMode(irSensorPin1, INPUT);
  pinMode(irSensorPin2, INPUT);
  pinMode(irSensorPin3, INPUT);
  pinMode(irSensorPin4, INPUT);

  Serial.begin(9600);
  Serial.print("OK\n");

  // Initialize the LCD
  lcd.begin(20, 4);
  lcd.backlight();
  updateLCD();
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove any leading or trailing whitespace
    if (input.equalsIgnoreCase("1")) {
      servo1.write(openAngle);
      // Serial.println("Servo 1 (canned goods) opened");
      servo1Open = true;
      countCannedGoods++;
      updateLCD();
    } else if (input.equalsIgnoreCase("2")) {
      servo2.write(openAngle);
      // Serial.println("Servo 2 (hygiene) opened");
      servo2Open = true;
      countHygiene++;
      updateLCD();
    } else if (input.equalsIgnoreCase("3")) {
      servo3.write(openAngle);
      // Serial.println("Servo 3 (dry goods) opened");
      servo3Open = true;
      countDryGoods++;
      updateLCD();
    } else if (input.equalsIgnoreCase("4")) {
      servo4.write(openAngle);
      // Serial.println("Servo 4 (drinks) opened");
      servo4Open = true;
      countDrinks++;
      updateLCD();
    }
  }

  // Check the proximity sensors and close the corresponding servos if not
  // detected and open
  checkProximitySensor(irSensorPin1, servo1, servo1Open, lastDebounceTime1,
                       "Servo 1 (canned goods)");
  checkProximitySensor(irSensorPin2, servo2, servo2Open, lastDebounceTime2,
                       "Servo 2 (hygiene)");
  checkProximitySensor(irSensorPin3, servo3, servo3Open, lastDebounceTime3,
                       "Servo 3 (dry goods)");
  checkProximitySensor(irSensorPin4, servo4, servo4Open, lastDebounceTime4,
                       "Servo 4 (drinks)");
}

void checkProximitySensor(int sensorPin, Servo &servo, bool &servoOpen,
                          unsigned long &lastDebounceTime,
                          const char *servoName) {
  int sensorValue = digitalRead(sensorPin);
  if (sensorValue == LOW &&
      servoOpen) {  // Change HIGH to LOW to check for absence of object
    unsigned long currentTime = millis();
    if ((currentTime - lastDebounceTime) > debounceDelay) {
      servo.write(closeAngle);
      servo.write(closeAngle);
      servoOpen = false;
      Serial.print(String(servoName) + " closed by sensor\n");
      lastDebounceTime = currentTime;
    }
  }
}
void updateLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Canned goods: ");
  lcd.print(countCannedGoods);
  lcd.setCursor(0, 1);
  lcd.print("Hygiene: ");
  lcd.print(countHygiene);
  lcd.setCursor(0, 2);
  lcd.print("Dry goods: ");
  lcd.print(countDryGoods);
  lcd.setCursor(0, 3);
  lcd.print("Drinks: ");
  lcd.print(countDrinks);
}
