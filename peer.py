from socket import *
import threading
import os
import platform
import commands
import datetime
import sys
import time

status_codes = {}
status_codes[200] = 'OK'
status_codes[400] = 'Bad Request'
status_codes[404] = 'Not Found'
status_codes[505] = 'P2P-CI Version Not Supported'

version = "P2P-CI/1.0"
path = ""
hostname = gethostbyname(gethostname()) #platform.uname()[1]
osDetails = platform.system() + " " + platform.release()

servingSocket = socket(AF_INET, SOCK_STREAM) # to serve other peers
servingPort = 0
args = sys.argv
if len(args) != 2:
    print "Please input 1 argument <server ip address>"
    sys.exit()
serverName = args[1]    
serverPort = 7734
clientSocket = socket(AF_INET, SOCK_STREAM) # to connect to the server

def send(sock, content):
	sock.sendall(content)
	response = sock.recv(4096)
	return response

def startService(servingSocket): # Keeps listening in a separate thread to new incoming connections from other peers.
	servingSocket.listen(1)
	#print "Peer ready to serve other peers."
	while 1:
		connSocket, addr = servingSocket.accept() # accept connection from a new peer and process its request in a different thread
		t = threading.Thread(target = processRequest, args = (connSocket, addr,))
		t.start()

def processRequest(connSocket, addr):
	message = connSocket.recv(4096)
	# parse this message and give content to that connSocket as a reply to the requesting peer
	message_split = message.split('\r\n')[0].split()
	status_code = 200
	file_content = "\r\n"
	if message_split[0] != "GET":
		status_code = 400
	else:
		filename_part = "RFC " + message_split[2]
		filename = [s for s in os.listdir(path) if filename_part in s]
		if len(filename) == 0:
			status_code = 404
		else:
			filename = filename[0]
			filepath = os.path.join(path, filename)
			#file_details = commands.getstatus(filepath)
			txt = open(filepath)
			filedata = txt.read()
			file_details = commands.getoutput('stat "' + filepath + '"')
			size = str(len(filedata)) #file_details.split('\n')[1].split('\t')[0].split()[1]
			#last_mod = file_details.split('\n')[5].split(': ')[1]
			mtime = time.ctime(os.path.getmtime(filepath))
			ltm = "last modified time"
			if mtime:
				q = mtime.split()
				if len(q) == 5:
					ltm = q[0] + ", " + q[2] + " " + q[1] + " " + q[4] + " " + q[3]

			last_mod = ltm

			file_content = "Last-Modified: " + last_mod + "\r\n"
			file_content = file_content + "Content-Length:" + size + "\r\n"
			file_content = file_content + "Content-Type: text/plain\r\n\r\n"
			file_content = file_content + filedata
			
		'''
		try this....
		size = file_details.split('\n')[0].split()[7]
		still not quite right though....
		last_mod = file_details.split('\n')[0].split()[9] + file_details.split('\n')[0].split()[8] + file_details.split('\n')[0].split()[11].strip() + file_details.split('\n')[0].split()[10]
		'''
		#find file
		#if not present - 404
		#else get content into file_content
		#append last-modified, etc. before file_content
	
	return_string = version + " " + str(status_code) + " " + status_codes[status_code] + "\r\n"
	return_string = return_string + "Date: " + datetime.datetime.strftime(datetime.datetime.now(), '%a, %d %b %Y %H:%M:%S %Z') + "\r\n"
	return_string = return_string + "OS: " + osDetails + "\r\n"
	return_string = return_string + file_content
	connSocket.sendall(return_string)
	connSocket.close()
	
	
def initial_adds():
	global path
	path = raw_input("Enter the folder that contains the RFCs: ")
	rfclist = os.listdir(path)
	#add_string = ""
	for eachrfc in rfclist:
		if eachrfc.startswith("RFC"):
			rfcsplit = eachrfc.split(' - ')
			rfcnum = rfcsplit[0].split()[1]
			rfcname = rfcsplit[1]
			addMessage = create_add_lookup_string("ADD", rfcnum, rfcname)
			response = send(clientSocket, addMessage)
			print "Response from the server: " + response + "\r\n"
			if response.split()[1] == '200':
				print "RFC " + rfcnum + " added successfully!"
			

def create_add_lookup_string(func, rfcnum, rfcname):
	al_string = func + " RFC " + rfcnum + " " + version + "\r\n"
	al_string = al_string + "Host: " + hostname + "\r\n"
	al_string = al_string + "Port: " + str(servingPort) + "\r\n"
	al_string = al_string + "Title: " + rfcname + "\r\n" + "\r\n"
	return al_string


