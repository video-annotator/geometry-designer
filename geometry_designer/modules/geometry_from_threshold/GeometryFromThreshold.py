from pyforms.controls import ControlText
from pyforms.controls import ControlProgress
from pyforms.controls import ControlSlider
from pyforms.controls import ControlCombo
from pyforms.controls import ControlButton
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlList
from pyforms.controls import ControlFile
from pyforms.basewidget import BaseWidget
import cv2, numpy as np, pyforms


def biggestContour(contours, howmany=1):
	biggest = []
	for blob in contours:
		area = cv2.contourArea(blob)
		biggest.append( (area, blob) )
	if len(biggest)==0: return None
	biggest = sorted( biggest, key=lambda x: -x[0])
	if howmany==1: return biggest[0][1]
	return [x[1] for x in biggest[:howmany] ]

def getBiggestContour(image, howmany=1):
	(_, blobs, dummy) = cv2.findContours( image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
	return biggestContour(blobs, howmany)







class GeometryFromThreshold(BaseWidget):
	
	def __init__(self, parent=None):
		super(GeometryFromThreshold, self).__init__('Find geometry using a threshold on the image', parent_win=parent)
		
		self._filename 		= ControlFile('Video file name')
		self._player   		= ControlPlayer('Player')
		self._threshold 	= ControlSlider('Movement threshold', default=10, minimum=0, maximum=255)
		self._epsilon 		= ControlSlider('Epsilon', default=10, minimum=1, maximum=255)
		self._add_contour   = ControlButton('add contour')


		self._formset = [ '_filename', 
			('_threshold', '_epsilon','_add_contour'),
			'_player']

		self._filename.changed_event 	= self.__filename_changed
		self._player.process_frame_event 		= self.__processFrame
		self._threshold.changed_event 	= self._player.refresh
		self._epsilon.changed_event 	= self._player.refresh
		self._add_contour.value			= self.__add_contours

		self._filename.value = '/home/ricardo/bitbucket/single-fly-tracker/Circle_and_Square.avi'

		self._contours = []
		

	def __add_contours(self): self.add_contours(self._contours)

	def add_contours(self, contours): pass


	def __filename_changed(self): self._player.value = self._filename.value


	
	def __processFrame(self, frame): 
		_, threshold = cv2.threshold(frame, self._threshold.value, 255, 0)

		gray    = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)
		_, blobs, dummy = cv2.findContours( gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )


		threshold[:,:,0] = 0
		threshold[:,:,1] = 0
		dst = cv2.addWeighted(frame,0.7,threshold,0.3,0)

		self._contours = []
		for contour in blobs:
			contour = cv2.approxPolyDP(contour,self._epsilon.value,True)
			self._contours.append(contour)
			cv2.polylines(dst, contour, True, (0,255,0), 11 )
			cv2.polylines(dst, np.array([contour]), True, (0,255,0), 1 )
		return dst



if __name__ == "__main__":  pyforms.startApp( GeometryFromThreshold )