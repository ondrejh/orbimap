#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
uint32_t tlast = 0;

#define PERIOD_MS 20

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10);

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
  tlast = millis();
}

void loop() {
  uint32_t now = millis();

  if ((now - tlast) >= PERIOD_MS) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    //Serial.print(millis());
    //Serial.print(" ");

    Serial.print(a.acceleration.x);
    Serial.print(" ");
    Serial.print(a.acceleration.y);
    Serial.print(" ");
    Serial.print(a.acceleration.z);
    Serial.print(" ");

    Serial.print(g.gyro.x);
    Serial.print(" ");
    Serial.print(g.gyro.y);
    Serial.print(" ");
    Serial.print(g.gyro.z);
    Serial.println("");

    //Serial.print(temp.temperature);
    //Serial.println("");

    //tlast += PERIOD_MS;
    tlast = now;
  }
}
