import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import Cura 1.0 as Cura

Panel 
{
    anchors.right: parent.right;
    anchors.verticalCenter: parent.verticalCenter

    title: "Settings"

    contents: ColumnLayout 
    {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400

        Rectangle 
        {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ListView
            {
                model: Cura.Models.settingsModel
                anchors.fill: parent
                delegate: settingDelegate
                section.property: "category"
                section.delegate:categoryDelegate
                
            }

            color: "blue"
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
        onClicked: settingDialog.visible = true
    }
    
    Component 
    {
        id: settingDelegate
        Item 
        {
            width: 180; height: 40
            Column {
                Text { text: '<b>Name:</b> ' + name }
            }
        }
    }
    Component
    {
        id: categoryDelegate
        Rectangle { color: "red"; width: 150; height: 20 }
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