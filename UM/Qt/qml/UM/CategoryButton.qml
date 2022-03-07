// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 2.1

import UM 1.5 as UM

Button
{
    id: base

    height: enabled ? UM.Theme.getSize("section").height : 0

    property var expanded: false

    property alias arrow: category_arrow
    property alias categoryIcon: icon.source
    property alias labelText: settingNameLabel.text

    property color text_color:
    {
        if (!base.enabled)
        {
            return UM.Theme.getColor("setting_category_disabled_text")
        } else if (base.hovered || base.pressed || base.activeFocus)
        {
            return UM.Theme.getColor("setting_category_active_text")
        }

        return UM.Theme.getColor("setting_category_text")
    }

    background: Rectangle
    {
        id: backgroundRectangle
        height: base.height
        anchors.verticalCenter: parent.verticalCenter

        color: UM.Theme.getColor("setting_category")
        Behavior on color { ColorAnimation { duration: 50; } }

        Rectangle
        {
            //Lining on top
            anchors.top: parent.top
            color: UM.Theme.getColor("border_main")
            height: UM.Theme.getSize("default_lining").height
            width: parent.width
        }

        states:
        [
            State
            {
                name: "disabled"
                when: !base.enabled
                PropertyChanges { target: backgroundRectangle; color: UM.Theme.getColor("setting_category_disabled")}
            },
            State
            {
                name: "hovered"
                when: base.hovered
                PropertyChanges { target: backgroundRectangle; color: UM.Theme.getColor("setting_category_hover")}
            }
        ]
    }

    contentItem: Item
    {
        anchors.fill: parent

        Label
        {
            id: settingNameLabel
            anchors
            {
                left: parent.left
                leftMargin: (0.9 * UM.Theme.getSize("default_margin").width) + UM.Theme.getSize("section_icon").width
                right: parent.right
                verticalCenter: parent.verticalCenter
            }
            text: ""
            textFormat: Text.PlainText
            renderType: Text.NativeRendering
            font: UM.Theme.getFont("medium_bold")
            color: base.text_color
            fontSizeMode: Text.HorizontalFit
            minimumPointSize: 8
        }

        UM.RecolorImage
        {
            id: category_arrow
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: UM.Theme.getSize("narrow_margin").width
            width: UM.Theme.getSize("standard_arrow").width
            height: UM.Theme.getSize("standard_arrow").height
            sourceSize.height: width
            color: UM.Theme.getColor("setting_control_button")
            source: expanded ? UM.Theme.getIcon("ChevronSingleDown") : UM.Theme.getIcon("ChevronSingleLeft")
        }
    }

    UM.RecolorImage
    {
        id: icon
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        color: base.text_color
        width: UM.Theme.getSize("section_icon").width
        height: UM.Theme.getSize("section_icon").height
        sourceSize.width: width
        sourceSize.height: width
    }
}