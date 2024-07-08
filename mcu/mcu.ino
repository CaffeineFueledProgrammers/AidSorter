#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Wire.h>

#define PROGRAM_NAME "AidSorter"
#define BAUDRATE 115200
// protocol version for the serial communication with the SBC
#define PROTOCOL_VERSION "1.0"
#define PROTOCOL_SEP '\n'

// PIN designations
#define pin_servo_gate1 A0
#define pin_servo_gate2 A1
#define pin_servo_gate3 A2
#define pin_servo_gate4 A3
#define pin_servo_platform A4

#define pin_ir_bucket1 2
#define pin_ir_bucket2 3
#define pin_ir_bucket3 4
#define pin_ir_bucket4 5
#define pin_ir_bucket5 6
#define pin_error_led 7

#define servo_angle_open 0   // Angle to open the servo
#define servo_angle_close 90 // Angle to close the servo

#define debounce 50 // Debounce delay in milliseconds

#define LCD_COLS 20
#define LCD_ROWS 4

// Protocol message definitions
// Format: `{definition}{PROTOCOL_SEP}`

// The commands that can be sent to the MCU.
#define PCMD_GET_PROTOCOL_VERSION "pro" // Get the MCU's protocol version
#define PCMD_STANDBY "stb"              // Put the MCU in standby mode
#define SHOW_STATISTICS = "sts"         // Show the statistics of the system

#define PCMD_GATE1_STATUS "g1s" // Get gate 1 status
#define PCMD_GATE2_STATUS "g2s" // Get gate 2 status
#define PCMD_GATE3_STATUS "g3s" // Get gate 3 status
#define PCMD_GATE4_STATUS "g4s" // Get gate 4 status
#define PCMD_COUNT_GATE5 "ct5"  // Count the object in bucket 5

#define PCMD_PLATFORM_STATUS "ps" // Get the platform status
#define PCMD_PLATFORM_OPEN "pso"  // Open platform
#define PCMD_PLATFORM_CLOSE "psc" // Close platform

#define PCMD_GATE1_OPEN "g1o"  // Open gate 1
#define PCMD_GATE2_OPEN "g2o"  // Open gate 2
#define PCMD_GATE3_OPEN "g3o"  // Open gate 3
#define PCMD_GATE4_OPEN "g4o"  // Open gate 4
#define PCMD_GATE1_CLOSE "g1c" // Close gate 1
#define PCMD_GATE2_CLOSE "g2c" // Close gate 2
#define PCMD_GATE3_CLOSE "g3c" // Close gate 3
#define PCMD_GATE4_CLOSE "g4c" // Close gate 4

#define PCMD_IR_STATUS "irs" // Get IR sensor status
#define PCMD_IR_ACK_1 "ir1"  // Acknowledge IR sensor 1 detection
#define PCMD_IR_ACK_2 "ir2"  // Acknowledge IR sensor 2 detection
#define PCMD_IR_ACK_3 "ir3"  // Acknowledge IR sensor 3 detection
#define PCMD_IR_ACK_4 "ir4"  // Acknowledge IR sensor 4 detection
#define PCMD_IR_ACK_5 "ir5"  // Acknowledge IR sensor 5 detection

#define PCMD_ERR_LED_STATUS "els" // Get error LED status
#define PCMD_ERR_LED_ON "elh"     // Turn on error LED
#define PCMD_ERR_LED_OFF "ell"    // Turn off error LED

// The responses that can be received from the MCU.
#define PRES_READY "RDY"            // The MCU is ready
#define PRES_SUCCESS "OK"           // The command was successful
#define PRES_PLATFORM_SUCCESS "OKP" // The platform command was successful
#define PRES_FAILURE "KO"           // The command failed
#define PRES_PVER_PREFIX "PV:"      // The protocol version prefix
#define PRES_GATE_OPEN "GO"         // The gate is open
#define PRES_GATE_CLOSED "GC"       // The gate is closed
#define PRES_COUNT_GATE5 "CT"       // The count object 5
#define PRES_PLATFORM_OPEN "PO"     // The platform is open
#define PRES_PLATFORM_CLOSED "PC"   // The platform is closed
#define PRES_ERR_LED_ON "ELH"       // The error LED is on
#define PRES_ERR_LED_OFF "ELL"      // The error LED is off

#define PRES_IR_STATUS "IS:" // IR sensor status prefix

