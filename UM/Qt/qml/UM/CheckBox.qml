// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.0 as UM

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

        color: UM.Theme.getColor("checkbox")
        Behavior on color { ColorAnimation { duration: 50; } }
        radius: UM.Theme.getSize("checkbox_radius").width
        anchors.verticalCenter: parent.verticalCenter
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("checkbox_border")

        UM.RecolorImage
        {
            anchors.centerIn: parent
            width: Math.round(parent.width / 1.5)
            height: Math.round(parent.height / 1.5)

            sourceSize.height: width
            color: UM.Theme.getColor("checkbox_mark")
            source: UM.Theme.getIcon("Check", "low")
            opacity: control.checked
            Behavior on opacity { NumberAnimation { duration: 100; } }
        }
    }
    contentItem: Label
    {
        text: control.text
        height: contentHeight
        color: UM.Theme.getColor("checkbox_text")
        font: UM.Theme.getFont("default")
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
