from pyforms.Controls 	import ControlText
from pyforms.Controls 	import ControlProgress
from pyforms.Controls 	import ControlSlider
from pyforms.Controls 	import ControlCombo
from pyforms.Controls 	import ControlButton
from pyforms.Controls 	import ControlPlayer
from pyforms.Controls 	import ControlList
from pyforms.Controls 	import ControlFile
from pyforms 			import BaseWidget
import cv2, numpy as np, pickle, math
from PyQt4 import QtGui, QtCore

from geometry_designer.modules.geometry_from_threshold.GeometryFromThreshold import GeometryFromThreshold


def pointsDistance(p1, p2): 			return  math.hypot(p2[0]-p1[0], p2[1]-p1[1])
def createRectanglePoints(start, end): 	return [ start, (end[0],start[1]), end, (start[0],end[1]) ]

def createEllipsePoints( start, end ):
	width = end[0]-start[0]
	height = end[1]-start[1]
	center = ( start[0] + width/2, start[1] + height/2 )
	
	distance = pointsDistance(start, end )
	nPoints = distance / 30
	if nPoints<8:nPoints = 8.0

	points = []
	for angleR in np.arange(0, math.pi*2, math.pi/nPoints):
		x = int(round(center[0] + width/2 * np.cos(angleR) ))
		y = int(round(center[1] + height/2 * np.sin(angleR)))
		points.append( ( x,y) )
	return points

def createCirclePoints( center, radius):
	nPoints = radius / 30
	if nPoints<8:nPoints = 8.0

	points = []
	for angleR in arange(0, math.pi*2, math.pi/nPoints):
		x = int(round(center[0] + radius * cos(angleR) ))
		y = int(round(center[1] + radius * sin(angleR)))
		points.append( ( x,y) )
	return points





