// Copyright (c) 2022 UltiMaker
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.12
import QtQuick.Controls 2.12

import UM 1.5 as UM

Switch
{
    id: control
    property double indicatorMargin: 2

    indicator: Rectangle
    {
        id: switchBackground
        implicitWidth: 32
        implicitHeight: 16
        x: control.leftPadding
        y: (parent.height - height) / 2
        radius: height / 2
        color: UM.Theme.getColor("switch_state_unchecked")

        Rectangle
        {
            x: control.checked ? parent.width - width - control.indicatorMargin : control.indicatorMargin
            y: control.indicatorMargin
            width: parent.height - 2 * control.indicatorMargin
            height: width
            radius: width / 2
            color: UM.Theme.getColor("switch")
        }
    }

    states:
    [
        State
        {
            name: "checked"
            when: control.checked
            PropertyChanges { target: switchBackground; color: UM.Theme.getColor("switch_state_checked") }
        },
        State
        {
            name: "disabled"
            when: !control.enabled
            PropertyChanges { target: switchBackground; color: UM.Theme.getColor("background_2") }
        }
    ]
}