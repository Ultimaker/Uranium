// Copyright (c) 2021 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.15
import QtQuick.Controls 2.15
import UM 1.5 as UM

Button
{
    id: control
    hoverEnabled: true

    property bool needBorder: true
    property alias imageSource: image.source
    property alias imageColor: image.color
    property alias imageWidth: image.width
    property alias imageHeight: image.height
    background: Item
    {
        implicitWidth: UM.Theme.getSize("button").width
        implicitHeight: UM.Theme.getSize("button").height

        UM.PointingRectangle
        {
            id: button_tooltip

            anchors.left: parent.right
            anchors.leftMargin: UM.Theme.getSize("button_tooltip_arrow").width * 2
            anchors.verticalCenter: parent.verticalCenter

            target: Qt.point(parent.x, y + Math.round(height/2))
            arrowSize: UM.Theme.getSize("button_tooltip_arrow").width
            color: UM.Theme.getColor("button_tooltip")
            opacity: control.hovered ? 1.0 : 0.0;
            visible: control.text != ""

            width: control.hovered ? button_tip.width + UM.Theme.getSize("button_tooltip").width : 0
            height: UM.Theme.getSize("button_tooltip").height

            Behavior on width { NumberAnimation { duration: 100; } }
            Behavior on opacity { NumberAnimation { duration: 100; } }

            UM.Label
            {
                id: button_tip

                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                text: control.text
                color: UM.Theme.getColor("tooltip_text")
            }
        }

        Rectangle
        {
            id: buttonFace

            anchors.fill: parent
            property bool down: control.pressed || (control.checkable && control.checked)

            color:
            {
                if(control.customColor !== undefined && control.customColor !== null)
                {
                    return control.customColor
                }
                else if(control.checkable && control.checked && control.hovered)
                {
                    return UM.Theme.getColor("toolbar_button_active_hover")
                }
                else if(control.pressed || (control.checkable && control.checked))
                {
                    return UM.Theme.getColor("toolbar_button_active")
                }
                else if(control.hovered)
                {
                    return UM.Theme.getColor("toolbar_button_hover")
                }
                return UM.Theme.getColor("toolbar_background")
            }
            Behavior on color { ColorAnimation { duration: 50; } }

            border.width: control.needBorder ? UM.Theme.getSize("default_lining").width : 0
            border.color: control.checked ? UM.Theme.getColor("icon") : UM.Theme.getColor("lining")
        }
    }
    contentItem: UM.ColorImage
    {
        id: image
        opacity: control.enabled ? 1.0 : 0.2
        color: UM.Theme.getColor("icon")
    }
}