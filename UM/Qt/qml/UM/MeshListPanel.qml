import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Rectangle {
    id:meshListPanel
    width:250
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
                //width:parent.width - meshListPanel.border.width * 4
                anchors.left:parent.left
                anchors.leftMargin:1
                anchors.top:parent.top
                anchors.topMargin:1
                Layout.fillHeight: true
                Layout.fillWidth: true
                id:meshList
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
                    width:parent.width - meshListPanel.border.width * 4
                    height:parent.height - meshListPanel.border.width * 2
                    anchors.horizontalCenter:parent.horizontalCenter
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
            id:background
            color: model.depth == 1 ?"#FFFFFF": "#EBEBEB" 
            width:meshList.width -2
            Behavior on opacity { NumberAnimation { } }
            opacity: model.has_children? 1: model.collapsed ? 0:1
            
            Behavior on height {NumberAnimation{}}
            height:model.has_children ? 25: model.collapsed? 0:25
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
                anchors.fill:parent
                
                ToggleButton
                { 
                    id:visibilityButton
                    onClicked:meshList.model.setVisibility(model.key,checked)
                    checkedImage:  UM.Resources.getIcon("icon_visibility.png")
                    uncheckedImage: UM.Resources.getIcon("icon_visibility_crossed.png")
                    checked:model.visibility
                    width:22
                }
 
                ToggleButton
                {
                    id:collapseButton
                    checkedImage: UM.Resources.getIcon("icon_collapse_up.png")
                    uncheckedImage:UM.Resources.getIcon("icon_collapse_down.png")
                    visible: model.depth != 1 ? false: model.has_children ? true:false
                    checked:model.collapsed
                    onClicked:meshList.model.setCollapsed(model.key)
                }
                TextField
                {
                    property bool editingName: false
                    text:model.name
                    Layout.maximumWidth: 100
                    Layout.minimumWidth:100
                    anchors.horizontalCenter:parent.horizontalCenter
                    onEditingFinished:{editingName = false; meshList.model.setName(model.key,text)}
                    id: nameTextField
                    readOnly:!nameTextField.editingName
                    
                    style: TextFieldStyle
                    {
                        background: Rectangle 
                        {
                            color: nameTextField.editingName ?  "white":"transparent"
                            radius:2
                            border.color:nameTextField.editingName ?"black": "transparent"
                            anchors.fill:parent
                        }
                    }
                    MouseArea
                    {
                        anchors.fill: parent;
                        anchors.horizontalCenter: parent.horizontalCenter; 
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: {nameTextField.editingName = true; console.log("Starting edit")}
                        enabled:!nameTextField.editingName
                    }
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
