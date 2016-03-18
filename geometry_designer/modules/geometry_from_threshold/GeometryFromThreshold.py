from pyforms.Controls import ControlText
from pyforms.Controls import ControlProgress
from pyforms.Controls import ControlSlider
from pyforms.Controls import ControlCombo
from pyforms.Controls import ControlButton
from pyforms.Controls import ControlPlayer
from pyforms.Controls import ControlList
from pyforms.Controls import ControlFile
from pyforms 		  import BaseWidget
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
		super(GeometryFromThreshold, self).__init__('Find geometry using a threshold on the image', parentWindow=parent)
		
		self._filename 		= ControlFile('Video file name')
		self._player   		= ControlPlayer('Player')
		self._threshold 	= ControlSlider('Movement threshold', 10, 0, 255)
		self._epsilon 		= ControlSlider('Epsilon', 10, 1, 255)
		self._add_contour   = ControlButton('add contour')


		self._formset = [ '_filename', 
			('_threshold', '_epsilon','_add_contour'),
			'_player']

		self._filename.changed 		= self.__filename_changed
		self._player.processFrame 	= self.__processFrame
		self._threshold.changed 	= self._player.refresh
		self._epsilon.changed 		= self._player.refresh
		self._add_contour.value		= self.__add_contour

		self._filename.value = '/home/ricardo/bitbucket/single-fly-tracker/Circle_and_Square.avi'

		self._contour = []
		

	def __add_contour(self): self.add_contour(self._contour)

	def add_contour(self, contour): pass


	def __filename_changed(self): self._player.value = self._filename.value


	
	def __processFrame(self, frame): 
		_, threshold = cv2.threshold(frame, self._threshold.value, 255, 0)

		gray    = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)
		contour = getBiggestContour(gray)

		threshold[:,:,0] = 0
		threshold[:,:,1] = 0
		dst = cv2.addWeighted(frame,0.7,threshold,0.3,0)

		self._contour = contour = cv2.approxPolyDP(contour,self._epsilon.value,True)

		cv2.polylines(dst, contour, True, (0,255,0), 11 )
		cv2.polylines(dst, np.array([contour]), True, (0,255,0), 1 )
		return dst



if __name__ == "__main__":  pyforms.startApp( GeometryFromThreshold )