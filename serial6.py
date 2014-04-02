import bpy
import Blender as B
import math as M
import serial
import time


serIn = serial.Serial('COM7', 115200)
serOut = serial.Serial('COM3', 9600)


k = 0

target = 100

print 'Running...'

# clear scene
scns = B.Scene.Get()	# get a list of all scenes in Blender
for i in scns:			# get each scene in the list
	scn = i
	obs = list(scn.objects)		# get a list of all objects in scene
	for j in obs:				# get each object in the scene
		scn.unlink(j)			# unlink the object from the scene

B.Redraw(-1) 		# update all of the views in the user inteface

scene = B.Scene.getCurrent()

# create a new object
myModel = B.Object.New('Mesh', 'myModel')
mesh = B.Mesh.New('Plane')

s = 1 # number of scans
t = s # temp variable for s

stepSize = 10



# while actuator is not fully extended and end of object has not been reached
while (target < 3900) & (t > 0):
	i = 0		# index in data array
	
	l = serIn.inWaiting() # number of characters waiting to be read
	
	if (l > 0):
		time.sleep(1) # delays for 1 second
		l = serIn.inWaiting()
		data = serIn.readline(l)
	
	#	print l
		print data
	
	
		while (i < l):
			if (data[i:i+4] == "COM:"):
				
				j = i + 4
				
				while (j < l):
					if (data[j:j+5] == "SCAN:"):
						
						ir = data[i+4:j-1].split(",")
	#					print ir
						t = s
						scans = data[j+5:].split(",")
						s = int(scans[0])
		#				print s
						
						if (s == 0):
							s = t + 1
							t = 0
						else:
							t = s
							
					j = j + 1
					
				n = 0	#  index of ir sensor values
				
				print 'converting to cm'
				#convert voltages to centimeters
				while (n < 360):
					
					cm = ir 	# new array to store centmeters
					
				#	cm[n] = 0.065041 / (float(ir[n]) * 0.0048828125) + 0.035
					
				#	print n
					
					cm[n] = float((2914 / (float(ir[n]) + 5)) - 1) 
					
					n = n + 1
				
				n = 0
				
	#			print cm
				
#				print 'calibrating'
				# calibrate distances
				while (n < 360):
					
					avCm = cm		#new array to store final values
					
					x = 1
					sum =  6 * cm[n]
					
					#print 'sum -'
					
					# sum up all values from cm[n - 5] to cm[n - 1]
					while (x <= 5):
						if (n-x) < 0:
							sum = sum + (6 - x) * cm[360 + n - x]
						else:
							sum = sum + (6 - x) * cm[n - x]
							
						x = x + 1
					#print 'sum +'
					x = 1
						
					# sum up all values from cm[n + 5] to cm[n + 1]
					while (x <= 5):
						if (n+x) >= 360:
							sum = sum + (6 - x) * cm[n + x - 360]
						else:
							sum = sum + (6 - x) * cm[n + x]
							
						x = x + 1
						
					avCm[n] = float(sum) / 36
					
					#if (n == 1):
						#avCm[n - 1] = avCm[n]
					
					n = n + 1
					
				n = 0
					
				while (n < 360):
					
			#		print 'here'
					x = float(avCm[n]) * M.cos(M.radians(n + 90)) # x coordinate of new vertex
					
					y = float(avCm[n]) * M.sin(M.radians(n + 90)) # y coordinate of new vertex
					
					z = target * float(12) / 4096 * 2.54
					
					v = [x, y, z]	# new vertex 
					
	#				print v
					
					coords = [v]
				
					mesh.verts.extend(coords)          # add vertices to mesh
				
					if (s > 1):
						if (n > 0):
							
							faces = [[n+(s-1)*360, n-1+(s-1)*360, n-1+(s-2)*360, n+(s-2)*360]]
							
							mesh.faces.extend(faces)           # add faces to the mesh (also adds edges)
								
							if (n == 359):
								
								faces = [[(s-1)*360, n+(s-1)*360, n+(s-2)*360, (s-2)*360]]
								
								mesh.faces.extend(faces)           # add faces to the mesh (also adds edges)
							
							
						
						
					
					n = n + 1
				
				#input = 360
				#data.split(data[i+4:])
		#	else:
			#	if (input == 0):
				#	if (data[i:i+5] == "SCAN:"):
				
				print t
				target = t * stepSize + 100
				
				if (t == 0):
					target = 0
				
				byte1 = 0xC0 + (target & 0x1F)
				byte2 = (target >> 5) & 0x7F
			
				#com2 = 225
				
				#if (com3 == 127):
				#	com3 = 100
				#else:
				#	com3 = com3 + 3
				
				
				serOut.write(chr(byte1))
				serOut.write(chr(byte2))
				
				serOut.write(chr(byte1))
				serOut.write(chr(byte2))
				
				print "target: "
				print target
				
			#	target = target + 50
				
			#print data[i]
			
			i = i + 1
			
myModel.link(mesh)		# link mesh to object
#mesh.remDoubles(LaneWidth/10)	# remove duplicate vertices from mesh object
scene.link(myModel)   	# link our new object into scene	
B.Redraw(-1)
		

serIn.close()
serOut.close()