// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3

import UM 1.3 as UM

CheckBox
{
    id: control

    property alias tooltip: tooltip.text

    hoverEnabled: true

    indicator: Rectangle
    {
        implicitHeight: UM.Theme.getSize("checkbox").height
        implicitWidth: UM.Theme.getSize("checkbox").width

        anchors.verticalCenter: parent.verticalCenter

        color:
        {
            if (!control.enabled)
            {
                return UM.Theme.getColor("checkbox_disabled")
            }
            return UM.Theme.getColor("checkbox")
        }

        radius: UM.Theme.getSize("checkbox_radius").width
        border.width: UM.Theme.getSize("default_lining").width
        border.color:
        {
            if (!enabled)
            {
                return UM.Theme.getColor("checkbox_border")
            }
            if (control.hovered || control.activeFocus)
            {
                return UM.Theme.getColor("checkbox_border_hover")
            }
            return UM.Theme.getColor("checkbox_border")
        }

        UM.RecolorImage
        {
            id: checkIcon

            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            width: height
            sourceSize.height: height

            Behavior on opacity { NumberAnimation { duration: 100; } }

            states: [
                State
                {
                    name: "checked"
                    when: (control.checkState == Qt.Checked)
                    PropertyChanges {
                        target: checkIcon
                        height: UM.Theme.getSize("checkbox_mark").height
                        color: !enabled ? UM.Theme.getColor("setting_control_disabled_text") : UM.Theme.getColor("checkbox_mark")
                        source: UM.Theme.getIcon("Check", "low")
                        opacity: 1
                    }
                },
                State
                {
                    name: "partiallyChecked"
                    when: (control.checkState == Qt.PartiallyChecked)
                    PropertyChanges {
                        target: checkIcon
                        height: UM.Theme.getSize("checkbox_square").height
                        color: !enabled ? UM.Theme.getColor("setting_control_disabled_text") : UM.Theme.getColor("checkbox_square")
                        source: UM.Theme.getIcon("CheckBoxFill", "low")
                        opacity: 1
                    }
                },
                State
                {
                    name: "unchecked"
                    when: (control.checkState == Qt.Unchecked)
                    PropertyChanges {
                        target: checkIcon
                        opacity: 0
                    }
                }
            ]
        }
    }

    contentItem: Label
    {
        id: textLabel
        anchors.left: control.indicator.right
        leftPadding: UM.Theme.getSize("checkbox_label_padding").width
        text: control.text
        font: control.font
        color: UM.Theme.getColor("text")
        renderType: Text.NativeRendering
        verticalAlignment: Text.AlignVCenter
    }

        ToolTip
    {
        id: tooltip
        text: ""
        delay: 500
        visible: text != "" && control.hovered
    }
}
