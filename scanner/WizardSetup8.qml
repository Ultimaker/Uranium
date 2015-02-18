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
            text: "<b>Object Characteristics</b><br>Choose an object setting that best matches the object that you're about to scan.."
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            source:"placeholder.png";
        }
        
        ExclusiveGroup { id: objectType }
        ColumnLayout
        {
            id: objectTypeSelection
            RadioButton 
            {
                text: "Simple / smooth"
                checked: true
                exclusiveGroup: objectType
            }
            RadioButton 
            {
                text: "Detailed"
                exclusiveGroup: objectType
            }
            RadioButton 
            {
                text: "Dificult object"
                exclusiveGroup: objectType
            }
        }
        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(9);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
