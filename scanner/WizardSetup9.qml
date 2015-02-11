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
            text: "<b>Scan object</b> <br> You're now scanning."
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            anchors.top: spacer.bottom
            source:"placeholder.png";
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
