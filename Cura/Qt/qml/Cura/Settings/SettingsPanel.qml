import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import Cura 1.0 as Cura

import ".."

Panel 
{
    id: settingsPanel
    color:"#ebebeb"
    title: "Settings";

    signal settingConfigurationRequested;

    contents: ColumnLayout 
    {
        
        Layout.preferredWidth: 250
        Layout.preferredHeight: 500

        Rectangle
        {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: settingsPanel.color
            ScrollView 
            {
                anchors.fill: parent
                ListView
                {
                    id:settingsList
                    model: Cura.Models.settingsModel
                    delegate: settingDelegate
                    section.property: "category"
                    section.delegate: categoryDelegate
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                }
            }
        }
        Button 
        {
            Layout.fillWidth: true
            //text: "Save"
            onClicked: settingsList.model.saveSettingValues()
            style: ButtonStyle 
            { 
                label: Rectangle
                {  
                    Layout.fillWidth: true
                    color: "transparent"
                    anchors.centerIn: parent
                    Row
                    {
                        anchors.centerIn: parent;
                        width: childrenRect.width;
                        height: childrenRect.height;
                        spacing:4
                        Text 
                        {
                            id:saveButtonText
                            text: "Save"
                            font.pointSize: 20
                            color:"#404040"
                        }
                        Image
                        {
                            id:saveButtonIcon

                            source:"../../../Resources/save_button.png"
                        }
                    }
                }
                background: Rectangle 
                {
                    implicitWidth: 100
                    implicitHeight: 50
                    border.width: 1
                    border.color: "#404040"
                    gradient: Gradient 
                    {
                        GradientStop 
                        { 
                            position: 0 ; 
                            color: control.pressed ? "#B2B2B2" : "#A1A1A1" 
                        }
                        GradientStop 
                        { 
                            position: 1 ; 
                            color: control.pressed ? "#B2B2B2" : "#B2B2B2" 
                        }
                    }
                }
            }
            
        }
    }

    Component 
    {
        id: settingDelegate  

        Loader
        {
            opacity: (model.visibility && !model.collapsed) ? 1 : 0
            Behavior on opacity { NumberAnimation { } }
            height: (model.visibility && !model.collapsed) ? 30 : 0
            Behavior on height { NumberAnimation { } }

            source:
            {
                switch(model.type)
                {
                    case "int":
                        return "SettingTextField.qml"
                    case "float":
                        return "SettingTextField.qml"
                }
            }

            onLoaded:
            {
                item.model = settingsList.model;
                item.key = model.key
                item.index = parseInt(index);
            }

            Binding { target: item; property: "valid"; value: model.valid; }
            Binding { target: item; property: "value"; value: model.value; }

            MouseArea
            {
                anchors.fill: parent;
                acceptedButtons: Qt.RightButton;
                onClicked: contextMenu.popup();
            }

            Menu
            {
                id: contextMenu;

                MenuItem { text: "Hide this setting"; onTriggered: settingsList.model.setVisibility(model.key, false); }
                MenuItem { text: "Configure setting visiblity..."; onTriggered: settingsPanel.settingConfigurationRequested(); }
            }

        }
    }
    Component
    {
        id: categoryDelegate
       
        Button
        {
            style: ButtonStyle 
            {
                
                label: Rectangle
                {  
                    Layout.fillWidth: true
                    color: "transparent"
                    anchors.centerIn: parent
                    Row
                    {
                        anchors.centerIn: parent;
                        width: parent.width;
                        height: childrenRect.height;
                        spacing: 4
                        Image
                        {

                            source:"../../../Resources/icon_resolution.png"
                        }
                        Text 
                        {
                            text: section
                            color:"#404040"
                        }
                        
                    }
                }
                background: Rectangle 
                {
                    implicitWidth: 100
                    implicitHeight: 50
                    color:"transparent"
                }
            }
            onClicked: settingsList.model.toggleCollapsedByCategory(section)
        }
    }
}
