// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

TextField {
    id: base;

    signal valueChanged(string value);

    text: value; //From parent loader
    validator: RegExpValidator { regExp: /[0-9.-]+/ }

    onTextChanged: valueChanged(text);

    style: TextFieldStyle
    {
        textColor: itemStyle.controlTextColor;
        font: itemStyle.controlFont;
        background: Rectangle
        {
            implicitHeight: control.height;
            implicitWidth: control.width;

            border.width: itemStyle.controlBorderWidth;
            border.color: itemStyle.controlBorderColor;

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
                        console.log(base.valid)
                        return "black"
                }
            }

            Rectangle {
                anchors.fill: parent;
                anchors.margins: itemStyle.controlBorderWidth;
                color: itemStyle.controlHighlightColor;
                opacity: !control.hovered ? 0 : valid == 5 ? 1.0 : 0.35;
            }

            Label {
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
