from pygame.locals import *
from pygame import gfxdraw
import numpy as np
import math as m
import pygame

width = 1080
height = 720

class r:
	red = [230, 0, 0]
	dred = [200, 0, 0]
	white = [255, 255, 255]
	brown = [120, 65, 40]
	black = [20, 20, 20]
	yellow = [255, 255, 0]
	blue = [0, 20, 255]
	dblue = [5, 25, 240]
	green = [0, 128, 0]
	dgreen = [0, 90, 0]
	orange = [255, 165, 0]
	purple = [128, 0, 128]

def rotationX(a): 
	return([[1, 0, 0],
			[0, m.cos(a), -m.sin(a)],
			[0, m.sin(a), m.cos(a)]])
			
def rotationY(a): 
	return([[m.cos(a), 0, m.sin(a)],
			[0, 1, 0],
			[-m.sin(a), 0, m.cos(a)]])
			
def rotationZ(a): 
	return([[m.cos(a), -m.sin(a), 0],
			[m.sin(a), m.cos(a), 0],
			[0, 0, 1]])

def thick_aaline(screen, p1, p2, thickness):
	length = m.hypot(p2[1] - p1[1], p2[0] - p1[0])
	center_L1 = ( (p1[0] + p2[0])/2, (p1[1] + p2[1])/2 )
	angle = m.atan2(p2[1] - p1[1], p2[0] - p1[0])
	UL = (center_L1[0] + (length / 2.) * m.cos(angle) - (thickness / 2.) * m.sin(angle),
		  center_L1[1] + (thickness / 2.) * m.cos(angle) + (length / 2.) * m.sin(angle))
	UR = (center_L1[0] - (length / 2.) * m.cos(angle) - (thickness / 2.) * m.sin(angle),
		  center_L1[1] + (thickness / 2.) * m.cos(angle) - (length / 2.) * m.sin(angle))
	BL = (center_L1[0] + (length / 2.) * m.cos(angle) + (thickness / 2.) * m.sin(angle),
		  center_L1[1] - (thickness / 2.) * m.cos(angle) + (length / 2.) * m.sin(angle))
	BR = (center_L1[0] - (length / 2.) * m.cos(angle) + (thickness / 2.) * m.sin(angle),
		  center_L1[1] - (thickness / 2.) * m.cos(angle) - (length / 2.) * m.sin(angle))

	pygame.gfxdraw.filled_polygon(screen, (UL, UR, BR, BL), r.blue)
	pygame.gfxdraw.aapolygon(screen, (UL, UR, BR, BL), r.black)

