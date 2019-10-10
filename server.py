import os 
import sys
from socket import *
import ssl

host = "127.0.0.1"
if len(sys.argv) != 2:
	print("Please run the application with: python3 server.py server_port")
	sys.exit(1)

server_port = int(sys.argv[1])

#create a tcp server socket and wrap it with ssl for encryption
tcp_server = socket(AF_INET, SOCK_STREAM)
secure_server = ssl.wrap_socket(tcp_server, ssl_version = ssl.PROTOCOL_SSLv23, server_side = True, certfile = "server.crt", keyfile = "server.key")
secure_server.bind((host, server_port))
secure_server.listen(5)

termin = False

print("Server is listening for requests from client.")

while True:
  #connect client with server
  (secure_comm_socket, client_addr) = secure_server.accept()
  print("Accept connection from client: " + str(client_addr))

  while True:
    #decode the request from the client
    rec = secure_comm_socket.recv(4096)
    msg = rec.decode('utf-8')
    #if the request is to terminate the application, terminate and close the sockets
    if msg == "terminate":
      termin = True
      break
    #if the request is to list current files, get the file list or generate a message and send it to the client
    elif msg == "ls":
      files = os.listdir()
      if not files:
        msg = "There's no file in the current directory"
        secure_comm_socket.send(msg.encode('utf-8'))
      else:
        file_list = " ".join(files)
        secure_comm_socket.send(file_list.encode('utf-8'))
    # if the request contains a file name, parse the request and determine request type
    else:
      request, file_name = msg.split(" ")
      #if the request is to delete a file
      if request == "del":
        #if the file exists, delete and send a success message
        if os.path.isfile(file_name):
          os.path.remove(file_name)
          secure_comm_socket.send("Deletion is successful".encode('utf-8'))
        #if the file doesn't exist, send a failure message
        else:
          secure_comm_socket.send("The file does not exist".encode('utf-8'))
      #if the request is to download a file
      else:
        #if the file exists, get the file size and send the binary data
        if os.path.isfile(file_name):
          msg = str(os.stat(file_name).st_size)
          secure_comm_socket.send(msg.encode('utf-8'))
          file = open(file_name, 'rb')
          binary_data = file.read(1024)
          while binary_data:
            secure_comm_socket.send(binary_data)
            binary_data = file.read(1024)
          file.close()
        #if the file does not exists, send a message to the client
        else:
          msg = "The file you are trying to download does not exist"
          secure_comm_socket.send(msg.encode('utf-8'))

  if termin:
    break

secure_server.close()
secure_comm_socket.close()