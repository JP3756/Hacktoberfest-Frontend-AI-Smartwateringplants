enum OperatingMode {
	FAST,
	SLOW,
	DRIP,
	SPRINKLE
};

const int PUMP1_PIN = 3;
const int PUMP2_PIN = 5;
const int PUMP3_PIN = 6;
const byte MOISTURE_PIN = A0;
const byte WATER_LEVEL_PIN = A1;
const int MOISTURE_LOW_VAL = 0;
const int MOISTURE_HIGH_VAL = 700;
const int WATER_LEVEL_LOW_VAL = 0;
const int WATER_LEVEL_HIGH_VAL = 350;
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

	digitalWrite(pumpPin, LOW);
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
}

void loop() {
	int moistureValue = analogRead(MOISTURE_PIN);
	int moisturePercent = map(moistureValue, MOISTURE_LOW_VAL, MOISTURE_HIGH_VAL, 0, 100);
	moisturePercent = constrain(moisturePercent, 0, 100);
	Serial.print("Soil moisture raw: ");
	Serial.print(moistureValue);
	Serial.println();
	Serial.print("Soil moisture percentage: ");
	Serial.print(moisturePercent);
	Serial.println();

	int waterLevelValue = analogRead(WATER_LEVEL_PIN);
	int waterLevelPercent = map(waterLevelValue, WATER_LEVEL_LOW_VAL, WATER_LEVEL_HIGH_VAL, 0, 100);
	waterLevelPercent = constrain(waterLevelPercent, 0, 100);
	Serial.print("Water level raw: ");
	Serial.print(waterLevelValue);
	Serial.println();
	Serial.print("Water level percentage: ");
	Serial.print(waterLevelPercent);
	Serial.println();

	// todo need to know level before watering

	delay(1000);
}
