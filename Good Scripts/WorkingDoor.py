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

import os
import time as t
import RPi.GPIO as GPIO
import string
def GetCardID(FilePtr):
	for line in FilePtr.readlines():
		if (string.find(line, "UID")) > -1:
			print ("Data to end of line is ", str(len(line[21:])))
			ID = line[21:35]
			print ("The card ID:", ID, "<--")
			return ID

def valid_card_check(file_ptr, test_card_id):
	found_match = False
	for card in file_ptr.readlines():
		#print "The card is " + card
		comma = string.find(card,',')
		#print "This comma is at position" + str(comma)
		if test_card_id == card[:comma]:
			found_match = True
			member_name = card[(comma + 1):-1]
		if found_match:
			print "This card is registered to " + member_name
			return [True, member_name]
		else:
			return [False, "NotAssigned"]

def activate_striker(dur_in_secs):
	GPIO.output(18,GPIO.HIGH)
	t.sleep(dur_in_secs)
	GPIO.output(18,GPIO.LOW)

def log_card(card_ID, comment):
	time_text = t.asctime(t.localtime(t.time()))
	log_file = open("CardRead.txt", 'a')
	log_file.write(time_text + ' ' + comment + ' ' + card_ID + '\n')
	log_file.close()

#Initialize the GPIO and set pin 18 LOW
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18,GPIO.LOW)

# Call the nfc-poll function and log a read card in the file poll.log
while True:
        print "Executing nfc-poll at " + t.asctime(t.localtime(t.time()))
        os.system("nfc-poll > poll.log")
        print "Completed nfc-poll at " + t.asctime(t.localtime(t.time()))
        try:	#See if a card was read, if so, poll.log will be created
                log_file = open("poll.log",'r')
                FileExists = True
        except IOError:
                FileExists = False

        if FileExists:	# Get and check the card information, if one was read
                cardID = GetCardID(log_file)
                if not cardID:
                        print("no Card")
                        continue
                print "Found the card with the ID: " + cardID
                log_file.close()
                file_ptr = open("MemberCards.txt",'r')	# File format: cardID,MemberName
                unlock = valid_card_check(file_ptr, cardID)	# Check to see if this card is a member's card
                file_ptr.close()
                if unlock[0]:
                        log_card(cardID,"open")
                        activate_striker(5)
                else:
                        log_card(cardID,"unregistered card")
                
                #GPIO.output(18,GPIO.HIGH)
                #t.sleep(5)
                #GPIO.output(18,GPIO.LOW)
                os.remove("poll.log")
