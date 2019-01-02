// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.4
import QtQuick.Controls.Private 1.0

// TooltipArea.qml
// This file contains private Qt Quick modules that might change in future versions of Qt
// Tested on: Qt 5.4.1
// Based on https://www.kullo.net/blog/tooltiparea-the-missing-tooltip-component-of-qt-quick/

MouseArea
{
    id: _root
    property string text: ""

    hoverEnabled: _root.enabled

    onExited: Tooltip.hideText()
    onCanceled: Tooltip.hideText()

    Timer
    {
        interval: 1000
        running: _root.enabled && _root.containsMouse && _root.text.length
        onTriggered: Tooltip.showText(_root, Qt.point(_root.mouseX, _root.mouseY), wrapText(_root.text))
    }

    /**
     * Wrap a line of text automatically to a readable width.
     *
     * This automatically wraps the line around if it is too wide.
     *
     * \param text The text to wrap.
     */
    function wrapText(text)
    {
        /* The divider automatically adapts to 100% of the parent width and
        wraps properly, so this causes the tooltips to be wrapped to the width
        of the tooltip as set by the operating system. */
        return "<div>" + text + "</div>"
    }
}
