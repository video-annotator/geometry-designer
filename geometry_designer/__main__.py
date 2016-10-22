import pyforms
from geometry_designer.modules.geometry_manual_designer.GeometryManualDesigner import GeometryManualDesigner


class GeometryDesigner(GeometryManualDesigner):
    """Application form"""

    def __init__(self):
    	super(GeometryDesigner, self).__init__('Geometry designer')

    	#self._video.value = '/home/ricardo/bitbucket/single-fly-tracker/Circle_and_Square.avi'


    	
		



##################################################################################################################
##################################################################################################################
##################################################################################################################

if __name__ == "__main__":  pyforms.startApp( GeometryDesigner )