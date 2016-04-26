// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Rectangle
{
    id: base;

    signal valueChanged(string value);

    property alias hovered: mouseArea.containsMouse;

    border.width: itemStyle.controlBorderWidth;
    border.color: !enabled ? itemStyle.controlDisabledBorderColor : hovered ? itemStyle.controlBorderHighlightColor : itemStyle.controlBorderColor

    property variant parentValue: value //From parent loader
    function notifyReset() {
        input.text = format(parentValue)
    }

    color: {
        if (!enabled)
        {
            return itemStyle.controlDisabledColor
        }
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
        opacity: !base.hovered ? 0 : valid == 5 ? 1.0 : 0.35;
    }

    Label
    {
        anchors.right: parent.right;
        anchors.rightMargin: itemStyle.unitRightMargin;
        anchors.verticalCenter: parent.verticalCenter;

        text: unit; //From parent loader
        color: itemStyle.unitColor
        font: itemStyle.unitFont;
    }

    MouseArea
    {
        id: mouseArea
        anchors.fill: parent;
        hoverEnabled: true;
        cursorShape: Qt.IBeamCursor
    }

    TextInput
    {
        id: input

        anchors
        {
            left: parent.left
            leftMargin: itemStyle.unitRightMargin
            right: parent.right
            verticalCenter: parent.verticalCenter
        }

        Keys.onReleased:
        {
            text = text.replace(",", ".") // User convenience. We use dots for decimal values
            if(parseFloat(text) != base.parentValue)
            {
                base.valueChanged(parseFloat(text));
            }
        }

        onEditingFinished:
        {
            if(parseFloat(text) != base.parentValue)
            {
                base.valueChanged(parseFloat(text));
            }
        }

        color: !enabled ? itemStyle.controlDisabledTextColor : itemStyle.controlTextColor;
        font: itemStyle.controlFont;

        selectByMouse: true;

        maximumLength: 10;

        validator: RegExpValidator { regExp: (type == "int") ? /[0-9-]{0,10}/ : /[0-9.,-]{0,10}/ } //"type" property from parent loader used to disallow fractional number entry

        Binding
        {
            target: input
            property: "text"
            value: format(base.parentValue)
            when: !input.activeFocus
        }
    }

    //Rounds a floating point number to 4 decimals. This prevents floating
    //point rounding errors.
    //
    //input:    The number to round.
    //decimals: The number of decimals (digits after the radix) to round to.
    //return:   The rounded number.
    function roundFloat(input, decimals)
    {
        //First convert to fixed-point notation to round the number to 4 decimals and not introduce new floating point errors.
        //Then convert to a string (is implicit). The fixed-point notation will be something like "3.200".
        //Then remove any trailing zeroes and the radix.
        return input.toFixed(decimals).replace(/\.?0*$/, ""); //Match on periods, if any ( \.? ), followed by any number of zeros ( 0* ), then the end of string ( $ ).
    }

    //Formats a value for display in the text field.
    //
    //This correctly handles formatting of float values.
    //
    //input:  The string value to format.
    //return: The formatted string.
    function format(inputValue) {
      return parseFloat(inputValue) ? roundFloat(parseFloat(inputValue), 4) : inputValue //If it's a float, round to four decimals.
    }
}
