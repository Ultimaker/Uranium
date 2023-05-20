// Copyright (c) 2023 Ultimaker
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import UM 1.5 as UM

MouseArea
{
    id: base

    hoverEnabled: true

    property color color: "black"
    property color hoverColor: color
    property color backgroundColor: "transparent"
    property color hoverBackgroundColor: backgroundColor
    property alias iconSource: image.source
    property real iconMargin: 0

    property alias hovered: base.containsMouse
    property alias backgroundRadius: background.radius

    Rectangle
    {
        id: background
        anchors.fill: parent
        color: base.containsMouse ? base.hoverBackgroundColor : base.backgroundColor
        radius: 0
    }

    UM.ColorImage
    {
        id: image

        anchors.fill: parent
        anchors.margins: base.iconMargin

        color: base.containsMouse ? base.hoverColor : base.color

        visible: source != ""
    }
}
