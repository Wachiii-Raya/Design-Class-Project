#include <Arduino.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define SENSOR_PIN A0
#define PUMP_PIN 9
#define RESISTOR_VALUE 1000000
#define PUMP_TIME 1000
#define PUMP_SPEED 125
#define UPPER_THRESHOLD 200000
#define LOWER_THRESHOLD 100000


void	setup() {
	Serial.begin(9600);
	pinMode(SENSOR_PIN, INPUT);
}


double	convertFsrVoltageToResistance(double fsrVoltage, int resistorValue)
{
	double voltage;
	double resistance;

	voltage = fsrVoltage * (5.0 / 1023.0);
	resistance = (5.0 - voltage) * resistorValue / voltage;
	return (resistance);
	
}


void loop()
{
	unsigned long fsrVoltage;
	unsigned long resistance;
	double resistanceFsr;

	resistance = RESISTOR_VALUE;
	fsrVoltage = analogRead(SENSOR_PIN);
	resistanceFsr = convertFsrVoltageToResistance(fsrVoltage, resistance);

	// If the resistance is reeach to the threshold, 100000 < x < 200000 then turn on the pump
	if (resistanceFsr > LOWER_THRESHOLD && resistanceFsr < UPPER_THRESHOLD)
	{
		analogWrite(PUMP_PIN, PUMP_SPEED);
		delay(PUMP_TIME);
		analogWrite(PUMP_PIN, 0);
	}
	
	Serial.println(resistanceFsr);
	delay(1500);
}
