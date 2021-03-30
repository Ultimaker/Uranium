// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import UM 1.2 as UM

/*
 * Wrapper around TabButton to use our theming and sane defaults.
 */
TabButton
{
    anchors.top: parent.top
    height: parent.height
    checked: model.index == 0 //First button is checked by default.

    background: Rectangle
    {
        radius: UM.Theme.getSize("default_radius").width
        border.color: UM.Theme.getColor("lining")
        border.width: UM.Theme.getSize("default_lining").width
        color: UM.Theme.getColor(parent.checked ? "main_background" : (parent.hovered ? "action_button_hovered" : "secondary"))

        //Make the lining go straight down on the bottom side of the left and right sides.
        Rectangle
        {
            anchors.bottom: parent.bottom
            width: parent.width
            //We take almost the entire height of the tab button, since this "manual" lining has no anti-aliasing.
            //We can hardly prevent anti-aliasing on the border of the tab since the tabs are positioned with some spacing that is not necessarily a multiple of the number of tabs.
            height: parent.height - (parent.radius + parent.border.width)
            color: parent.border.color

            //Don't add lining at the bottom side.
            Rectangle
            {
                anchors
                {
                    bottom: parent.bottom
                    bottomMargin: parent.parent.parent.checked ? 0 : parent.parent.border.width //Allow margin if tab is not selected.
                    left: parent.left
                    leftMargin: parent.parent.border.width
                    right: parent.right
                    rightMargin: parent.parent.border.width
                }
                color: parent.parent.color
                height: parent.height - anchors.bottomMargin
            }
        }
    }
    contentItem: Label
    {
        anchors.centerIn: parent
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        text: parent.text
        font: parent.checked ? UM.Theme.getFont("default_bold") : UM.Theme.getFont("default")
        color: UM.Theme.getColor("text")
        renderType: Text.NativeRendering
    }
}
