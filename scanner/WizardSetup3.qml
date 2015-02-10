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
            text: "<b>Position calibration board</b> <br> The calibration board needs to be placed in<br> the centre of the camera view. Make sure that <br>sufficient markers are visible. Ensure that<br> ~80% of the image is filled up with the <br>calibration board."
        }
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            anchors.top: spacer.bottom
            source:"placeholder.png";
        }
        Image
        {
            id:placeholder2

            source:"placeholder.png";
        }
        

        
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(4);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