// Track the state of servos
bool gate1_open = false;
bool gate2_open = false;
bool gate3_open = false;
bool gate4_open = false;
bool platform_open = false;

bool ir_detected_bucket1 = false;
bool ir_detected_bucket2 = false;
bool ir_detected_bucket3 = false;
bool ir_detected_bucket4 = false;
bool ir_detected_bucket5 = false;

bool is_err_led_on = false;

// Last Debounce Time (LDT) for IR sensors
unsigned long ldt_gate1 = 0;
unsigned long ldt_gate2 = 0;
unsigned long ldt_gate3 = 0;
unsigned long ldt_gate4 = 0;
unsigned long ldt_gate5 = 0;

// Item counts
unsigned int bucket1_count = 0;
unsigned int bucket2_count = 0;
unsigned int bucket3_count = 0;
unsigned int bucket4_count = 0;
unsigned int bucket5_count = 0;

// Initialize objects
Servo gate1;
Servo gate2;
Servo gate3;
Servo gate4;
Servo platform;
LiquidCrystal_I2C lcd(0x27, LCD_COLS, LCD_ROWS);

String encodeMessage(String message) { return message + PROTOCOL_SEP; }
String decodeMessage(String message)
{
  return message.substring(0, message.indexOf(PROTOCOL_SEP));
}

void updateLCDContents(bool clear, String line1, String line2, String line3,
                       String line4)
{
  if (clear)
    lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  for (int i = line1.length(); i < LCD_COLS; i++)
  {
    lcd.print(" ");
  }
  lcd.setCursor(0, 1);
  lcd.print(line2);
  for (int i = line2.length(); i < LCD_COLS; i++)
  {
    lcd.print(" ");
  }
  lcd.setCursor(0, 2);
  lcd.print(line3);
  for (int i = line3.length(); i < LCD_COLS; i++)
  {
    lcd.print(" ");
  }
  lcd.setCursor(0, 3);
  lcd.print(line4);
  for (int i = line4.length(); i < LCD_COLS; i++)
  {
    lcd.print(" ");
  }
}

void showStandbyScreen()
{
  updateLCDContents(true, PROGRAM_NAME, PROTOCOL_VERSION, "Waiting...", "");
}

void showBucketStatistics()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Canned Goods: " + String(bucket1_count));
  lcd.setCursor(0, 1);
  lcd.print("Hygiene:      " + String(bucket2_count));
  lcd.setCursor(0, 2);
  lcd.print("Biscuits:     " + String(bucket3_count));
  lcd.setCursor(0, 3);
  lcd.print("Noodles:      " + String(bucket4_count));
}

void checkProximitySensor(int sensorPin, unsigned long &lastDebounceTime,
                          bool &ir_detected)
{
  int sensorValue = digitalRead(sensorPin);
  if (sensorValue ==
      LOW)
  { // Change HIGH to LOW to check for absence of object
    unsigned long currentTime = millis();
    if ((currentTime - lastDebounceTime) > debounce)
    {
      ir_detected = true;
      lastDebounceTime = currentTime;
    }
  }
}

void setup()
{
  // Initialize the servos
  gate1.attach(pin_servo_gate1);
  gate2.attach(pin_servo_gate2);
  gate3.attach(pin_servo_gate3);
  gate4.attach(pin_servo_gate4);

  // Start with all servos closed
  gate1.write(servo_angle_close);
  gate2.write(servo_angle_close);
  gate3.write(servo_angle_close);
  gate4.write(servo_angle_close);

  // Initialize the IR sensors
  pinMode(pin_ir_bucket1, INPUT);
  pinMode(pin_ir_bucket2, INPUT);
  pinMode(pin_ir_bucket3, INPUT);
  pinMode(pin_ir_bucket4, INPUT);
  pinMode(pin_ir_bucket5, INPUT);

  pinMode(pin_error_led, OUTPUT);

  // Initialize the LCD
  lcd.begin(LCD_COLS, LCD_ROWS);
  lcd.backlight();
  showStandbyScreen();

  Serial.begin(BAUDRATE);
  Serial.print(encodeMessage(PRES_READY)); // signal to SBC that MCU is ready
}

