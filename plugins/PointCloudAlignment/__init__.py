from . import PointCloudAlignTool
from . import PointCloudAlignView
from UM.Application import Application
def getMetaData():
    return {
        'type': 'tool',
        'plugin': 
        {
            "name": "PointCloudAlignment",
            'author': 'Jaime van Kessel',
            'version': '1.0',
            'description': ''
        },
        'view': 
        {
            'name': 'PointCloudAlignmentView',
            'visible': False
        },
        'tool': 
        {
            'name': 'PointCloudAlignmentTool',
        },
        'cura': {
            'tool': {
                'visible': False
            }
        }
    }

def register(app):
    #TODO: Once multiple plugin types are supported, this needs to be removed.
    view = PointCloudAlignView.PointCloudAlignView()
    view.setPluginId("PointCloudAlignment")
    Application.getInstance().getController().addView(view)
    return PointCloudAlignTool.PointCloudAlignTool()
