// Copyright (c) 2019 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3 as Controls

import UM 1.3 as UM

//
// Styled progress bar, with colours from the theme and rounded corners.
//
Controls.ProgressBar
{
    id: progressBar
    width: parent.width
    height: UM.Theme.getSize("progressbar").height

    background: Rectangle
    {
        anchors.fill: parent
        radius: UM.Theme.getSize("progressbar_radius").width
        color: UM.Theme.getColor("progressbar_background")
    }

    contentItem: Item
    {
        anchors.fill: parent

        Rectangle
        {
            width: progressBar.visualPosition * parent.width
            height: parent.height
            radius: UM.Theme.getSize("progressbar_radius").width
            color: UM.Theme.getColor("progressbar_control")
        }
    }
}
