from . import PointCloudAlignTool
from . import PointCloudAlignView
from . import PointCloudAlignExtension


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
            'view_panel': 'PointCloudAlignView.qml',
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
    
    #extension.setPluginId("PointCloudAlignment")
    #view = 
    #view.setPluginId("PointCloudAlignment")     
    #Application.getInstance().getController().addView(view)
    plugin_dict = {}
    plugin_dict["view"] = PointCloudAlignView.PointCloudAlignView()
    plugin_dict["extension"] = PointCloudAlignExtension.PointCloudAlignExtension()
    plugin_dict["tool"] = PointCloudAlignTool.PointCloudAlignTool()
    return plugin_dict
