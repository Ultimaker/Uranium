// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.4

import UM 1.5 as UM

// TooltipArea.qml
Item {
    id: _root

    property alias text: tooltip.text
    property alias acceptedButtons: mouse_area.acceptedButtons

    MouseArea
    {
        id: mouse_area
        anchors.fill: _root
        z: 1000
        propagateComposedEvents: true
        hoverEnabled: _root.enabled
        acceptedButtons: Qt.NoButton

        onExited: tooltip.hide()
        onCanceled: tooltip.hide()

        UM.ToolTip
        {
            id: tooltip
            arrowSize: 0
        }

        Timer
        {
            interval: 1000
            running: _root.enabled && mouse_area.containsMouse && _root.text.length
            onTriggered:
            {
                tooltip.x = mouse_area.mouseX
                tooltip.y = mouse_area.height - mouse_area.mouseY
                tooltip.show()
            }
        }
    }
}
