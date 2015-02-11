import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
Rectangle 
{
    id:base
    width: 250
    height: 500
    color:"white"
    property int objectsMargin:10
    ColumnLayout
    {
        anchors.fill: parent;
        anchors.leftMargin:2
        Text
        {
            id:introText
            text: "<b>Hardware setup</b><br>Choose a hardware setup. We recommend choosing 'basic setup' if this is your first time using Argus."
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }
        Rectangle 
        {
            id:spacer
            width: 246
            color:"black"
            height: 2
            anchors.topMargin:objectsMargin
            anchors.top:introText.bottom
        }
        Image
        {
            id:scanImage
            anchors.topMargin:objectsMargin
            anchors.top: spacer.bottom
            source:"placeholder.png";
        }
        
        ExclusiveGroup { id: setupType }
        ColumnLayout
        {
            id: setupSelection
            anchors.top: scanImage.bottom
            anchors.topMargin:objectsMargin
            RadioButton 
            {
                text: "Basic setup"
                checked: true
                exclusiveGroup: setupType
            }
            RadioButton 
            {
                text: "Same as last time"
                exclusiveGroup: setupType
            }
            RadioButton 
            {
                text: "Custom / free setup"
                exclusiveGroup: setupType
            }
        }
        Rectangle 
        {
            id:spacer2
            width: 246
            color:"black"
            height: 2
            anchors.topMargin:objectsMargin
            anchors.top:setupSelection.bottom
        }
        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(2);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
