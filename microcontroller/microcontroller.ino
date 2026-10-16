enum OperatingMode {
  FAST,
  SLOW,
  DRIP,
  SPRINKLE
};

const int PUMP1_PIN = 25;
const int PUMP2_PIN = 26;
const int PUMP3_PIN = 27;

const int MOISTURE_PIN = 34;
const int WATER_LEVEL_PIN = 35;

const int MOISTURE_LOW_VAL = 0;
const int MOISTURE_HIGH_VAL = 2800;
const int WATER_LEVEL_LOW_VAL = 0;
const int WATER_LEVEL_HIGH_VAL = 1400;

int curMode = FAST;

void fast() {
  Serial.println("-- Fast Flow Mode --");
  digitalWrite(PUMP1_PIN, HIGH);
  digitalWrite(PUMP2_PIN, HIGH);
  digitalWrite(PUMP3_PIN, HIGH);
}

void slow() {
  Serial.println("-- Slow Flow Mode --");
  analogWrite(PUMP1_PIN, 120);
  analogWrite(PUMP2_PIN, 120);
  analogWrite(PUMP3_PIN, 120);
}

void drip() {
  Serial.println("-- Drip Flow Mode --");
  digitalWrite(PUMP1_PIN, HIGH);
  digitalWrite(PUMP2_PIN, HIGH);
  digitalWrite(PUMP3_PIN, HIGH);
  delay(150);

  digitalWrite(PUMP1_PIN, LOW);
  digitalWrite(PUMP2_PIN, LOW);
  digitalWrite(PUMP3_PIN, LOW);
  delay(2500);
}

void sprinkle() {
  Serial.println("-- Sprinkle Flow Mode --");
}

void setup() {
  Serial.begin(115200);

  pinMode(PUMP1_PIN, OUTPUT);
  pinMode(PUMP2_PIN, OUTPUT);
  pinMode(PUMP3_PIN, OUTPUT);
  
  pinMode(MOISTURE_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  
  Serial.println("ESP32 Watering System Initialized");
}

void loop() {
  int moistureValue = analogRead(MOISTURE_PIN);
  int moisturePercent = map(moistureValue, MOISTURE_LOW_VAL, MOISTURE_HIGH_VAL, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  Serial.print("Soil moisture raw: ");
  Serial.println(moistureValue);
  Serial.print("Soil moisture percentage: ");
  Serial.println(moisturePercent);

  int waterLevelValue = analogRead(WATER_LEVEL_PIN);
  int waterLevelPercent = map(waterLevelValue, WATER_LEVEL_LOW_VAL, WATER_LEVEL_HIGH_VAL, 0, 100);
  waterLevelPercent = constrain(waterLevelPercent, 0, 100);
  
  Serial.print("Water level raw: ");
  Serial.println(waterLevelValue);
  Serial.print("Water level percentage: ");
  Serial.println(waterLevelPercent);

  // TODO: need to know level before watering

  delay(1000);
}