class GeometryManualDesigner(BaseWidget):

	def __init__(self, title, parent=None):
		super(GeometryManualDesigner, self).__init__(title, parentWindow=parent)

		self._threshold_win  = None
		self._startPoint 	= None
		self._endPoint 		= None

		self._selectedPoly = None
		self._selectedPoint = None
		

		self._video  = ControlFile("Video file")
		self._player = ControlPlayer("Video")
		self._remove = ControlButton("Remove")
		self._square = ControlButton("Square", checkable=True)
		self._circle = ControlButton("Circle", checkable=True)
		self._threshold = ControlButton("Threshold")
		self._export 	= ControlButton("Export")
		self._import 	= ControlButton("Import")
		self._polygons 	= ControlList('Polygons')

		self._apply 	= ControlButton('Apply')

		self._formset 	= [ '_video',"_player", ("_square", "_circle", "_threshold", " ","_remove"," ", "_export", "_import"), "=", "_polygons",'_apply' ]

		self._video.changed 	= self.videoSelected
		self._square.value  	= self.square_toggle
		self._circle.value  	= self.circle_toggle
		self._remove.value  	= self.remove_clicked
		self._export.value  	= self.export_clicked
		self._import.value  	= self.import_clicked
		self._threshold.value  	= self.threshold_btn_click
				
		self._player.onDrag    		= self.on_player_drag_in_video_window
		self._player.onEndDrag 		= self.on_player_end_drag_in_video_window
		self._player.onClick   		= self.on_player_click_in_video_window
		self._player.onDoubleClick 	= self.on_player_double_click_in_video_window
		self._player.processFrame   = self.process_frame
		self._player.onKeyRelease 	= self.on_player_key_release

		self._apply.hide()

		#self._video.value = '/home/ricardo/Desktop/Ai35_3_Ai35xa2aCre14Hz_35ms_Lside_Lp.avi'

	def on_player_key_release(self, event):
		if event.key() == QtCore.Qt.Key_Delete:
			if self._selectedPoly!=None and self._selectedPoint!=None:
				poly = self._polygons.getValue( 1, self._selectedPoly )
				try:
					points = eval(poly)
					p = points.pop(self._selectedPoint)
					self._polygons.setValue( 1, self._selectedPoly, points )
				except: pass
				if not self._player.is_playing: self._player.refresh()

	def export_clicked(self):
		filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Choose a file', '') )
		if filename!="":
			output = open( filename, 'w')
			for values in self._polygons.value: output.write(';'.join(values)+'\n')
			output.close()

	def import_clicked(self):
		filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Choose a file', '') )
		if filename!="":
			infile 	 = open( filename, 'r');
			polygons = []
			for line in infile:
				values = line.split(';')
				name   = values[0]
				poly   = values[1]
				polygons.append( (name, poly) )
			self._polygons.value += polygons

	def process_frame(self, frame):
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):		
			points = eval(obj[1])
			cv2.polylines(frame, [np.array(points,np.int32)], True, (0,255,0), 1, lineType=cv2.LINE_AA)			
			for pointIndex, point in enumerate( points ):
				if self._selectedPoint == pointIndex and objIndex==self._selectedPoly:
					cv2.circle(frame, point, 4, (0,0,255), 2)
				else:
					cv2.circle(frame, point, 4, (0,255,0), 2)
			
		if self._startPoint and self._endPoint:
			if self._square.checked:
				cv2.rectangle(frame, self._startPoint, self._endPoint, (233,44,44), 1 )
			elif self._circle.checked and self._endPoint[0]>self._startPoint[0] and self._endPoint[1]>self._startPoint[1]:
				width = self._endPoint[0]-self._startPoint[0]
				height = self._endPoint[1]-self._startPoint[1]
				center = ( self._startPoint[0] + width/2, self._startPoint[1] + height/2 )
				
				cv2.ellipse( frame, center, (width/2,height/2), 0, 0, 360, (233,44,44), 1 )
				
		return frame

	def selectPoint(self,x, y):
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):
			try:
				mouseCoord 	= ( x, y )					
				points 		= eval(obj[1])
				for pointIndex, point in enumerate( points):
					if pointsDistance( mouseCoord, point ) <= 5:
						self._selectedPoint = pointIndex
						self._selectedPoly = objIndex
						return
				self._selectedPoint = None
				self._selectedPoly = None
			except: pass


	def getIntersectionPoint(self, testPoint, point1, point2, tolerance = 5):
		vector = ( point2[0]-point1[0], point2[1]-point1[1] )
		p0 = point1
		if vector[0]!=0:
			k = float(testPoint[0] - p0[0]) / float(vector[0])
			y = float(p0[1]) + k * float(vector[1]) 
			if point2[0]>point1[0]:
				maxValue = point2[0]
				minValue = point1[0]
			else:
				maxValue = point1[0]
				minValue = point2[0]
			if abs(y-testPoint[1])<=tolerance and testPoint[0]<=maxValue and testPoint[0]>=minValue: return testPoint
			else: return None
		elif vector[1]!=0:
			k = float(testPoint[1] - p0[1]) / float(vector[1])
			x = float(p0[0]) + k * float(vector[0])
			if point2[1]>point1[1]: 
				maxValue = point2[1]
				minValue = point1[1]
			else:
				maxValue = point1[1]
				minValue = point2[1]
			if abs(x-testPoint[0])<=tolerance and testPoint[1]<=maxValue and testPoint[1]>=minValue: return testPoint
			else: return None
		else: return None

	def on_player_double_click_in_video_window(self, event, x, y):
		mouse = ( int(x), int(y) )
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):
			try:
				points = eval(obj[1])
				n_points = len(points)
				for pointIndex, point in enumerate( points ):
					next_point = points[ (pointIndex+1) % n_points ]
					intersection = self.getIntersectionPoint(mouse, point, next_point )
					if intersection != None:
						self._selectedPoly = objIndex
						points.insert( pointIndex + 1, intersection )
						self._polygons.setValue( 1, self._selectedPoly, points )
						self._selectedPoint = pointIndex + 1
						if not self._player.is_playing: self._player.refresh()
						return
			except: pass

	
	def on_player_click_in_video_window(self, event, x, y):
		self.selectPoint( int(x), int(y) )
		if not self._player.is_playing: self._player.refresh()

	def on_player_drag_in_video_window(self, startPoint, endPoint):
		self._startPoint = ( int(startPoint[0]), int(startPoint[1]) )
		self._endPoint = ( int(endPoint[0]), int(endPoint[1]) )

		if self._selectedPoly!=None and self._selectedPoint!=None:
			poly = self._polygons.getValue( 1, self._selectedPoly )
			try:
				points = eval(poly)
				points[self._selectedPoint] = self._endPoint
				self._polygons.setValue( 1, self._selectedPoly, points )
			except: pass

		if not self._player.is_playing: self._player.refresh() 
			
	def on_player_end_drag_in_video_window(self, startPoint, endPoint):
		self._startPoint = int(startPoint[0]), int(startPoint[1])
		self._endPoint 	 = int(endPoint[0]),   int(endPoint[1])

		points = None
		if self._square.checked:
			points = createRectanglePoints(self._startPoint, self._endPoint)
		elif self._circle.checked and self._endPoint[0]>self._startPoint[0] and self._endPoint[1]>self._startPoint[1]:
			points = createEllipsePoints(self._startPoint, self._endPoint)

		if points: self._polygons += ["Poly_%d" % self._polygons.count, points]

		self._startPoint = None
		self._endPoint = None
		self._square.checked = False
		self._circle.checked = False


	def __add_contours_from_threshold_win(self, contours):
		for contour in contours:
			if contour.any(): 
				points = [tuple(p[0]) for p in contour.tolist()]
				self._polygons += ["Poly_%d" % self._polygons.count, points]

	def videoSelected(self): self._player.value = self._video.value
		
	def square_toggle(self, checked):
		if checked:
			self._circle.checked = False

	def circle_toggle(self, checked):
		if checked:
			self._square.checked = False

	def threshold_btn_click(self):
		if self._threshold_win is None:
			self._threshold_win = GeometryFromThreshold(self)
			self._threshold_win.add_contours = self.__add_contours_from_threshold_win
		
		self._threshold_win.show()
		if len(self._video.value)>0: self._threshold_win._filename.value = self._video.value




	def remove_clicked(self):
		self._polygons -= -1 #Remove the selected row


	@property
	def polygons(self):
		polys = []
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):		
			points = eval(obj[1])
			polys.append( np.array(points,np.int32) )
		return np.array(polys)	

	@property
	def apply_evt(self): return self._apply.value
	@apply_evt.setter
	def apply_evt(self, value): 
		self._apply.value = value
		self._show_apply = value is not None
		

	def show(self):
		super(GeometryManualDesigner, self).show()
		if hasattr(self,'_show_apply') and self._show_apply: self._apply.show()