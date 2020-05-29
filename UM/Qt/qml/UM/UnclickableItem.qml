// Copyright (c) 2020 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7

// Item with a MouseArea to consume unwanted clicks and scroll wheels.
Item
{
    MouseArea
    {
       acceptedButtons: Qt.AllButtons
       onClicked: parent.onClicked ? parent.onClicked() : {}
       onWheel: parent.onWheel ? parent.onWheel() : {}
       anchors.fill: parent
    }
}