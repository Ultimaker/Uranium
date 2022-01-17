// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.15
import QtQuick.Controls 2.15
import UM 1.4 as UM

//Scroll bar that uses our own theme.
ScrollBar
{
    background: Rectangle
    {
        implicitWidth: UM.Theme.getSize("scrollbar").width

        radius: implicitWidth / 2
        color: UM.Theme.getColor("scrollbar_background")
    }

    contentItem: Rectangle
    {
        implicitWidth: UM.Theme.getSize("scrollbar").width

        radius: implicitWidth / 2
        color: parent.pressed ? UM.Theme.getColor("scrollbar_handle_down") : parent.hovered ? UM.Theme.getColor("scrollbar_handle_hover") : UM.Theme.getColor("scrollbar_handle")
        Behavior on color { ColorAnimation { duration: 50; } }
    }
}