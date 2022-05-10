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
            PropertyChanges { target: indicator_background; border.color: UM.Theme.getColor("checkbox_border_hover"); }
        },
        State {
            name: "disabled"
            when: !control.enabled
            PropertyChanges
            {
                target: indicator_background
                color: UM.Theme.getColor("checkbox_disabled")
                border.color: UM.Theme.getColor("checkbox_border_disabled")
            }
        }
    ]

    indicator: Rectangle
    {
        id: indicator_background
        implicitWidth:  UM.Theme.getSize("checkbox").width
        implicitHeight: UM.Theme.getSize("checkbox").height
        anchors.verticalCenter: parent.verticalCenter

        color: UM.Theme.getColor("checkbox")
        border.color: UM.Theme.getColor("checkbox_border")
        border.width: UM.Theme.getSize("default_lining").width

        Behavior on color { ColorAnimation { duration: 50; } }
        radius: UM.Theme.getSize("checkbox_radius").width

        UM.ColorImage
        {
            id: indicator_item
            height: width

            states: [
                State {
                    name: "unchecked"
                    when: control.checkState == Qt.Unchecked
                    PropertyChanges
                    {
                        target: indicator_item
                        visible: false
                        source: ""
                    }
                },
                State {
                    name: "partially_checked"
                    when: control.checkState == Qt.PartiallyChecked
                    PropertyChanges
                    {
                        target: indicator_item
                        width: Math.round(parent.width / 1.8)
                        color: control.enabled ? UM.Theme.getColor("checkbox_square") : UM.Theme.getColor("checkbox_mark_disabled")
                        source: UM.Theme.getIcon("Solid")
                        visible: true
                    }
                },
                State {
                    name: "checked"
                    when: control.checkState == Qt.Checked
                    PropertyChanges
                    {
                        target: indicator_item
                        width: Math.round(parent.width / 1.5)
                        color: control.enabled ? UM.Theme.getColor("checkbox_mark") : UM.Theme.getColor("checkbox_mark_disabled")
                        source: UM.Theme.getIcon("Check", "low")
                        visible: true
                    }
                }
            ]

            anchors.centerIn: parent

            Behavior on opacity { NumberAnimation { duration: 100; } }
        }
    }
    contentItem: UM.Label
    {
        text: control.text
        height: contentHeight
        color: control.enabled ? UM.Theme.getColor("checkbox_text"): UM.Theme.getColor("checkbox_text_disabled")
        elide: Text.ElideRight
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
