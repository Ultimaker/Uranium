import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Item
{
    width: 250
    height: 250
    Button 
    { 
        text: "Stitch"
        anchors.right : parent.right
        onClicked:UM.ActiveView.triggerAction("test", value)
    }
}