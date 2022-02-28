// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.5 as UM

CheckBox
{
    id: control
    property alias tooltip: tooltip.text

    hoverEnabled: true
    states: [
        State {
            name: "hovered"
            when: control.hovered
            PropertyChanges { target: indicator_background; color: UM.Theme.getColor("checkbox_hover")}
            PropertyChanges { target: indicator_background; border.color: UM.Theme.getColor("checkbox_border_hover")}
        },
        State {
            name: "disabled"
            when: !control.enabled
            PropertyChanges { target: indicator_background; color: UM.Theme.getColor("checkbox_disabled")}
        }
    ]

    indicator: Rectangle
    {
        id: indicator_background
        implicitWidth:  UM.Theme.getSize("checkbox").width
        implicitHeight: UM.Theme.getSize("checkbox").height

        color: control.enabled ? UM.Theme.getColor("checkbox") : UM.Theme.getColor("checkbox_disabled")
        Behavior on color { ColorAnimation { duration: 50; } }
        radius: UM.Theme.getSize("checkbox_radius").width
        anchors.verticalCenter: parent.verticalCenter
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("checkbox_border")

        UM.RecolorImage
        {
            anchors.centerIn: parent
            width: Math.round(parent.width / 2.5)
            height: Math.round(parent.height / 2.5)

            sourceSize.height: width
            color: control.enabled ? UM.Theme.getColor("checkbox_mark") : UM.Theme.getColor("checkbox_disabled")
            source: UM.Theme.getIcon("Check")
            opacity: control.checked
            Behavior on opacity { NumberAnimation { duration: 100; } }
        }
    }
    contentItem: UM.Label
    {
        text: control.text
        height: contentHeight
        color: control.enabled ? UM.Theme.getColor("checkbox_text"): UM.Theme.getColor("checkbox_disabled")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width
    }
    ToolTip
    {
        id: tooltip
        text: ""
        delay: 500
        visible: text != "" && control.hovered
    }
}
