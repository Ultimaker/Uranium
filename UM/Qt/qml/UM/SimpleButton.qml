// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1

MouseArea
{
    id: base

    hoverEnabled: true;

    property alias color: image.color;
    property alias backgroundColor: background.color;
    property alias iconSource: image.source;

    property alias hovered: base.containsMouse;

    Rectangle {
        id: background;
        anchors.fill: parent;
        color: "transparent";
    }

    RecolorImage {
        id: image;

        anchors.fill: parent;

        sourceSize.width: width
        sourceSize.height: width

        color: "black";
    }
}
