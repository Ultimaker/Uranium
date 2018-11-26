// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.0
import QtQuick.Controls 2.0
import UM 1.2 as UM

/*
 * Wrapper around TabButton to use our theming and sane defaults.
 */
TabButton
{
    height: parent.height

    background: Rectangle
    {
        width: parent.width
        height: parent.height

        radius: UM.Theme.getSize("default_radius").width
        border.color: UM.Theme.getColor("lining")
        border.width: UM.Theme.getSize("default_lining").width
        color: UM.Theme.getColor(parent.hovered ? "secondary" : "main_background")

        //Make the lining go straight down on the bottom side of the left and right sides.
        Rectangle
        {
            anchors
            {
                bottom: parent.bottom
                left: parent.left
                right: parent.right
            }
            height: parent.radius + parent.border.width
            color: parent.border.color

            //Don't add lining at the bottom side.
            Rectangle
            {
                anchors
                {
                    bottom: parent.bottom
                    left: parent.left
                    leftMargin: parent.parent.border.width
                    right: parent.right
                    rightMargin: parent.parent.border.width
                }
                color: parent.parent.color
                height: parent.parent.radius + parent.parent.border.width
            }
        }
    }
}