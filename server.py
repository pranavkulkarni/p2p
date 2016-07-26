#open connection on 7734
#input - input string
#eachpeer - tuples with each peer detail
#peers - list of eachpeer tuples
#eachrfc - tuples with each rfcindex detail
#rfcindex - list of eachrfc tuples

from socket import *
import threading

status_codes = {}
status_codes[200] = 'OK'
status_codes[400] = 'Bad Request'
status_codes[404] = 'Not Found'
status_codes[505] = 'P2P-CI Version Not Supported'

peers = []
rfcindex = []


#version = "P2P-CI/1.0"

def extract_add_lookup(extract_string):
	lines = extract_string.split('\r\n')
	host = lines[1].split()[1]
	''' if we need to handle the part where host can have a space
	host_parts = lines.split('\r\n')
	host = host_parts[1]
	i = 2
	while i < len(host_parts)
		host = host + " " + host_parts[i]
		i = i + 1''' 
	
	port = int(lines[2].split()[1])
	
	title_parts = lines[3].split()
	title = title_parts[1]
	i = 2
	length = len(title_parts)
	while i < length:
		title = title + " " + title_parts[i]
		i = i + 1
	
	rfcnum = int(lines[0].split()[2])
	version = lines[0].split()[3]
	
	return host, port, title, rfcnum, version
#end of extract function


def create_details_string(rfclist):
	details = ""
	for item in rfclist:
		hostdetails = [iter for iter in peers if iter[0] == item[2]]
		if len(hostdetails) > 0:
			details = details + "RFC " + str(item[0]) + " " + item[1] + " " + hostdetails[0][0] + " " + str(hostdetails[0][1]) + "\r\n"
	
	return details
#end of create details string function


#ADD function
def add(add_string):
	host, port, title, rfcnum, version = extract_add_lookup(add_string)
	
	eachpeer = (host, port)
	eachrfc = (rfcnum, title, host)
	
	if eachpeer not in peers:
		peers.append(eachpeer)
	
	if eachrfc not in rfcindex:
		rfcindex.append(eachrfc)
	
	status_code = 200
	return_string = version + " " + str(status_code) + " " + status_codes[status_code] + "\r\n" + "RFC" + " " + str(rfcnum) + " " + title + " " + host + " " + str(port) + "\r\n\r\n"
	
	return return_string
#end of add function


#LOOKUP function
def lookup(lookup_string):
	host, port, title, rfcnum, version = extract_add_lookup(lookup_string)
	
	lookup_result = [item for item in rfcindex if item[0] == rfcnum and item[1] == title]
	
	status_code = 200
	if len(lookup_result) == 0:
		status_code = 404
		details = ""
	else:
		details = create_details_string(lookup_result)
		if len(details) == 0:
			status_code = 404
	
	return_string = version + " " + str(status_code) + " " + status_codes[status_code] + "\r\n"
	return_string = return_string + "\r\n" + details + "\r\n"
	
	return return_string
#end of lookup function


#LIST function
def listAll(list_string):
	version = list_string.split('\r\n')[0].split()[2]
	status_code = 200
	if len(rfcindex) == 0:
		status_code = 404
		details = ""
	else:
		details = create_details_string(rfcindex)
		if len(details) == 0:
			status_code = 404
	
	return_string = version + " " + str(status_code) + " " + status_codes[status_code] + "\r\n"
	return_string = return_string + "\r\n" + details + "\r\n"
	
	return return_string
#end of list function

def child(connSocket, addr):
	global peers
	global rfcindex
	print "New peer connected."
	resp = ""
	while 1:
		msg = connSocket.recv(4096)
		if msg.startswith("ADD"):
			resp = add(msg)
		elif msg.startswith("LOOKUP"):
			resp = lookup(msg)
		elif msg.startswith("LIST"):
			resp = listAll(msg)
		elif msg.startswith("EXIT"):
			removeHost = msg.split()[1]
			#print " ################### Before removing ###################"
			#print peers
			#print rfcindex
			print "removing host..." + removeHost
			temp = [i for i in peers if removeHost != i[0]]
			peers = temp
			temp = [i for i in rfcindex if removeHost != i[2]]
			rfcindex = temp
			connSocket.close()
			#print peers
			#print rfcindex
			return
		connSocket.sendall(resp)
		#print "All data sent... ", resp
	
serverName = "localhost"
serverPort = 7734
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print "The server is ready..."
while 1:
	connSocket, addr = serverSocket.accept()
	t = threading.Thread(target = child, args = (connSocket, addr,))
	t.start()
	
		

