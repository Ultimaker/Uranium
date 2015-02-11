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
        Label
        {
            id:introText1
            text: "<b>Edit object</b> <br> Stitch the clouds."
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            anchors.top: spacer.bottom
            source:"placeholder.png";
        }
        Label
        {
           
            text: "Make sure you select two layers at a time."
        }
        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(11);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
