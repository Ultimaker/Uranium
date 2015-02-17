import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Panel {
    title: "Layers"
    contents: ColumnLayout 
    {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400

        ListView
        {
            Layout.fillWidth: true
            Layout.fillHeight: true
            id:meshList
            //headerVisible: false
            //TableViewColumn{ role: "name" ; title: "Name" ; width: 200 }
            delegate: meshDelegate      
            model: UM.Models.meshListModel
        }

    }
    Component 
    {
        id: meshDelegate
        Rectangle 
        {
            color: model.depth == 1 ?"#FFFFFF": "#EBEBEB" 
            width:meshList.width
            Behavior on opacity { NumberAnimation { } }
            opacity:model.collapsed ? 0:1
            
            Behavior on height {NumberAnimation{}}
            height:model.collapsed ? 0:25
            MouseArea
            {
                anchors.fill: parent;
                acceptedButtons: Qt.LeftButton 
                onClicked: meshList.model.setSelected(model.key)
            }
            MouseArea
            {
                anchors.fill: parent;
                acceptedButtons: Qt.RightButton;
                onClicked: contextMenu.popup();
            }

            Menu
            {
                id: contextMenu;

                MenuItem { text: "Delete"; onTriggered: meshList.model.removeMesh(model.key); }
                MenuItem { text: "Save"; onTriggered: {fileDialog.key = model.key;
                                                        fileDialog.open();} }
            }
            
            RowLayout 
            {
                anchors.fill: parent
                //Layout.fillWidth:true
                
                ToggleButton
                { 
                    onClicked:meshList.model.setVisibility(model.key,checked)
                    checkedImage:  UM.Resources.getIcon("icon_visibility.png")
                    uncheckedImage: UM.Resources.getIcon("icon_visibility_crossed.png")
                    width:22
                }
 
                ToggleButton
                {
                    id:collapseButton
                    checkedImage: UM.Resources.getIcon("icon_collapse_up.png")
                    uncheckedImage:UM.Resources.getIcon("icon_collapse_down.png")
                    visible: model.depth == 1 ? true: false
                    onClicked:meshList.model.setCollapsed(model.key)
                }
                Text 
                {
                    text:model.name
                    width:50
                }

                ToggleButton
                {
                    id: lockButton
                    checkedImage: UM.Resources.getIcon("icon_lock_open.png")
                    uncheckedImage: UM.Resources.getIcon("icon_lock_closed.png")   
                    anchors.right:selectIcon.left
                } 
                ToggleButton
                {
                    id:selectIcon
                    checkedImage: UM.Resources.getIcon("icon_selected_open.png")
                    uncheckedImage:UM.Resources.getIcon("icon_selected_closed.png")
                    anchors.right:parent.right
                }
            }
        }
    }
    
    FileDialog {
        id: fileDialog
        property variant key;

        title: "Save"
        modality: Qt.NonModal
        selectMultiple: false
        selectExisting:false

        onAccepted: 
        {
            meshList.model.saveMesh(key,fileUrl)
        }
    }
}
