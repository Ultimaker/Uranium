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

        // The progress block for showing determinate progress value
        Rectangle
        {
            id: progressBlockDeterminate
            width: progressBar.visualPosition * parent.width
            height: parent.height
            radius: UM.Theme.getSize("progressbar_radius").width
            color: UM.Theme.getColor("progressbar_control")
            visible: !progressBar.indeterminate
        }

        // The progress block for showing indeterminate progress value
        Rectangle
        {
            id: progressBlockIndeterminate
            x: progressBar.visualPosition * parent.width
            width: parent.width * 0.1
            height: parent.height
            radius: UM.Theme.getSize("progressbar_radius").width
            color: UM.Theme.getColor("progressbar_control")
            visible: progressBar.indeterminate
        }

        PropertyAnimation {
            target: progressBar
            property: "value"
            from: 0.2
            to: 0.8
            duration: 3000
            running: progressBar.indeterminate
            loops: Animation.Infinite
        }
    }
}
