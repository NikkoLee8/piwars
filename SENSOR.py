#!/usr/bin/env python
#Setup ADC0832 and LED and BUZZER
import RPi.GPIO as GPIO
import time

ADC_CS  = 11
ADC_CLK = 13
ADC_DIO = 12
RedPin = 15
BZRPin = 29
GPIO.setmode(GPIO.BOARD)     # Number GPIOs by its physical location
GPIO.setup(BZRPin, GPIO.OUT) # Set BZRPin mode as output
p = GPIO.PWM(BZRPin, 50) # init frequency : 50 HZ

def setup():
	global p
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)     # Number GPIOs by its physical location
	GPIO.setup(ADC_CS, GPIO.OUT) # Setup ADC0832
	GPIO.setup(ADC_CLK, GPIO.OUT)# Setup ADC0832
	GPIO.setup(RedPin, GPIO.OUT) # Set REDpin mode as output
	GPIO.output(RedPin, GPIO.HIGH) # Set REDpin to high (+3.3V) to off the led
	GPIO.setup(BZRPin, GPIO.OUT) # Set BZRPin mode as output
	GPIO.output(BZRPin, GPIO.LOW)
	p = GPIO.PWM(BZRPin, 50) # init frequency : 50 HZ

def destroy():
	GPIO.output(RedPin, GPIO.HIGH) # Led off
	p.stop()
	GPIO.cleanup()			# Release resources

def LedRedOn():
	GPIO.output(RedPin, GPIO.LOW) # led on

def LedRedOff():
	GPIO.output(RedPin, GPIO.HIGH) # led off

def SoundBuzzer():
	print "Sound Buzzer"
	p.start(50) # Duty cycle : 50%
	for f in range(4):
		p.ChangeFrequency(923.32)
		time.sleep(0.1)
		p.ChangeFrequency(880)
		time.sleep(0.1)
	p.stop()

def getResult():     # get ADC result
	GPIO.setup(ADC_DIO, GPIO.OUT)
	GPIO.output(ADC_CS, 0)
	
	GPIO.output(ADC_CLK, 0)
	GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
	GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
	GPIO.output(ADC_CLK, 0)

	GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
	GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
	GPIO.output(ADC_CLK, 0)

	GPIO.output(ADC_DIO, 0);  time.sleep(0.000002)

	GPIO.output(ADC_CLK, 1)
	GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
	GPIO.output(ADC_CLK, 0)
	GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
	
	dat1 = 0
	for i in range(0, 8):
		GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
		GPIO.setup(ADC_DIO, GPIO.IN)
		dat1 = dat1 << 1 | GPIO.input(ADC_DIO)  # or ?
	
	dat2 = 0
	for i in range(0, 8):
		dat2 = dat2 | GPIO.input(ADC_DIO) << i
		GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
	
	GPIO.output(ADC_CS, 1)
	GPIO.setup(ADC_DIO, GPIO.OUT)

	if dat1 == dat2:
		return dat1
	else:
		return 0

def loop():
	setup()
	while True:
		res = getResult()
		print 'res = %d' % res
		SoundBuzzer()
		time.sleep(0.4)

if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()

