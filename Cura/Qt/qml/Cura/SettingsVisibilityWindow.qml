import QtQuick 2.1
import QtQuick.Window 2.
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import Cura 1.0 as Cura

Window 
{
    id:settingsVisibilityWindow
    title: "Setting configuration"
    
    flags: Qt.Dialog
    width:250
    height:250
    
    ListView 
    {
        id:settingVisibilityList
        anchors.fill: parent;
        delegate: settingDelegate
        model: Cura.Models.settingsModel
        section.property: "category"
        section.delegate: categoryDelegate
    }
    
    Component
    {
        id: categoryDelegate
       
        Button
        {
            text:section; 
        }
    }
    
    Component
    {
        id: settingDelegate
        CheckBox
        {
            text:name;
            x: depth * 25
            checked: model.visibility
            onClicked: {settingVisibilityList.model.setVisibility(key,checked)}
            enabled: {!model.disabled}
        }
    }
    
    Button
    { 
        onClicked:settingDialog.visible = false
        text: "Close" 
        anchors.bottom:parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }
}