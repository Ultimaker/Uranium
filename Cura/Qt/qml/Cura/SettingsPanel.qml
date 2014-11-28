import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import Cura 1.0 as Cura

Panel 
{
    anchors.right: parent.right;
    anchors.verticalCenter: parent.verticalCenter


    contents: ColumnLayout 
    {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400
        Rectangle
        {
            Layout.fillWidth:true
            height:25
            color:"black"
            Label {
                text: "Settings" 
                anchors.centerIn: parent
                color: "white"
            }
        }
        Rectangle 
        {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ScrollView {
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
//             ScrollBar {
//                 flickable: settingsList
//             }
        }

        Button 
        {
            Layout.fillWidth: true
            text: "Save"
        }
    }
    Button
    {
        text:"s"
        width: 20
        height: 20
        y:2
        x:2
        onClicked: settingDialog.visible = true
    }
    
    Component 
    {
        id: settingDelegate
        
        
        Loader
        {
            source: {
                switch(model.type) {
                    case "int":
                        return "SettingTextField.qml"
                    case "float":
                        return "SettingTextField.qml" 
                }
            }
            
        }
    }
    Component
    {
        id: categoryDelegate
       
         Button{text:section; onClicked: settingsList.model.toggleCollapsedByCategory(section)}
    }
    
    Window {
        id: settingDialog
        title: "Setting configuration"
        
        flags: Qt.Dialog
        width:250
        height:250
        
        Rectangle { color: "red"; width: 150; height: 100 }
        Button
        { 
            onClicked:settingDialog.visible = false
            text: "Close" 
            anchors.bottom:parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}