class ThreeD_Space():
	def __init__(self, origin, scale):
		self.origin = origin
		self.scale = scale
		
		self.st_lines = []
		self.dy_lines = []
		self.st_faces = []
		self.dy_faces = []
		self.faces = []
		self.lines = []
		self.x_a = self.y_a = self.z_a = 0
		self.x_pos = self.y_pos = self.z_pos = 0    
		
	def add_static_line(self, points):
		self.st_lines.append(points)
		
	def add_dynamic_line(self, points):
		self.dy_lines.append(points)
		
	def add_static_face(self, points, doubled=False):
		self.st_faces.append(points)
		if doubled:
			self.rev = []
			for point in points:
				self.rev.insert(0, point)
			self.st_faces.append(self.rev)

	def add_dynamic_face(self, points, doubled=False):
		self.dy_faces.append(points)
		if doubled:
			self.rev = []
			for point in points:
				self.rev.insert(0, point)
			self.dy_faces.append(self.rev)
		
	def set_angle(self, a, ang):
		if a == 'x': self.x_a = ang
		if a == 'y': self.y_a = ang
		if a == 'z': self.z_a = ang
		
	def set_pos(self, p, pos):
		if p == 'x': self.x_pos = pos
		if p == 'y': self.y_pos = pos
		if p == 'z': self.z_pos = pos
		
	def get_cam_pos(self):
		self.cam_pos = [0, 0, -5]
		self.cam_pos = np.dot(np.linalg.inv(rotationX(self.x_a)), self.cam_pos)
		self.cam_pos = np.dot(np.linalg.inv(rotationY(self.y_a)), self.cam_pos)

	
	def render_faces(self, screen, persp, culling=True):
		self.get_cam_pos()
		self.faces = list(self.st_faces)
		for f in self.dy_faces:
			self.faces.append(f)
		
		self.sorted_faces = []
		for face in self.faces:
			self.middles = []
			self.middle = [0,0,0]
			for i in range(int(len(face)/2)):
				self.middles.append(((face[2*i][0]+face[(2*i)+1][0])/2, ((face[2*i][1]+face[(2*i)+1][1])/2), ((face[2*i][2]+face[(2*i)+1][2])/2)))
			for mid	in self.middles:
				self.middle = [self.middle[0]+mid[0], self.middle[1]+mid[1], self.middle[2]+mid[2]]
			self.middle = [self.middle[0]/len(self.middles),self.middle[1]/len(self.middles),self.middle[2]/len(self.middles)]
			# self.dy_lines.append(((self.middle, self.middle)))
		
			self.distance = m.sqrt((self.middle[0]-self.cam_pos[0])**2 + (self.middle[1]-self.cam_pos[1])**2 + (self.middle[2]-self.cam_pos[0])**2)
			self.sorted_faces.append((face, self.distance))
		
		self.sorted_faces = sorted(self.sorted_faces, key = lambda x: x[1])
		for item in self.sorted_faces:
			self.faces.append((item[0]))
		
		for face in self.faces:
			self.face_2d = []
			for point in face:
				t = [point[0]+self.x_pos,
					 point[1]+self.y_pos,
					 point[2]+self.z_pos]
				self.rot = np.dot(rotationZ(self.z_a), t)
				self.rot = np.dot(rotationY(self.y_a), self.rot)
				self.rot = np.dot(rotationX(self.x_a), self.rot)
				self.z = 1/(2 - self.rot[2]*persp) #adds perspective
				projection = [[self.z, 0, 0],
							  [0, self.z, 0]]
				self.face_2d.append(np.dot(projection, self.rot))
			
			self.sum = 0 # backface culling
			for i in range(len(self.face_2d)):
				if  i == len(self.face_2d)-1:
					self.sum += (self.face_2d[0][0] - self.face_2d[i][0]) * (self.face_2d[0][1] + self.face_2d[i][1])
				else:
					self.sum += (self.face_2d[i+1][0] - self.face_2d[i][0]) * (self.face_2d[i+1][1] + self.face_2d[i][1])

			if (self.sum > 0 and self.z > 0 and self.z < 3) or culling == False:
				self.s_points = []
				for point in self.face_2d:
					self.s_points.append(point*self.scale+self.origin)
				self.color = r.red
				pygame.gfxdraw.filled_polygon(screen, (self.s_points), Color(255, 0, 0, 50)) #self.color
				# pygame.gfxdraw.aapolygon(screen, (self.s_points), Color(255, 0 ,0 ,0)) #r.black
		self.dy_faces = []
		
	def render_lines(self, screen, persp):
		self.get_cam_pos() 
		self.lines = ''
		self.lines = list(self.st_lines)
		for l in self.dy_lines:
			self.lines.append(l)
		
		self.sorted_lines = [] # depth sorter
		for line in self.lines:
			self.middle = (((line[0][0]+line[1][0])/2), ((line[0][1]+line[1][1])/2), ((line[0][2]+line[1][2])/2))
			self.distance = m.sqrt((self.middle[0]-self.cam_pos[0])**2 + (self.middle[1]-self.cam_pos[1])**2 + (self.middle[2]-self.cam_pos[0])**2)
			self.sorted_lines.append((line, self.distance))
		
		self.sorted_lines = sorted(self.sorted_lines, key = lambda x: x[1])
		for item in self.sorted_lines:
			self.lines.append((item[0]))
		
		for line in self.lines: #transpose lines
			self.s_lines = []
			self.line_2d = []
			for point in line:
				t = [point[0]+self.x_pos,
					 point[1]+self.y_pos,
					 point[2]+self.z_pos]
				self.rot = np.dot(rotationZ(self.z_a), t)
				self.rot = np.dot(rotationY(self.y_a), self.rot)
				self.rot = np.dot(rotationX(self.x_a), self.rot)
				self.z = 1/(2 - self.rot[2]*persp)
				projection = [[self.z, 0, 0],
							  [0, self.z, 0]]
				self.line_2d.append(np.dot(projection, self.rot))
				
			if self.z > 0 and self.z < 3:
				for point in self.line_2d:
					self.s_lines.append(point*self.scale+self.origin)		
			
			thick_aaline(screen, self.s_lines[0], self.s_lines[1], 8)
			for point in self.line_2d:
				pygame.gfxdraw.filled_circle(screen, int(point[0]*self.scale+self.origin[0]),int(point[1]*self.scale+self.origin[1]), 6, r.black)
				pygame.gfxdraw.aacircle(screen, int(point[0]*self.scale+self.origin[0]),int(point[1]*self.scale+self.origin[1]), 6, r.black)
		self.dy_lines = []