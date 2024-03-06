// Copyright (c) 2024 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.8 as UM

MouseArea
{
    property alias text: tooltip.text
    property alias icon: image.source
    property alias color: image.color

    id: helpIconMouseArea
    hoverEnabled: true

    implicitWidth: UM.Theme.getSize("section_icon").width
    implicitHeight: UM.Theme.getSize("section_icon").height

    UM.ColorImage
    {
        id: image
        anchors.fill: parent
        color: UM.Theme.getColor("warning")
        source: UM.Theme.getIcon("Help")

        UM.ToolTip
        {
            UM.I18nCatalog { id: catalog; name: "cura" }

            id: tooltip
            visible: helpIconMouseArea.containsMouse
            targetPoint: Qt.point(parent.x + Math.round(parent.width / 2), parent.y)
            x: 0
            y: parent.y + parent.height + UM.Theme.getSize("default_margin").height
            width: UM.Theme.getSize("tooltip").width
        }
    }
}