void loop()
{
  if (Serial.available() > 0)
  {
    String command = decodeMessage(Serial.readStringUntil(PROTOCOL_SEP));
    if (command.equalsIgnoreCase(PCMD_GET_PROTOCOL_VERSION))
    {
      Serial.print(
          encodeMessage(String(PRES_PVER_PREFIX) + String(PROTOCOL_VERSION)));
    }
    else if (command.equalsIgnoreCase(PCMD_STANDBY))
    {
      showStandbyScreen();
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_SHOW_STATISTICS))
    {
      showBucketStatistics();
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_ERR_LED_STATUS))
    {
      Serial.print(encodeMessage(is_err_led_on ? PRES_ERR_LED_ON : PRES_ERR_LED_OFF));
    }
    else if (command.equalsIgnoreCase(PCMD_ERR_LED_ON))
    {
      digitalWrite(pin_error_led, HIGH);
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_ERR_LED_OFF))
    {
      digitalWrite(pin_error_led, LOW);
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE1_STATUS))
    {
      Serial.print(encodeMessage(gate1_open ? PRES_GATE_OPEN : PRES_GATE_CLOSED));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE2_STATUS))
    {
      Serial.print(encodeMessage(gate2_open ? PRES_GATE_OPEN : PRES_GATE_CLOSED));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE3_STATUS))
    {
      Serial.print(encodeMessage(gate3_open ? PRES_GATE_OPEN : PRES_GATE_CLOSED));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE4_STATUS))
    {
      Serial.print(encodeMessage(gate4_open ? PRES_GATE_OPEN : PRES_GATE_CLOSED));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE1_OPEN))
    {
      gate1.write(servo_angle_open);
      gate1_open = true;
      bucket1_count++;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE2_OPEN))
    {
      gate2.write(servo_angle_open);
      gate2_open = true;
      bucket2_count++;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE3_OPEN))
    {
      gate3.write(servo_angle_open);
      gate3_open = true;
      bucket3_count++;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE4_OPEN))
    {
      gate4.write(servo_angle_open);
      gate4_open = true;
      bucket4_count++;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE1_CLOSE))
    {
      gate1.write(servo_angle_close);
      gate1_open = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE2_CLOSE))
    {
      gate2.write(servo_angle_close);
      gate2_open = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE3_CLOSE))
    {
      gate3.write(servo_angle_close);
      gate3_open = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_GATE4_CLOSE))
    {
      gate4.write(servo_angle_close);
      gate4_open = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_COUNT_GATE5))
    {
      bucket5_count++;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_PLATFORM_STATUS))
    {
      Serial.print(encodeMessage(platform_open ? PRES_PLATFORM_OPEN : PRES_PLATFORM_CLOSED));
    }
    else if (command.equalsIgnoreCase(PCMD_PLATFORM_OPEN))
    {
      platform.write(servo_angle_open);
      gate4_open = true;
      Serial.print(encodeMessage(PRES_PLATFORM_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_PLATFORM_CLOSE))
    {
      platform.write(servo_angle_close);
      platform_open = false;
      Serial.print(encodeMessage(PRES_PLATFORM_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_STATUS))
    {
      String ir_status = PRES_IR_STATUS;
      ir_status += ir_detected_bucket1 ? "1" : "0";
      ir_status += ir_detected_bucket2 ? "1" : "0";
      ir_status += ir_detected_bucket3 ? "1" : "0";
      ir_status += ir_detected_bucket4 ? "1" : "0";
      ir_status += ir_detected_bucket5 ? "1" : "0";
      Serial.print(encodeMessage(ir_status));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_ACK_1))
    {
      ir_detected_bucket1 = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_ACK_2))
    {
      ir_detected_bucket2 = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_ACK_3))
    {
      ir_detected_bucket3 = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_ACK_4))
    {
      ir_detected_bucket4 = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else if (command.equalsIgnoreCase(PCMD_IR_ACK_5))
    {
      ir_detected_bucket5 = false;
      Serial.print(encodeMessage(PRES_SUCCESS));
    }
    else
    {
      Serial.print(encodeMessage(PRES_FAILURE));
    }

    // Check the proximity sensors
    checkProximitySensor(pin_ir_bucket1, ldt_gate1, ir_detected_bucket1);
    checkProximitySensor(pin_ir_bucket2, ldt_gate2, ir_detected_bucket2);
    checkProximitySensor(pin_ir_bucket3, ldt_gate3, ir_detected_bucket3);
    checkProximitySensor(pin_ir_bucket4, ldt_gate4, ir_detected_bucket4);
    checkProximitySensor(pin_ir_bucket5, ldt_gate5, ir_detected_bucket5);
  }
}