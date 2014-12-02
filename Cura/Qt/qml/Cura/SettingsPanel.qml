import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1
import Cura 1.0 as Cura

Panel 
{
    id: settingsPanel
    color:"#ebebeb"
    anchors.right: parent.right;
    anchors.verticalCenter: parent.verticalCenter
    //background:Rectangle {color:}
    contents: ColumnLayout 
    {
        
        Layout.preferredWidth: 250
        Layout.preferredHeight: 500
        Rectangle
        {
            id: settingPanelTitleBar
            Layout.fillWidth:true
            height:25
            gradient: Gradient 
            {
                GradientStop { position: 0 ; color: "#646464"}
                GradientStop { position: 1 ; color: "#353535" }
            }
            Label 
            {
                text: "Settings" 
                anchors.centerIn: parent
                color: "white"
            }
        }
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
                    Text 
                    {
                        id:saveButtonText
                        text: "Save"
                        font.pointSize: 20
                        color:"#404040"
                        verticalAlignment: Text.AlignVCenter
                        anchors.centerIn: parent
                    }
                    Image
                    {
                        id:saveButtonIcon
                        anchors.left: saveButtonText.right
                        source:"../../../Resources/save_button.png"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin:5
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
            
            onLoaded: {
                item.model = settingsList.model;
                item.key = model.key
//                 item.valid = parseInt(model.valid); 
//                 item.value = model.value
                item.index = parseInt(index);
            }
         
            Binding { target: item; property: "valid"; value: model.valid; }
            Binding { target: item; property: "value"; value: model.value; }
        }
    }
    Component
    {
        id: categoryDelegate
       
        Button
        {
            text:section; 
            onClicked: settingsList.model.toggleCollapsedByCategory(section)
        }
    }
    
    Window {
        id: settingDialog
        title: "Setting configuration"
        
        flags: Qt.Dialog
        width:250
        height:250
        
        Rectangle 
        { 
            color: "red";
            width: 150;
            height: 100 
            
        }
        Button
        { 
            onClicked:settingDialog.visible = false
            text: "Close" 
            anchors.bottom:parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}