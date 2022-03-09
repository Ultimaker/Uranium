// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.1
import QtQuick.Window 2.1

import UM 1.5 as UM

Item
{
    property alias title: titleLabel.text
    default property alias contents: contentsItem.children
    property bool resetEnabled: true
    property alias buttons: buttonRow.children

    function reset()
    {
        UM.Application.log("w", "No reset implemented!")
    }
    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if (value == "True")
        {
            return true
        }
        else if (value == "False" || value == undefined)
        {
            return false
        }
        else
        {
            return value
        }
    }

    Item
    {
        id: titleBar
        height: buttonRow.height
        anchors
        {
            top: parent.top
            left: parent.left
            right: parent.right
            margins: UM.Theme.getSize("narrow_margin").width
        }
        UM.Label
        {
            id: titleLabel
            anchors.verticalCenter: parent.verticalCenter
            font: UM.Theme.getFont("large_bold")
        }
        Row
        {
            id: buttonRow
            anchors.verticalCenter: parent.verticalCenter
            spacing: UM.Theme.getSize("narrow_margin").width
            anchors.right: parent.right
            height: childrenRect.height
        }
    }

    Rectangle
    {
        color: UM.Theme.getColor("main_background")
        anchors
        {
            top: titleBar.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: UM.Theme.getSize("narrow_margin").width
            bottomMargin: 0
        }
        Item
        {
            id: contentsItem

            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width

            clip: true
        }
    }
}
