import os
import pyaudio
from pyfiglet import Figlet
import socket, cv2, pickle, struct, time, threading

# Sets up front end
pyf = Figlet(font='puffy') #figlet= convert ASCII text into ASCII art fonts
a = pyf.renderText("UDP Chat App with Multi-Threading")
os.system("tput setaf 3") #This module provides a portable way of using operating system 
print(a)

# create UDP socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


"""
    connect_to_server()
    
    -Connects to the server, receives the metadata, receives the data, and displays the frames
    onto the screen.

"""
def connect_to_server():
    time.sleep(15)
    
    # Initialize socket for client
    host_ip = '10.0.0.184' 
    port = 56116
    s.connect((host_ip,port)) 
    data = b""  # byte
    metadata_size = struct.calcsize("Q")
    
    # Get metadata for the video
    while True:
        while len(data) < metadata_size:
            packet = s.recv(4*1024) 
        if not packet: break
        data+=packet
    
    packed_msg_size = data[:metadata_size]  # Data msg size
    data = data[metadata_size:]             # Data load
    
    # Get the message size
    msg_size = struct.unpack("Q",packed_msg_size)[0]
    
    # Get the frames for the video stream
    while len(data) < msg_size:
        data += s.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)
        
        # Display images
        cv2.imshow("Receiving Video", frame)
        
        # Exit key
        key = cv2.waitKey(10) 
        if key  == 13:
            break
        
    s.close()
    
"""
    sender()
    
    -The code sets up a server-side application that captures frames from the 
    server's camera and sends them to a connected client over a socket connection.
    

"""
def sender():
    
    # Initialize socket for client
    host_name  = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print('Host IP:',host_ip)
    port = 56116
    socket_address = (host_ip,port)
    
    # Socket Bind
    s.bind(socket_address)
    
    # Socket Listen
    s.listen(5)
    print("Listening at:",socket_address)
    
    # Get connect to client
    while True:
        client_socket,addr = s.accept()
        print('Connected to:',addr)
        # Initializes a video capture object to capture frames from the server's camera
        if client_socket:
            vid = cv2.VideoCapture(1)
            
        # Read frames from the camera and send them to the client   
        while(vid.isOpened()):
            ret,image = vid.read() #It reads a frame from the camera
            img_serialize = pickle.dumps(image)
            message = struct.pack("Q",len(img_serialize))+img_serialize #It creates a message by packing the length of the serialized data
            client_socket.sendall(message)
            cv2.imshow('Video from server',image)
            key = cv2.waitKey(10) #It waits for a key press
            if key ==13:
                client_socket.close()
                
# Initialize PyAudio
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk)

# Audio Socket Initialization
audioSocket = socket.socket()
port1 = 56166
audioSocket.bind(('10.0.0.184',56166))
audioSocket.listen(5)
cAudio, addr = audioSocket.accept()

"""
    recordAudio()
    
    - the code sets up a server-side application that records audio
    and streams it to a connected client over a socket connection
    
"""
# records audio and sends it to a client over a socket connection
def recordAudio():
    time.sleep(5)
    while True:
        data = stream.read(chunk) #the number of audio samples to read at once
        
        #If the audio data is not empty, it sends it to the client
        if data:
            cAudio.sendall(data)
            
"""
    rcvAudio()
    
    - the code sets up a client-side application that receives audio 
    data from a server over a socket connection and plays it
    
"""          
def rcvAudio():
    #receive audio data from the server.
    while True:
        audioData = audioSocket.recv(4096)#The 4096 value is the buffer size used for receiving audio data
        stream.write(audioData)
        
# Creat Threads
x1 = threading.Thread(target = connect_to_server)
x2 = threading.Thread(target = sender)
x3 = threading.Thread(target = recordAudio)
x4 = threading.Thread(target = rcvAudio)

# Start Threads
x1.start()
x2.start()
x3.start()
x4.start()