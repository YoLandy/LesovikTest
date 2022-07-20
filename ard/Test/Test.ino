void setup() {
  pinMode(DAC0, OUTPUT);
  pinMode(A0, INPUT);
  Serial.begin(115200);
  analogReadResolution(12);
  analogWriteResolution(12);
}

void loop() {
  if (Serial.available()) {
    Serial.readStringUntil('\n');
    for (int i = 0; i < 4096; i++) {
    analogWrite(DAC0, i);
    Serial.println(i);
    Serial.println(analogRead(A0));
    Serial.println();
  }
  }
}
