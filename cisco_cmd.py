#!/usr/bin/env python3

from Exscript.util.interact import read_login
from Exscript.protocols import SSH2
from Exscript import Account
import sys, getopt, time, datetime, getpass, importlib, os, built_in_commands, argparse

date = datetime.datetime.now()
myFile = open("hosts_file.txt").read().splitlines()            #Print # hosts in file

###Help Menu
#The nargs='?', is used to not have to enter data after or the action='store_false'. Can be used to adjust what appears on screen when not requiring <-l all> <-l> alone will work
#metavar='<custom_cmd>'
#https://docs.python.org/3/howto/argparse.html
single_quotes = " ' ' " 
parser = argparse.ArgumentParser(description='  View README for detailed help/examples \n\n  " " or %s REQUIRED when using spaces \n\n  -o NOT required to run a built-in command' % single_quotes, 
formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-c", "--cmd", help='Run a built-in command from array')
parser.add_argument("-b", "--list-builtin", help='List the available built-in commands from an array')
parser.add_argument("-o", "--option", help='Optional user input filter for the builtin commands')
parser.add_argument("-d", "--custom", help='Custom command generated by user')                    
parser.add_argument("-m", "--module", help='Run selected module from the available modules')
parser.add_argument("-l", "--list-modules", help='List the available modules') 
args = parser.parse_args()
###

#Count hosts in the hosts_file.txt
def count_hosts(hosts):
   counter = 0
   for i in myFile:
      if i:
         counter += 1
   return counter

#Gets creds
def get_creds():
   # username = input("Username [%s]: " % os.getlogin())         #For Linux
   username = input("Username: ")                                #For WSL 2 or without default username:
   if len(username) == 0 :
       username = os.getlogin()
   password = getpass.getpass()
   #Date for logs
   account = Account(username, password)
   return account
# print("\n",date, "\n")

#Used to run the -c commands
def one_command(myFile, command):
    creds = get_creds()
    results = open("/tmp/cisco_cmd_logs/results.txt", "a")
    results.write(str(date) + "\n")
    for host in myFile:
        conn = SSH2()                       
        conn.connect(host)
        conn.login(creds)
        conn.execute('terminal length 0')           
        conn.execute(command)
        # print out connection response
        results.write(host + "\n" + conn.response + "\n")
        print(host)
        print(conn.response + "\n")


#Create list for multi command file [-m]
def get_exscript_hosts(myFile):
   mylst = ''
   print(mylst)
   for host in myFile:
      mylst += "ssh://" + host + " "
   return mylst

###Generates the command to use with the multi command [-m]
def multcmd_cmds(mod_run):
   multi_cmds = open("modules/"+mod_run).read().splitlines()
   final_multcmds = ''
   for i in multi_cmds:
      final_multcmds +=  i + "\n"
   return final_multcmds

###Generates the command to show built-in commands [-b]
def built_in_cmds():
  shorthand = built_in_commands.my_dict.keys()
  for i in shorthand:
     print(i + " = " + built_in_commands.my_dict.get(i))

#command line arguements - gets the -c -o, etc options
def main(argv):
   command = ''
   option = ''
   try:
      opts, args = getopt.getopt(argv,"hi:c:d:o:bi:m:li:",["cmd=","custom=","option=","list-builtin","module=","list-modules"])        #hi, bi, li - the i is required if want print to console maybe? it is required though. : is required at end
   except getopt.GetoptError:
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-c", "--cmd"):
         command = str(built_in_commands.my_dict.get(arg))
      elif opt in ("-d", "--customcmd"):
         command = arg
      elif opt in ("-o", "--option"):
         option = " " + arg
      elif opt in ("-b", "--list-builtin"):
         built_in_cmds()
         sys.exit()
      elif opt in ("-m", "--module"):
         print("\n""COMMANDS:\n%s" % multcmd_cmds(arg))
         print("\nNUMBER OF HOSTS YOU ARE TARGETING: ",count_hosts(myFile))
         print("\nDevice Responses = /tmp/cisco_cmd_logs/")
         final = "exscript -l /tmp/cisco_cmd_logs "+"modules/"+arg+" "+get_exscript_hosts(myFile)
         print("Running Commands From Module : ", arg+"\n")
         os.system(final)
         sys.exit()
      elif opt in ("-l", "--list-modules"):
         i=sorted(os.listdir("modules"))
         for x in i:
            print(x)
         sys.exit()
      else:
         assert False, "unhandled option"
      final_cmd = command + option
   print("YOU ARE ABOUT TO RUN THE COMMAND: ",final_cmd)
   print("\nNUMBER OF HOSTS YOU ARE TARGETING: ",count_hosts(myFile))
   print("\nCANCEL NOW IF THIS IS THE WRONG COMMAND/HOST NUMBER \n")
   print("Responses are appended to /tmp/cisco_cmd_logs/results.txt")
   return one_command(myFile,final_cmd)

#initializes the "main" function so it provides command line variables
if __name__ == "__main__":
   command = main(sys.argv[1:])
