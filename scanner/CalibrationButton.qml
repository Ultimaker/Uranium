import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Window 2.1
import UM 1.0 as UM
import QtQuick.Controls.Styles 1.1

Button
{
    id:base
    property bool active:true;
    property variant key;
    onClicked :
    {
        UM.ScannerEngineBackend.calibrationButtonPressed(key)
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
                width: childrenRect.width;
                height: childrenRect.height;
                spacing:4
                Text 
                {
                    text: base.text
                    font.pointSize: 10
                    color:base.active ? "#404040": "#AAAAAA"
                }
            }
        }
        
        background: Rectangle 
        {
            implicitWidth: 75
            implicitHeight: 75
            border.width: 1
            border.color: base.active ? "#404040": "#BBBBBB"
            gradient: Gradient  
            {
                GradientStop { position: 0; color: base.active ? "#A1A1A1" : "#BBBBBB" }
                GradientStop { position: 1; color: base.active ? "#B2B2B2" : "#BBBBBB"}
            }
            radius: width * 0.5
        }
    }
}