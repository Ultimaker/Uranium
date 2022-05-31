// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.5 as UM

ToolTip
{
    // Defines the alignment of the content, by default to the left
    property int contentAlignment: UM.Enums.ContentAlignment.AlignRight

    property alias tooltipText: tooltip.text
    property alias arrowSize: backgroundRect.arrowSize
    property var targetPoint: Qt.point(parent.x, y + Math.round(height/2))

    id: tooltip
    text: ""
    delay: 500
    font: UM.Theme.getFont("default")
    visible: opacity != 0.0
    opacity: 0.0 // initially hidden

    Behavior on opacity
    {
        NumberAnimation { duration: 100; }
    }

    onAboutToShow: show()
    onAboutToHide: hide()

    // If the text is not set, just set the height to 0 to prevent it from showing
    height: label.contentHeight + 2 * UM.Theme.getSize("thin_margin").width

    x:
    {
        switch (contentAlignment)
        {
            case UM.Enums.ContentAlignment.AlignLeft:
                return (label.width + Math.round(UM.Theme.getSize("default_arrow").width * 1.2) + padding * 2) * -1;
            case UM.Enums.ContentAlignment.AlignRight:
                return parent.width + Math.round(UM.Theme.getSize("default_arrow").width * 1.2 + padding);
        }
    }

    y: Math.round(parent.height / 2 - label.height / 2 ) - padding

    padding: UM.Theme.getSize("thin_margin").width

    background: UM.PointingRectangle
    {
        id: backgroundRect
        color: UM.Theme.getColor("tooltip")
        target: Qt.point(targetPoint.x - tooltip.x, targetPoint.y - tooltip.y)
        arrowSize: UM.Theme.getSize("default_arrow").width
        visible: tooltip.height != 0
    }

    contentItem: UM.Label
    {
        id: label
        text: tooltip.text
        font: tooltip.font
        textFormat: Text.RichText
        color: UM.Theme.getColor("tooltip_text")
    }

    function show() {
        opacity = text != "" ? 1 : 0
    }

    function hide() {
        opacity = 0
    }
}