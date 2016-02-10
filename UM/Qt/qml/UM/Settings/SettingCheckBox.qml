// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

MouseArea
{
    id: base;

    signal valueChanged(bool value);

    property bool checked:
    {
        if(value == "True")
        {
            return true;
        }
        else if(value == "False")
        {
            return false;
        }
        else
        {
            return value;
        }
    }

    onClicked: valueChanged(!checked);

    hoverEnabled: true;

    Rectangle
    {
        anchors
        {
            top: parent.top
            bottom: parent.bottom
            left: parent.left
        }
        width: height

        color:
        {
            if(base.containsMouse || base.activeFocus)
            {
                return itemStyle.controlHighlightColor
            }
            else
            {
                return itemStyle.controlColor
            }
        }
        border.width: itemStyle.controlBorderWidth;
        border.color: base.containsMouse ? itemStyle.controlBorderHighlightColor : itemStyle.controlBorderColor;

        UM.RecolorImage {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width/2.5
            height: parent.height/2.5
            sourceSize.width: width
            sourceSize.height: width
            color: UM.Theme.getColor("checkbox_mark");
            source: UM.Theme.getIcon("check")
            opacity: base.checked
            Behavior on opacity { NumberAnimation { duration: 100; } }
        }
    }
}
/*
CheckBox
{
    signal valueChanged(bool value);
    id: base
    checked: boolCheck(value) //From parent loader

    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if(value == "True")
        {
            return true
        }else if(value == "False")
        {
            return false
        }
        else
        {
            return value
        }
    }

    MouseArea {
        anchors.fill: parent;
        onClicked: valueChanged(!checked);
    }

    style: CheckBoxStyle
    {
        background: Item { }
        label: Label{ }
        indicator:
    }
}*/
