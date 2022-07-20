void setup() {
  // код для настроек
  pinMode(A0, INPUT);
  analogReadResolution(12);
  analogWriteResolution(12);
  pinMode(DAC0, OUTPUT);
  Serial.begin(115200);
  Serial.println("0,0");
}

// пакет:
// key , param ;
//


void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil(';');
    if (input == "0,0") {
      Serial.println("0,0");
    }
    if (input == "1,0") {
      Serial.println("1," + String(analogRead(A0)));
    }
    if (input[0] == '2') {
      int param = 0;
      param = (input[2] - '0')*1000 + (input[3]- '0')*100 + (input[4] - '0')*10 + (input[5] - '0');
      Serial.println("2," + String(param));
      analogWrite(DAC0, param);
    }
  }
}
