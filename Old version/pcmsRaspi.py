#python command line interpreter for talking to the system while live
#Can be used to update info, lock/unlock door, reboot, etc

import cmd
import os
import time as t
import RPi.GPIO as GPIO
import string

class pcmsRaspi(cmd.Cmd):        

    def do_getCardID(FilePtr):  # FilePtr should be the file: 'poll.log' for now
        for line in FilePtr.readlines():
            #print line
            #print (str(string.find(line, "UID")))
            if (string.find(line, "UID")) > -1:
                print "Data to end of line is " + str(len(line[21:]))
                ID = line[21:35]
                print "The card ID:" + ID +"<--"
                return ID

    def do_check(file_ptr, test_card_id):
        found_match = False
        for card in file_ptr.readlines():
            print "The card is " + card
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

    def do_activate_striker(dur_in_secs):
        GPIO.output(18,GPIO.HIGH)
        t.sleep(dur_in_secs)
        GPIO.output(18,GPIO.LOW)
	
    def do_log_card(card_ID, comment):
        time_text = t.asctime(t.localtime(t.time()))
        #log_file = open("CardRead.txt", 'w')
        log_file = open("CardRead.txt",'a')
        log_file.write(time_text + ' ' + comment + ' ' + card_ID + '\n')
        log_file.close()
    

if __name__ == "__main__":
    # Call the nfc-poll function and log a read card in the file poll.log
    print "Executing nfc-poll at " + t.asctime(t.localtime(t.time()))
    os.system("nfc-poll > poll.log")
    print "Completed nfc-poll at " + t.asctime(t.localtime(t.time()))

    try:					#See if a card was read, if so, poll.log will be created						
        log_file = open("poll.log",'r')
        FileExists = True
    except IOError:
        FileExists = False

    if FileExists:		# Get and check the card information, if one was read
        cardID = getCardID(log_file)
        print("Found the card with the ID: ",  cardID)
        log_file.close()
        file_ptr = open("MemberCards.txt",'r') 	# File format: cardID,MemberName
        unlock = check(file_ptr, cardID)  	# Check to see if this card is a member's card
        file_ptr.close()
        if unlock[0]:
            log_card(cardID,"open")
            activate_striker(5)
        else:
            log_card(cardID,"unregistered card")
    
