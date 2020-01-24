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

        // The progress block for showing progress value
        Rectangle
        {
            id: progressBlockDeterminate
            x: progressBar.indeterminate ? progressBar.visualPosition * parent.width : 0
            width: progressBar.indeterminate ? parent.width * 0.1 : progressBar.visualPosition * parent.width
            height: parent.height
            radius: UM.Theme.getSize("progressbar_radius").width
            color: UM.Theme.getColor("progressbar_control")
        }
        SequentialAnimation
        {
            PropertyAnimation
            {
                target: progressBar
                property: "value"
                from: 0
                to: 0.9 // The block is not centered, so let it go to 90% (since it's 10% long)
                duration: 3000
            }
            PropertyAnimation
            {
                target: progressBar
                property: "value"
                from: 0.9 // The block is not centered, so let it go to 90% (since it's 10% long)
                to: 0
                duration: 3000
            }

            loops: Animation.Infinite
            running: progressBar.visible && progressBar.indeterminate
        }
    }
}
