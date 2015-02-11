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
            text: "<b>Focus Beamer</b> <br> Move the focus slide of the projector so that<br> the image is sharply projected on the <br>calibration board. "
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            source:"placeholder.png";
        }
        
        Label 
        {
            text: "When image is in foucs like the image above, <br>you can continue to the next step."
            
        }
        

        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(5);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
