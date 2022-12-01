//Copyright (c) 2022 UltiMaker B.V.
//Cura is released under the terms of the LGPLv3 or higher.

import QtQuick.Controls 2.15
import QtQuick 2.15

import UM 1.5 as UM

TextField
{
    id: control
    property alias unit: unitLabel.text
    property alias liningColor: background.liningColor
    property alias borderColor: background.borderColor
    property alias unitText: unitLabel.text

    renderType: Qt.platform.os == "osx" ? Text.QtRendering : Text.NativeRendering

    selectByMouse: true
    hoverEnabled: true
    font: UM.Theme.getFont("default")
    color: UM.Theme.getColor("text_field_text")
    selectedTextColor: UM.Theme.getColor("text_field_text")
    placeholderTextColor: UM.Theme.getColor("text_field_text_disabled")
    selectionColor: UM.Theme.getColor("text_selection")

    background: UM.UnderlineBackground
    {
        id: background

        UM.Label
        {
            id: unitLabel
            anchors.right: parent.right
            anchors.rightMargin: Math.round(UM.Theme.getSize("setting_unit_margin").width)
            anchors.verticalCenter: parent.verticalCenter
            visible: text != ""
            textFormat: Text.PlainText
            color: UM.Theme.getColor("setting_unit")
        }
    }

    states: [
        State
        {
            name: "disabled"
            when: !control.enabled
            PropertyChanges { target: control; color: UM.Theme.getColor("text_field_text_disabled")}
            PropertyChanges { target: background; liningColor: UM.Theme.getColor("text_field_border_disabled")}
        },
        State
        {
            name: "invalid"
            when: !control.acceptableInput
            PropertyChanges { target: background; color: UM.Theme.getColor("setting_validation_error_background")}
        },
        State
        {
            name: "active"
            when: control.activeFocus
            PropertyChanges
            {
                target: background
                liningColor: UM.Theme.getColor("text_field_border_active")
                borderColor: UM.Theme.getColor("text_field_border_active")
            }
        },
        State
        {
            name: "hovered"
            when: control.hovered && !control.activeFocus
            PropertyChanges
            {
                target: background
                liningColor: UM.Theme.getColor("text_field_border_hovered")
            }
        }
    ]
}