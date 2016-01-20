// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

TextField
{
    id: base;

    signal valueChanged(string value);
    property bool focusVar: false

    validator: RegExpValidator { regExp: /[0-9.-]+/ }

    onTextChanged: if(base.activeFocus) { valueChanged(text); }

    property variant parentValue: value

    Binding
    {
        target: base
        property: "text"
        value: base.parentValue
        when: !base.activeFocus
    }

    function notifyReset()
    {
        // The reset of this setting field was called so this is the item that has the focus.
        // This ensures that all values are correctly updated when inheritance is in play.
        forceActiveFocus()
        base.text = base.parentValue;
    }

    style: TextFieldStyle
    {
        textColor: itemStyle.controlTextColor;
        font: itemStyle.controlFont;
        background: Rectangle
        {
            implicitHeight: control.height;
            implicitWidth: control.width;

            border.width: itemStyle.controlBorderWidth;
            border.color: control.hovered ? itemStyle.controlBorderHighlightColor : itemStyle.controlBorderColor

            color: {
                switch(valid) //From parent loader
                {
                    case 0:
                        return itemStyle.validationErrorColor;
                    case 1:
                        return itemStyle.validationErrorColor;
                    case 2:
                        return itemStyle.validationErrorColor;
                    case 3:
                        return itemStyle.validationWarningColor;
                    case 4:
                        return itemStyle.validationWarningColor;
                    case 5:
                        return itemStyle.validationOkColor;

                    default:
                        return itemStyle.controlTextColor;
                }
            }

            Rectangle
            {
                anchors.fill: parent;
                anchors.margins: itemStyle.controlBorderWidth;
                color: itemStyle.controlHighlightColor;
                opacity: !control.hovered ? 0 : valid == 5 ? 1.0 : 0.35;
            }

            Label
            {
                anchors.right: parent.right;
                anchors.rightMargin: itemStyle.unitRightMargin;
                anchors.verticalCenter: parent.verticalCenter;

                text: unit; //From parent loader
                color: itemStyle.unitColor; //From parent loader
                font: itemStyle.unitFont;
            }
        }
    }
}
