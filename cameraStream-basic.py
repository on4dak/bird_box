#!/usr/bin/env python3

# ---------------------------------------------------------------------
# Very basic implimentation of fully python implimentation of streaming
# Raspberry Pi camera to uStream using picamera piped to ffmpeg
# internally within this python script using subprocess.Popen
# ---------------------------------------------------------------------

import subprocess
import picamera
from time import sleep, time
from datetime import datetime

# uStream server info
# uStream keys
#RTMP_URL="rtmp://1.21705518.fme.ustream.tv/ustreamVideo/21705518"
#STREAM_KEY="fKb9NJUycD2unefr9JhukXybZBRSB3Wq"
# uStream2 keys
RTMP_URL="rtmp://1.22079439.fme.ustream.tv/ustreamVideo/22079439"
STREAM_KEY="U8LmvKcPe3pCU5gbb5m2pexDXHCRBJDW"

snapshot_frequency = 60 * 60  #frequency of snapshops in seconds

max_images = 24 		# Maximum number of images to keep
re_stream = 0

def start_stream(val):
	global re_stream 
	global stream
	global camera
	start= time()
	last = start
	snap_shot_count = 0
#	stream_now(val)

	if val == "restart":
		print("re-opening pipe")
		stream = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
		sleep(1)

	
	try:
		print("Create camera object")
		camera = picamera.PiCamera()
#		with picamera.PiCamera() as camera:
		camera.resolution = (960, 540)
		camera.framerate = 25
		camera.vflip = True
		camera.hflip = True
		camera.annotate_background = picamera.Color('black')

	except picamera.exc.PiCameraMMALError:
		print("Camera Closed!")
		camera.close()
		print("Is camera recording", camera.recording)
		print("Is camera closed?", camera.closed)

	
	print("About to start recording")
	camera.start_recording(stream.stdin, format='h264', bitrate = 500000)
	
	running = True
	while running:
		i = datetime.now()
		now = i.strftime('%d %b %Y - %H:%M:%S')
		camera.annotate_text = ' Bird Cam - ' + now + ' - restream = ' + str(re_stream) + ' '
		
		try:
			camera.wait_recording(0.2)

		except IOError:
			running = False
			print("PIPE error detected")
			re_stream += 1
			print ("re_stream =", re_stream)
			stream.terminate()
			print("Close camera")
			print("restart stream")
			return("restart")
					
		except KeyboardInterrupt:
			running = False
			camera.stop_recording()
			stream.stdin.close()
			stream.terminate()
			print("Close camera")
			camera.close()
			return("stop")
			
		else:
			if time() - last > snapshot_frequency:  # Take snap shot
				print("taking snap shot No.",snap_shot_count)
				snap_shot('image'+str(snap_shot_count))
				last = time()
				if snap_shot_count >= max_images:
					snap_shot_count = 0
				else:
					snap_shot_count += 1
	
				

def stream_now(val):
	global stream
	global cmdline
	global camera
	if val == "restart":
		print("re-opening pipe")
		stream = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
		sleep(1)
		print("Start Picamera")
		if start_picamera():
			print("About to start recording")
			camera.start_recording(stream.stdin, format='h264', bitrate = 500000)
		else:
			print("This did not work")
			return
	if val == "start":
		print("Start Picamera")
		if start_picamera():
			print("About to start recording")
			camera.start_recording(stream.stdin, format='h264', bitrate = 500000)
		else:
			print("This did not work")
			return
	
#Function to take a snapshop image	
def snap_shot(name):
	camera.capture('images/'+ name +'.jpg', use_video_port=True)  	


def start_picamera():
	global camera
	global stream
	try:
		print("Create camera object")
#			camera = picamera.PiCamera()
		with picamera.PiCamera() as camera:
			camera.resolution = (960, 540)
			camera.framerate = 25
			camera.vflip = True
			camera.hflip = True
			camera.annotate_background = picamera.Color('black')
			return camera
	except picamera.exc.PiCameraMMALError:
		print("Camera Closed!")
		camera.close()
		print("Is camera recording", camera.recording)
		print("Is camera closed?", camera.closed)


# ffmpeg command line
cmdline =['ffmpeg', 
			'-i' , '-', 
			'-vcodec', 'copy', 
			'-an', 
			'-metadata', 'title=\"Ipswich IP1 bird box camera\"', 
			'-f', 'flv',
			 RTMP_URL +'/' + STREAM_KEY]


# Setup up pipe to ffmpeg
print("Setup stream")

stream = subprocess.Popen(cmdline, stdin=subprocess.PIPE)



#Set up picamera
val = start_stream("start")
global camera		
running2 = True
while running2:
	if val == "stop":
		print("CTRL+C pressed, exiting stream")
		break
	elif val == "restart":
		start_stream("restart")	
	else:	
		running2 = False
print("end")