def requestDownload(response):
	lines = response.split("\r\n")
	if status_codes[200] not in lines[0]:
		print lines[0]
		return
	# give options to the user to download from. Options are from lines 2 to second last line
	print "RFC Number ~ RFC Title ~ Hostname ~ Port"
	i = 1
	for item_temp in lines[2:-2]:
		item = item_temp.split()
		print str(i),".", " ".join(item[0:2]), "~", " ".join(item[2:-2]), '~', item[-2], '~', item[-1]
		i = i+1
	print str(i),". Go back to the main menu"
	while 1:
		opt = int(raw_input("Choose an option from above to download from: "))
		if opt == i:
			break
		elif opt < i:
			s = lines[opt+1].split()
			port = s[-1]
			host = s[-2]
			rfcNo = s[0] + " " + s[1]
			rfcName = " ".join(s[2:-2])
			downloadRFC(rfcNo, host, port, rfcName)
			break
		else:
			print "Not an option"


def lookup(rfcNo, rfcName):
	lookupString = create_add_lookup_string("LOOKUP", rfcNo, rfcName)
	response = send(clientSocket, lookupString)
	requestDownload(response)
	
	
def listAll():
	l_string = "LIST ALL " + version + "\r\n"
	l_string = l_string + "Host: " + hostname + "\r\n"
	l_string = l_string + "Port: " + str(servingPort) + "\r\n" + "\r\n"
	response = send(clientSocket, l_string)
	requestDownload(response)
	

def downloadRFC(rfcNo, host, port, rfcName):
	downloadSocket = socket(AF_INET, SOCK_STREAM)
	print "Downloading from..." + host + ":" + port
	downloadSocket.connect((host, int(port)))
	getMessage = "GET " + rfcNo + " " + version + "\r\n" + "Host: " + hostname + "\r\n" + "OS: " + osDetails + "\r\n\r\n"
	#print getMessage
	downloadSocket.send(getMessage)
	content = downloadSocket.recv(16384)
	#print "Content - ", content[:300]
	downloadSocket.close()
	splitLines = content.split("\r\n")
	if status_codes[200] not in splitLines[0]:
		print "Something went wrong while downloading. " + splitLines[0]
		return
	
	# write data to a file
	write(splitLines[-1], rfcNo, rfcName) # data is the last portion
	print "\r\n"
	while 1:
		print "Would you like to add this RFC to the server's list?"
		opt = raw_input("[Y]es/[N]o: ")
		if opt.startswith('Y') or opt.startswith('y'):
			#send add request
			addString = create_add_lookup_string("ADD", rfcNo.split()[1], rfcName)
			response = send(clientSocket, addString)
			print response + "\r\n"
			if response.split()[1] == '200':
				print rfcNo + " added successfully!"
			break
		elif opt.startswith('N') or opt.startswith('n'):
			break
		else:
			print "Not an option"
	
	
def write(content, rfcNo, rfcName):
	global path
	filename = rfcNo + " - " + rfcName
	if not path.endswith('/'):
		path = path + '/'
	result = open(path + filename, 'w')
	result.write(content)
	result.close()
	
def main():
	# intialize a port to serve peers
	global servingPort
	global hostname
	servingSocket.bind(("", 0))
	servingPort = servingSocket.getsockname()[1]
	hostname = hostname #+ "_"+ str(servingPort)
	#print servingPort
	# now register with the central server
	clientSocket.connect((serverName,serverPort)) 

	# get files to serve from the dir that the user has entered
	initial_adds()

	# spawn a new thread to start serving other peers who will download from this peer and this happens in the background
	t = threading.Thread(target = startService, args = (servingSocket,))
	t.start()
	
	# now keep interacting with the user
	while 1:
		print "1. ADD"
		print "2. LOOKUP"
		print "3. LIST"
		print "4. EXIT"
		opt = int(raw_input("Select one of the options above. (Enter only the number): "))
		if opt == 4:
			clientSocket.sendall("EXIT " + hostname)
			#servingSocket.shutdown(1)
			servingSocket.close()
			#clientSocket.shutdown()
			clientSocket.close()
			break
		elif opt == 1:
			rfcName = raw_input("Enter RFC name: ")
			rfcNo = raw_input("Enter RFC number: ")
			add_string = create_add_lookup_string("ADD", rfcNo, rfcName)
			response = send(clientSocket, add_string)
			print response
		elif opt == 2:
			rfcName = raw_input("Enter RFC name (just the title) : ")
			rfcNo = raw_input("Enter RFC number (just the number): ")
			lookup(rfcNo, rfcName)
			
		elif opt == 3:
			listAll()
		else:
			print "Please select correct option!"
		
	print "Bye."
	# close all connections and exit
	#clientSocket.close()
	#servingSocket.close()
	#return
	
if __name__ == "__main__":
	main()

