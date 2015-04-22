from UM.Extension import Extension
from PyQt5.QtCore import QObject, QUrl, Qt, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtQuick import QQuickView
from UM.Qt.ListModel import ListModel
from UM.Application import Application
from UM.Scene.Camera import Camera

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog('plugins')


class PointCloudAlignExtension(QObject, Extension):
    NameRole = Qt.UserRole + 1
    NodeRole = Qt.UserRole + 2
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.addMenuItem(i18n_catalog.i18n("Align clouds"), self.openMergeCloudsInterface)
        self._cloud_list_model = None
        self._selectable_nodes = []
    
    cloudListChanged = pyqtSignal()    
    
    def openMergeCloudsInterface(self):
        self._select_clouds_view = QQuickView()
        self._select_clouds_view.engine().rootContext().setContextProperty('manager',self)
        self._select_clouds_view.setSource(QUrl("plugins/PointCloudAlignment/SelectClouds.qml"))
        self._select_clouds_view.show()
    
    @pyqtSlot(int,int)
    def startAlignProcess(self, index1, index2):
        self._select_clouds_view.hide()
        Application.getInstance().getController().setActiveTool("PointCloudAlignment")
        Application.getInstance().getController().getActiveTool().setAlignmentNodes(self._selectable_nodes[index1],self._selectable_nodes[index2])
        #node1 = self._selectable_nodes[index1]
        #print(self._selectable_nodes[index1])
        #print(self._selectable_nodes[index2])
    
    @pyqtProperty(QObject, notify = cloudListChanged)
    def cloudList(self):
        if not self._cloud_list_model:
            self._cloud_list_model = ListModel()
            self._cloud_list_model.addRoleName(self.NameRole, "text")
            
            for group_node in Application.getInstance().getController().getScene().getRoot().getChildren():
                if type(group_node) is not Camera:
                    self._cloud_list_model.appendItem({"text":group_node.getName()})
                    self._selectable_nodes.append(group_node)
        return self._cloud_list_model