import os 
import sys
from socket import *
import ssl

host = "127.0.0.1"
if len(sys.argv) != 2:
	print("Please run the application with: python3 client.py server_port")
	sys.exit(1)

client_port = int(sys.argv[1])

#create a tcp client socket and wrap it with ssl for encryption
tcp_client = socket(AF_INET, SOCK_STREAM)
secure_client = ssl.wrap_socket(tcp_client, ssl_version = ssl.PROTOCOL_SSLv23, server_side = False)
secure_client.connect((host, client_port))

print("Connected to server")

while True:
	#take user commnad as input
	request = input("Please enter your command (dl file_name, del file_name, ls, terminate): ")

	#if the command is to terminate, terminate client and server
	if request.startswith("terminate"):
		secure_client.send(request.encode('utf-8'))
		break
	elif request.startswith("dl"):
		secure_client.send(request.encode('utf-8'))
		request, file_name = request.split()
		rec = conn.recv(4096)
		message = rec.decode('utf-8')
		#if the file to be downloaded does not exist, print the warning message
		if message.startswith("The"):
			print(message)
		#if the file exists, first get the file size and then download the binary data
		else:
			file_size = int(message)
			file = open(file_name, 'wb')
			received_bytes = 0
			while received_bytes < file_size:
				binary_data = secure_client.recv(1024)
				file.write(binary_data)
				received_bytes += 1024
			file.close()
			print("Download complete")
	#if the command is to list the files in the current directory, send the request and print the message or file list
	elif request.startswith("ls"):
		secure_client.send(request.encode('utf-8'))
		rec = secure_client.recv(8192)
		message = rec.decode('utf-8')
		#print out the message if there's no file in the current directory
		if message.startswith("There's"):
			print(message)
		#print out the file list
		else:
			files = message.split()
			for file in files:
				print(file)
	#if the command is to delete a file, send the request to the server and print the response
	elif request.startswith("del"):
		secure_client.send(request.encode('utf-8'))
		rec = conn.recv(4096)
		message = rec.decode('utf-8')
		print(message)
	#if the command does not match any of the above commands, print a warning message and start over
	else:
		print("Invalid command")
		continue

secure_client.close()