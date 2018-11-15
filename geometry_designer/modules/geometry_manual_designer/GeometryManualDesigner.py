from confapp import conf
from pyforms.controls 	import ControlText
from pyforms.controls 	import ControlProgress
from pyforms.controls 	import ControlSlider
from pyforms.controls 	import ControlCombo
from pyforms.controls 	import ControlButton
from pyforms.controls 	import ControlPlayer
from pyforms.controls 	import ControlList
from pyforms.controls 	import ControlFile
from pyforms.basewidget import BaseWidget
import cv2, numpy as np, pickle, math, AnyQt
from geometry_designer.modules.geometry_from_threshold.GeometryFromThreshold import GeometryFromThreshold

if conf.PYFORMS_MODE=='GUI':
	from AnyQt.QtWidgets import QFileDialog
	from AnyQt import QtCore

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
		super(GeometryManualDesigner, self).__init__(title, parent_win=parent)

		self._threshold_win  = None
		self._start_point 	= None
		self._end_point 		= None

		self._selected_poly = None
		self._selected_point = None
		

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

		self._video.changedchanged_event 	= self.videoSelected
		self._square.value  	= self.square_toggle
		self._circle.value  	= self.circle_toggle
		self._remove.value  	= self.remove_clicked
		self._export.value  	= self.export_clicked
		self._import.value  	= self.import_clicked
		self._threshold.value  	= self.threshold_btn_click
				
		self._player.drag_event 	 		= self.on_player_drag_in_video_window
		self._player.end_drag_event	 		= self.on_player_end_drag_in_video_window
		self._player.click_event   	 		= self.on_player_click_in_video_window
		self._player.double_click_event 	= self.on_player_double_click_in_video_window
		self._player.process_frame_event 	= self.process_frame
		self._player.key_release_event  	= self.on_player_key_release

		self._apply.hide()

	def on_player_key_release(self, event):
		if event.key() == QtCore.Qt.Key_Delete:
			if self._selected_poly!=None and self._selected_point!=None:
				poly = self._polygons.get_value( 1, self._selected_poly )
				try:
					points = list(eval(poly))
					p = points.pop(self._selected_point)
					self._polygons.set_value( 1, self._selected_poly, str(points)[1:-1] )
					if not self._player.is_playing: self._player.refresh()
				except:
					pass

	def export_clicked(self):
		filename = str(QFileDialog.getSaveFileName(self, 'Choose a file', '') )
		if filename!="":
			output = open( filename, 'w')
			for values in self._polygons.value: output.write((';'.join(values)+'\n'))
			output.close()

	def import_clicked(self):
		filename = str(QFileDialog.getOpenFileName(self, 'Choose a file', '') )
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
			cv2.polylines(frame, [np.array(points,np.int32)], True, (0,255,0), 2, lineType=cv2.LINE_AA)			
			for pointIndex, point in enumerate( points ):
				if self._selected_point == pointIndex and objIndex==self._selected_poly:
					cv2.circle(frame, point, 4, (0,0,255), 2)
				else:
					cv2.circle(frame, point, 4, (0,255,0), 2)
			
		if self._start_point and self._end_point:
			if self._square.checked:
				cv2.rectangle(frame, self._start_point, self._end_point, (233,44,44), 2 )
			elif self._circle.checked and self._end_point[0]>self._start_point[0] and self._end_point[1]>self._start_point[1]:
				width = self._end_point[0]-self._start_point[0]
				height = self._end_point[1]-self._start_point[1]
				center = ( self._start_point[0] + width/2, self._start_point[1] + height/2 )
				
				cv2.ellipse( frame, (center, (width,height), 0), (233,44,44), 2 )
	
		return frame

	def selectPoint(self,x, y):
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):
			try:
				mouseCoord 	= ( x, y )					
				points 		= eval(obj[1])
				for pointIndex, point in enumerate( points):
					if pointsDistance( mouseCoord, point ) <= 5:
						self._selected_point = pointIndex
						self._selected_poly = objIndex
						return
				self._selected_point = None
				self._selected_poly = None
			except: pass


	def get_intersection_point_distance(self, test_point, point1, point2):
		p1 = np.float32(point1)
		p2 = np.float32(point2)
		p3 = np.float32(test_point)
		dist = np.linalg.norm(np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1)
		return dist


	def on_player_double_click_in_video_window(self, event, x, y):
		mouse = ( int(x), int(y) )
		rows  = self._polygons.value

		distances = []
		for obj_index, obj in enumerate(rows):
			try:
				points = list(eval(obj[1]))
				n_points = len(points)
				for point_index, point in enumerate( points ):
					next_point = points[ (point_index+1) % n_points ]
					distance = self.get_intersection_point_distance(mouse, point, next_point )
					if distance<=5: 
						vector = next_point[0]-point[0], next_point[1]-point[1]
						center = point[0]+vector[0]/2,point[1]+vector[1]/2
						radius = pointsDistance(center, point)

						mouse_distance = pointsDistance(center, mouse)
						if mouse_distance<radius:
							distances.append( (distance, obj_index, point_index) )
			except:
				pass

		if len(distances)>0:
			distances = sorted(distances, key=lambda x: x[0])
			obj_index   = distances[0][1]
			point_index = distances[0][2]
			points = list(eval(rows[obj_index][1]))

			points.insert( point_index + 1, mouse )
			self._polygons.set_value( 1, obj_index, str(points)[1:-1])

			self._selected_poly  = obj_index
			self._selected_point = point_index + 1

			if not self._player.is_playing: self._player.refresh()
			
	
	def on_player_click_in_video_window(self, event, x, y):
		self._selected_poly  = None
		self._selected_point = None

		if not self._square.checked and not self._circle.checked:
			self.selectPoint( int(x), int(y) )
		
		
	def on_player_drag_in_video_window(self, startPoint, endPoint):
		self._start_point = ( int(startPoint[0]), int(startPoint[1]) )
		self._end_point   = ( int(endPoint[0]), int(endPoint[1]) )
		
		if self._selected_poly!=None and self._selected_point!=None:
			poly = self._polygons.get_value( 1, self._selected_poly )
			try:
				points = list(eval(poly))
				points[self._selected_point] = self._end_point
				self._polygons.set_value( 1, self._selected_poly, str(points)[1:-1])
			except Exception as e:
				print(e)

		if not self._player.is_playing: self._player.refresh() 
			
	def on_player_end_drag_in_video_window(self, startPoint, endPoint):
		self._start_point = int(startPoint[0]), int(startPoint[1])
		self._end_point   = int(endPoint[0]),   int(endPoint[1])
		
		
		points = None
		if self._square.checked:
			points = createRectanglePoints(self._start_point, self._end_point)
		elif self._circle.checked and self._end_point[0]>self._start_point[0] and self._end_point[1]>self._start_point[1]:
			points = createEllipsePoints(self._start_point, self._end_point)

		if points: self._polygons += ["Poly_%d" % self._polygons.rows_count, str(points)[1:-1]]

		self._start_point 	 = None
		self._end_point 	 = None
		self._square.checked = False
		self._circle.checked = False

		if not self._player.is_playing: self._player.refresh() 


	def __add_contours_from_threshold_win(self, contours):
		for contour in contours:
			if contour.any(): 
				points = [tuple(p[0]) for p in contour.tolist()]
				self._polygons += ["Poly_%d" % self._polygons.rows_count, str(points)[1:-1]]

	def videoSelected(self): self._player.value = self._video.value
		
	def square_toggle(self, checked):
		if checked: self._circle.checked = False

	def circle_toggle(self, checked):
		if checked: self._square.checked = False

	def threshold_btn_click(self):
		if self._threshold_win is None:
			self._threshold_win = GeometryFromThreshold(self)
			self._threshold_win.add_contours = self.__add_contours_from_threshold_win
		
		self._threshold_win.show()
		if len(self._video.value)>0: self._threshold_win._filename.value = self._video.value




	def remove_clicked(self):
		self._polygons -= -1 #Remove the selected row
		if not self._player.is_playing: self._player.refresh() 

	@property
	def geometries(self):
		polys = []
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):		
			points = eval(obj[1])
			polys.append( [obj[0], points] )
		return polys

	@geometries.setter
	def geometries(self, value):
		self._polygons.value = []

		for name, poly in value:	
			points = [tuple(p) for p in poly]
			self._polygons += [name, str(points)[1:-1]]


		







	@property
	def polygons(self):
		polys = []
		rows = self._polygons.value
		for objIndex, obj in enumerate(rows):		
			points = eval(obj[1])
			polys.append( np.array(points,np.int32) )
		return np.array(polys)
	

	@property
	def apply_event(self): return self._apply.value
	@apply_event.setter
	def apply_event(self, value): 
		self._apply.value = value
		self._show_apply = value is not None
		

	def show(self):
		super(GeometryManualDesigner, self).show()
		if hasattr(self,'_show_apply') and self._show_apply: self._apply.show()

	@property
	def video_filename(self): return None
	@video_filename.setter
	def video_filename(self, value): 
		self._video.hide()
		self._player.value = value

	@property
	def video_capture(self): return self.video_capture.value
	@video_capture.setter
	def video_capture(self, value): 
		self._video.hide()
		self._player.value = value

	@property
	def total_n_frames(self): 
		if self._player._value is not None and self._player.value!='':
			return self._player.max
		else:
			return 0

	