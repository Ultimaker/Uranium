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
        }
    }
    Component
    {
        id: categoryDelegate
       
        Button
        {
            id:categoryDelegateButton
            property bool on: false
            property int border_thickness: 0  //Stupid hack as propertychanges won't let me change it.
            function toggle() 
            {
                if(on)
                {
                    border_thickness = 0;
                    on = !on;
                } else {
                    border_thickness = 1;
                    on = !on;
                }
            }

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
                        spacing:4
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
                    id:categoryDelegateButtonBackground
                    implicitWidth: 240
                    implicitHeight: 50
                    color:"transparent"
                    radius:3
                    border.width:border_thickness
                }
            }
            onClicked: {
                settingsList.model.toggleCollapsedByCategory(section); 
                toggle();
            }
        }
    }
    
    SettingsVisibilityWindow 
    {
        id: settingDialog
    }
}