// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.3
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.1

import UM 1.3 as UM

ListView
{
    id: base
    boundsBehavior: ListView.StopAtBounds
    verticalLayoutDirection: ListView.BottomToTop

    model: UM.VisibleMessagesModel { }
    spacing: UM.Theme.getSize("default_margin").height

    // Messages can have actions, which are displayed by means of buttons. The message stack supports 3 styles
    // of buttons "Primary", "Secondary" and "Link" (aka; "tertiary")
    property Component primaryButton: Component
    {
        Button
        {
            text: model.name
        }
    }

    property Component secondaryButton: Component
    {
        Button
        {
            text: model.name
        }
    }

    property Component link: Component
    {
        Button
        {
            text: model.name
            style: ButtonStyle
            {
                background: Item {}

                label: Label
                {
                    text: control.text
                    font:
                    {
                        var defaultFont = UM.Theme.getFont("default")
                        defaultFont.underline = true
                        return defaultFont
                    }
                    color: UM.Theme.getColor("text_link")
                }
            }
        }
    }

    interactive: false

    delegate: Message {}


    add: Transition
    {
        NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200; }
    }

    displaced: Transition
    {
        NumberAnimation { property: "y"; duration: 200; }
    }

    remove: Transition
    {
        NumberAnimation { property: "opacity"; to: 0; duration: 200; }
    }

}
