# Python program to validate an Ip address
 
# re module provides support
# for regular expressions
import re
 
# Make a regular expression
# for validating an Ip-address
regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
 
 
     
# Define a function for
# validate an Ip address
def checkIP(Ip):
 
    # pass the regular expression
    # and the string in search() method
    if(re.search(regex, Ip)):
        return True
    else:
        return False