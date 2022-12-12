// Copyright (c) 2022 UltiMaker
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3

import UM 1.5 as UM

// Reusable component that holds an (re-colorable) icon on the left with a component on the right.
Item
{
    property alias source: icon.source
    property alias iconSize: icon.width
    property alias iconColor: icon.color
    property real spacing: UM.Theme.getSize("narrow_margin").width
    default property alias contents: displayComponentContainer.children

    property string tooltipText: ""

    UM.ColorImage
    {
        id: icon
        // Icon will always match loaded component height
        width: displayComponentContainer.height
        height: width
        color: UM.Theme.getColor("icon")

        anchors
        {
            left: parent.left
            verticalCenter: parent.verticalCenter
        }
    }


    Item
    {
        id: displayComponentContainer
        height: childrenRect.height

        anchors
        {
            left: icon.right
            right: parent.right
            verticalCenter: parent.verticalCenter
            leftMargin: spacing
        }
    }

    MouseArea
    {
        enabled: tooltipText != ""
        anchors.fill: parent
        hoverEnabled: true
        onEntered: base.showTooltip(parent, Qt.point(-UM.Theme.getSize("thick_margin").width, 0), tooltipText)
        onExited: base.hideTooltip()
    }
}