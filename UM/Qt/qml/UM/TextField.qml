// Copyright (c) 2022 UltiMaker
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick.Controls 2.15
import QtQuick 2.15

import UM 1.5 as UM


// Base styles UM TextField. When creating new TextFields use this as the base.
TextField
{
    id: control
    property alias unit: unitLabel.text
    property alias liningColor: background.liningColor
    property alias borderColor: background.borderColor
    property alias unitText: unitLabel.text

    // States added in this component take precedence over states defined in children. You can force use child states
    // over these states by setting this value to true. Look at SingleSettingTextField states for an example.
    property bool overrideState: false

    renderType: Qt.platform.os === "osx" ? Text.QtRendering : Text.NativeRendering

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
            visible: text !== ""
            textFormat: Text.PlainText
            color: UM.Theme.getColor("setting_unit")
        }
    }
    // Change the name of the states based on if it's overriden. This is to prevent the spam of "duplicate state"
    states: [
        State
        {
            name: overrideState? "__disabled":" disabled"
            when: !control.enabled && !overrideState
            PropertyChanges
            {
                target: control
                color: UM.Theme.getColor("text_field_text_disabled")
            }
            PropertyChanges
            {
                target: background
                liningColor: UM.Theme.getColor("text_field_border_disabled")
            }
        },
        State
        {
            name: overrideState? "__invalid":" invalid"
            when: !control.acceptableInput && !overrideState
            PropertyChanges
            {
                target: background
                color: UM.Theme.getColor("setting_validation_error_background")
            }
        },
        State
        {
            name: overrideState? "__active": "active"
            when: control.activeFocus && !overrideState
            PropertyChanges
            {
                target: background
                liningColor: UM.Theme.getColor("text_field_border_active")
                borderColor: UM.Theme.getColor("text_field_border_active")
            }
        },
        State
        {
            name: overrideState? "__hovered": "hovered"
            when: control.hovered && !control.activeFocus && !overrideState
            PropertyChanges
            {
                target: background
                liningColor: UM.Theme.getColor("text_field_border_hovered")
            }
        }
    ]
}