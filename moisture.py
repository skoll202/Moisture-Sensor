#!/usr/bin/python

# Start by importing the libraries we want to use

import RPi.GPIO as GPIO # This is the GPIO library we need to use the GPIO pins on the Raspberry Pi
import smtplib # This is the SMTP library we need to send the email notification
import time # This is the time library, we need this so we can use the sleep function

# Define some variables to be used later on in our script
CHANNEL = {17:"Pot 1",29:"Pot 2"} # pins connected to the digital output of the sensors, with the name of the plant as the value
TTL = 5 # time in minutes to wait before sending another message
CHANNELTIMER = {}
for c in CHANNEL.keys():
	CHANNELTIMER[c] = time.time()
# You might not need the username and password variable, depends if you are using a provider or if you have your raspberry pi setup to send emails
# If you have setup your raspberry pi to send emails, then you will probably want to use 'localhost' for your smtp_host

smtp_username = "enter_email_address_here" # This is the username used to login to your SMTP provider
smtp_password = "enter_password_here" # This is the password used to login to your SMTP provider
smtp_host = "smtp.gmail.com" # This is the host of the SMTP provider
smtp_port = 465 # This is the port that your SMTP provider uses

smtp_sender = smtp_username # This is the FROM email address
smtp_receivers = [smtp_username] # This is the TO email address

# The next two variables use triple quotes, these allow us to preserve the line breaks in the string. 

# This is the message that will be sent when NO moisture is detected

def generateMessage(isMoisture,channel):
	message = "From: %s <%s>\n" % (CHANNEL[channel],smtp_username)
	message += "To: Gardener <%s>\n" % smtp_username
	message += "Subject: Moisture Sensor Notification\n\n" 
	if isMoisture:
		message += "Moisture detected.  Everything seems fine."
	else:
		message += "Moisture no linger detected.  Assistance needed."
	return message

# This is our sendEmail function

def sendEmail(smtp_message):
	try:
		smtpObj = smtplib.SMTP_SSL(smtp_host, smtp_port)
		smtpObj.login(smtp_username, smtp_password) # If you don't need to login to your smtp provider, simply remove this line
		smtpObj.sendmail(smtp_sender, smtp_receivers, smtp_message)         
		print("Successfully sent email")
	except smtplib.SMTPException:
		print("Error: unable to send email")

# This is our callback function, this function will be called every time there is a change on the specified GPIO channel, in this example we are using 17

def callback(channel):  
	if time.time() - CHANNELTIMER[channel] > TTL*60:
		CHANNELTIMER[channel] = time.time()
		if GPIO.input(channel):
			print("LED off")
			sendEmail(generateMessage(False,channel))
		else:
			print("LED on")
			sendEmail(generateMessage(True,channel))

# Set our GPIO numbering to BCM
GPIO.setmode(GPIO.BCM)

for c in CHANNEL.keys():
	GPIO.setup(c, GPIO.IN)

# This line tells our script to keep an eye on our gpio pin and let us know when the pin goes HIGH or LOW
	GPIO.add_event_detect(c, GPIO.BOTH, bouncetime=300)
# This line asigns a function to the GPIO pin so that when the above line tells us there is a change on the pin, run this function
	GPIO.add_event_callback(c, callback)

# This is an infinte loop to keep our script running
while True:
	# This line simply tells our script to wait 0.1 of a second, this is so the script doesnt hog all of the CPU
	time.sleep(0.1)
