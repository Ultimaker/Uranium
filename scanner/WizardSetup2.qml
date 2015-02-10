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
            text: "<b>Hardware setup</b> <br> Choose a hardware setup. We recommend <br> choosing 'basic setup' if this is your first time <br>using Argus."
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
            id:introText2
            text: "Make sure all cables are attached well <br> and that everything is positioned in its slot"
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
                UM.ToolbarData.setState(3);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
