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

        border.color: UM.Theme.getColor("lining")
        color: UM.Theme.getColor(parent.hovered ? "secondary" : "main_background")
    }
}