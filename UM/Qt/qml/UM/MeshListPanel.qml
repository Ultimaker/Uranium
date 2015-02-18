import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Rectangle {
    id:meshListPanel
    width:200
    height:500
    border.width:1
    border.color:"black"
    Rectangle
    {
        id: dragHandle
        width: parent.width
        height: 16
        color: "white"
        radius: 0
        border.width: 1
        border.color: "#000000"
        anchors.top: parent.bottom
        Image
        {
            source:UM.Resources.getIcon("expand_small.png")
            anchors.horizontalCenter:parent.horizontalCenter
        }
        MouseArea 
        {
            id: mouseAreaDragHandle
    
            property int oldMouseY
    
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            width: parent.width
            height: parent.height
            hoverEnabled: true
    
            onPressed: 
            {
                oldMouseY = mouseY
            }
    
            onPositionChanged: 
            {
                if (pressed) 
                {
                    meshListPanel.height = meshListPanel.height + (mouseY - oldMouseY)
                    meshListPanel.height = meshListPanel.height > 250 ? meshListPanel.height : 250
                }
            }
        }
    }
    
    Item
    {
        id:mainContent
        anchors.fill:parent
        ColumnLayout 
        {
            anchors.fill:parent
            Layout.preferredHeight:400
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
            
            Item
            {
                Layout.fillWidth: true
                height: 50
                Rectangle 
                {
                    color:"black"
                    width:parent.width
                    height:2
                }
                RowLayout
                {
                    anchors.fill:parent
                    Label 
                    {
                        text:"0 layers of scans"
                    }
                    Button
                    {
                        iconSource: UM.Resources.getIcon("open.png")
                        style:ButtonStyle{ background:Item{}}
                    }
                    
                    Button
                    {
                        iconSource: UM.Resources.getIcon("icon_search.png")
                        style:ButtonStyle{background:Item{}}
                    }
                    
                    Button
                    {
                        iconSource: UM.Resources.getIcon("icon_trash_bin.png")
                        style:ButtonStyle{background:Item{}}
                        onClicked:
                        {
                            meshList.model.removeSelected()
                        }
                    }
                }
            }
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
                    checkedImage: UM.Resources.getIcon("icon_selected_closed.png")
                    uncheckedImage:UM.Resources.getIcon("icon_selected_open.png")
                    anchors.right:parent.right
                    checked: model.selected
                    onClicked: meshList.model.setSelected(model.key)
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
