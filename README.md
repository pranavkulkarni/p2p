# p2p
A peer-peer file sharing system

The file peer.py has the peer code and the file server.py has the server code.
Some naming conventions and pre-requisites - 
1. Provide a full directory name where the RFCs will be downloaded or where the RFCs are already present.
2. As per the project description, we have followed the naming convention of a RFC document as follows: "RFC <RFC number> - <RFC title>"

Instructions to run:
First run server.py on a machine (it will pickup localhost as the ip address)
Then run peer.py <ip address of the server> (please run the peer with the ip address of the server as the argument)
When the peer is run, it will ask for a directory. Please enter the full path to the directory where RFCs are stored or RFCs will be downloaded to. The program is interactive. At each step, for example, you need to enter the number corresponding to an operation like ADD, LOOKUP, LIST, EXIT.

############# Commands (example) ############# 

`python server.py`

`python peer.py 152.46.20.136`

Input: `/home/pkulkar5/projectdemo/rfcdata`
