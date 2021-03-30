// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1

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

    Rectangle
    {
        id: background
        anchors.fill: parent
        color: base.containsMouse ? base.hoverBackgroundColor : base.backgroundColor
    }

    RecolorImage
    {
        id: image

        anchors.fill: parent
        anchors.margins: base.iconMargin
        sourceSize.height: width

        color: base.containsMouse ? base.hoverColor : base.color

        visible: source != ""
    }
}
