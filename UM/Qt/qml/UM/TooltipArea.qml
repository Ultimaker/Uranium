// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.4

import UM 1.5 as UM

// TooltipArea.qml

MouseArea
{
    id: _root
    property alias text: tooltip.text

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
        running: _root.enabled && _root.containsMouse && _root.text.length
        onTriggered:
        {
            tooltip.x = _root.mouseX
            tooltip.y = _root.height - _root.mouseY
            tooltip.show()
        }
    }
}
