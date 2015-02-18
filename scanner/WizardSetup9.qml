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
            text: "<b>Object Shade</b><br>Choose an object setting that best matches the object that you're about to scan.."
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            source:"placeholder.png";
        }
        
        ExclusiveGroup { id: objectShadeType }
        ColumnLayout
        {
            id: objectTypeSelection
            RadioButton 
            {
                text: "Light"
                checked: true
                exclusiveGroup: objectShadeType
            }
            RadioButton 
            {
                text: "Medium"
                exclusiveGroup: objectShadeType
            }
            RadioButton 
            {
                text: "Dark"
                exclusiveGroup: objectShadeType
            }
        }
        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(10);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
