# PCMDoor_v2.py 
# This file is the basis for the Raspberry Pi - based door entry system at the 
# Port City Makerspace. It is to be used in conjunction with the NFC-RFID card reader 
# and the MiFare Classic card. 
# 
# Three files: poll.log, MemberCards.txt, and CardRead.txt are used in this program. The file 
# poll.log is used to capture the card information that is read from the 'nfc-poll' call.
# The file MemberCards.txt needs to exist and be populated with the format
# CardID,Membername\n before the program is executed
# The CardRead.txt file is used to log those cards that were detected by the reader
# and to indicate weather or not this was a member's card which would cause the
# door to unlock.
# 
# Author: Dave Strohschein 
# Revision Date: April 13, 2014 
# Revision Date: October 30, 2016: Paul StPierre > Streamlined code, added more data in log_card

import os
import time as t
import RPi.GPIO as GPIO
import csv

def GetCardID(FilePtr):
	for line in FilePtr.readlines():
		if (string.find(line, "UID")) > -1:
			print ("Data to end of line is ", str(len(line[21:])))
			ID = line[21:35]
			print ("The card ID:", ID, "<--")
			return ID

def valid_card_check(file_ptr, test_card_id):				# Member card validation
	with open(file_ptr,"r") as member_cards :				# Better method for opening files
		cardfile = csv.reader(member_cards)				# Using csv function to streamline search and access more data
		for card in cardfile :							# Makes a list from the current line of the opened file
			if test_card_id == card[0] :					# Card id in the format    XX  XX  XX  XX  -8 alphanumeric characters total with 6 spaces -14 total
				return card							# Return entire card for further processing
		
		return 'Not assigned'							# Otherwise return without data

def activate_striker(dur_in_secs):
	GPIO.output(18,GPIO.HIGH)
	GPIO.output(24,GPIO.HIGH)
	t.sleep(dur_in_secs)
	GPIO.output(24,GPIO.LOW)
	GPIO.output(18,GPIO.LOW)
	return

def deny_Access(dur_in_secs):
	GPIO.output(23,GPIO.HIGH)
	t.sleep(dur_in_secs)
	GPIO.output(23,GPIO.LOW)

def log_card(member_name, card_ID, comment):
	time_text = t.asctime(t.localtime(t.time()))
	log_file = open("CardRead.txt", 'a')
	log_file.write(time_text + ' | ' + member_name + ' | ' + comment + ' | ' + card_ID + '\n')
	log_file.close()
	return

													#Initialize the GPIO and set pin 18 LOW
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18,GPIO.LOW)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23,GPIO.LOW)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24,GPIO.LOW)

													# Call the nfc-poll function and log a read card in the file poll.log
while True:											# Infinite loop
        print ("Executing nfc-poll at " + t.asctime(t.localtime(t.time())))
        os.system("nfc-poll > poll.log")						# Calling nfc-poll
        print( "Completed nfc-poll at " + t.asctime(t.localtime(t.time())))
        try:												#See if a card was read, if so, poll.log will be created
                log_file = open("poll.log",'r')
                FileExists = True
        except IOError:
                FileExists = False

if FileExists:											# Get and check the card information, if one was read
        cardID = GetCardID(log_file)
        if not cardID:
                print("no Card")
		continue
        print ("Found the card with the ID: " + cardID)
        log_file.close()
	os.remove("poll.log")

        file_ptr = "MemberCards.txt" 						# File format: cardID,MemberName
        validCard = valid_card_check(file_ptr, cardID)			# Check to see if this card is a member's card

        if validCard[2] == "G" :
                log_card(card[1], card[0], card[2], "Access Allowed")
                activate_striker(5)

        elif validCard[2] == "E" :
                log_card(card[1], card[0], "Membership Expired", "Access Denied")

	else :
		log_card(cardID, "Not assigned", "Unregistered Card", "Access Denied")

