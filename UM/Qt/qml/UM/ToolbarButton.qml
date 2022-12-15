// Copyright (c) 2022 UltiMaker
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.5 as UM

Button
{
    id: base

    property alias toolItem: contentItemLoader.sourceComponent

    // These two properties indicate whether the toolbar button is at the top of the toolbar column or at the bottom.
    // If it is somewhere in the middle, then both has to be false. If there is only one element in the column, then
    // both properties have to be set to true. This is used to create a rounded corner.
    property bool isTopElement: false
    property bool isBottomElement: false
    property int buttonSize: UM.Theme.getSize("button").width
    property double iconScale: 0.5

    hoverEnabled: true

    // Recalculed scaled size when used to center within another component.
    // As we can not place component on fractional coordinates ill-related
    // parent-child sized components will result in un-centered placement of the child component.
    // Behavior of this function if the initial size is
    //   -even will result in an even-sized new component,
    //   -odd will result in an odd-sized new component.
    // This will always result in an even left over space (initialSize - newSize) which
    // can be partitioned in two even margin which will result in an centered component
    function resizeCenter(initialSize, scaleFactor)
    {
        return initialSize - Math.round(initialSize * (1 - scaleFactor) / 2) * 2;
    }

    background: Rectangle
    {
        implicitWidth: buttonSize
        implicitHeight: buttonSize
        color: "transparent"
        radius: UM.Theme.getSize("default_radius").width

        Rectangle
        {
            id: topSquare
            anchors
            {
                left: parent.left
                right: parent.right
                top: parent.top
            }
            height: parent.radius
            color: parent.color
            visible: !base.isTopElement
        }

        Rectangle
        {
            id: bottomSquare
            anchors
            {
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }
            height: parent.radius
            color: parent.color
            visible: !base.isBottomElement
        }

        Rectangle
        {
            id: leftSquare
            anchors
            {
                left: parent.left
                top: parent.top
                bottom: parent.bottom
            }
            width: parent.radius
            color: parent.color
        }
    }
    contentItem: Rectangle
    {
        implicitWidth: contentSize
        implicitHeight: contentSize
        opacity: parent.enabled ? 1.0 : 0.2
        property int contentSize: resizeCenter(buttonSize, 0.75);
        radius: Math.round(width * 0.5)

        color:
        {
            if (base.checked && base.hovered)
            {
                return UM.Theme.getColor("toolbar_button_active_hover")
            }
            else if (base.checked)
            {
                return UM.Theme.getColor("toolbar_button_active")
            }
            else if(base.hovered)
            {
                return UM.Theme.getColor("toolbar_button_hover")
            }
            return UM.Theme.getColor("toolbar_background")
        }
        Loader
        {
            id: contentItemLoader
            width: iconSize
            height: iconSize
            anchors.centerIn: parent
            property int iconSize: resizeCenter(buttonSize, iconScale);
        }
    }

    UM.ToolTip
    {
        id: tooltip
        tooltipText: base.text
        visible: base.hovered
    }
}
