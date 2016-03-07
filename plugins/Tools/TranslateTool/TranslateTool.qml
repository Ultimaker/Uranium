// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    width: Math.max(14 * UM.Theme.getSize("line").width, childrenRect.width);
    height: Math.max(4.5 * UM.Theme.getSize("line").height, childrenRect.height);
    UM.I18nCatalog { id: catalog; name:"uranium"}

    Grid
    {
        id: textfields;

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

        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.top: parent.top;

        columns: 2;
        flow: Grid.TopToBottom;
        spacing: UM.Theme.getSize("default_margin").width / 2;

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "X";
            font: UM.Theme.getFont("default");
            color: "red"
            verticalAlignment: Text.AlignVCenter;
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Y";
            font: UM.Theme.getFont("default");
            color: "green"
            verticalAlignment: Text.AlignVCenter;
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Z";
            font: UM.Theme.getFont("default");
            color: "blue"
            verticalAlignment: Text.AlignVCenter;
        }
        TextField
        {
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.getValue("X").toFixed(4).replace(/\.?0*$/, "")
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("X", text);
        }
        TextField
        {
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: parent.roundFloat(UM.ActiveTool.properties.getValue("Y"), 4)
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("Y", text);
        }
        TextField
        {
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: parent.roundFloat(UM.ActiveTool.properties.getValue("Z"), 4)
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("Z", text);
        }
    }
}