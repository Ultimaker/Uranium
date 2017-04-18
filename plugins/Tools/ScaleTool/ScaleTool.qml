// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name:"uranium"}

    // We use properties for the text as doing the bindings indirectly doesn't cause any breaks
    // Javascripts don't seem to play well with the bindings (and sometimes break em)
    property string xPercentageText;
    property string yPercentageText;
    property string zPercentageText;

    property string heightText
    property string depthText
    property string widthText

    function getPercentage(scale){
        return scale * 100;
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

    Button
    {
        id: resetScaleButton
        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        z: 1

        //: Reset scale tool button
        text: catalog.i18nc("@action:button","Reset")
        iconSource: UM.Theme.getIcon("scale_reset");

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("resetScale");
    }


    Flow {
        id: checkboxes;

        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.right: parent.right;
        anchors.top: resetScaleButton.top;

        spacing: UM.Theme.getSize("default_margin").height;

        CheckBox
        {
            id: snapScalingCheckbox
            //: Snap Scaling checkbox
            text: catalog.i18nc("@option:check","Snap Scaling");

            style: UM.Theme.styles.checkbox;
            checked: UM.ActiveTool.properties.getValue("ScaleSnap");
            onClicked: {
                UM.ActiveTool.setProperty("ScaleSnap", checked);
                if (snapScalingCheckbox.checked){
                    UM.ActiveTool.setProperty("ScaleX", parseFloat(xPercentage.text) / 100);
                    UM.ActiveTool.setProperty("ScaleY", parseFloat(yPercentage.text) / 100);
                    UM.ActiveTool.setProperty("ScaleZ", parseFloat(zPercentage.text) / 100);
                }
            }
        }

        CheckBox
        {
            //: Uniform scaling checkbox
            text: catalog.i18nc("@option:check","Uniform Scaling");

            style: UM.Theme.styles.checkbox;

            checked: !UM.ActiveTool.properties.getValue("NonUniformScale");
            onClicked: UM.ActiveTool.setProperty("NonUniformScale", !checked);
        }
    }

    Grid
    {
        id: textfields;

        anchors.top: parent.top;

        columns: 3;
        flow: Grid.TopToBottom;
        spacing: UM.Theme.getSize("default_margin").width / 2;

        Text
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "X";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("x_axis");
            verticalAlignment: Text.AlignVCenter;
        }

        Text
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Y";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("z_axis"); // This is intentional. The internal axis are switched.
            verticalAlignment: Text.AlignVCenter;
        }

        Text
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Z";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("y_axis"); // This is intentional. The internal axis are switched.
            verticalAlignment: Text.AlignVCenter;
        }

        TextField
        {
            id: widthTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: widthText
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ObjectWidth", modified_text);
            }
        }
        TextField
        {
            id: depthTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: depthText
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ObjectDepth", modified_text);
            }
        }
        TextField
        {
            id: heightTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: heightText
            validator: DoubleValidator
            {
                bottom: 0.1
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ObjectHeight", modified_text);
            }
        }

        TextField
        {
            id: xPercentage
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: xPercentageText
            validator: DoubleValidator
            {
                // Validate to 0.1 mm
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.getValue("ObjectWidth") / UM.ActiveTool.properties.getValue("ScaleX")));
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ScaleX", parseFloat(modified_text) / 100);
            }
        }
        TextField
        {
            id: zPercentage
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: zPercentageText
            validator: DoubleValidator
            {
                // Validate to 0.1 mm
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.getValue("ObjectDepth") / UM.ActiveTool.properties.getValue("ScaleZ")));
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ScaleZ", parseFloat(modified_text) / 100);
            }
        }
        TextField
        {
            id: yPercentage
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;

            text: yPercentageText
            validator: DoubleValidator
            {
                // Validate to 0.1 mm
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.getValue("ObjectHeight") / UM.ActiveTool.properties.getValue("ScaleY")))
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("ScaleY", parseFloat(modified_text) / 100);
            }

        }

        // We have to use indirect bindings, as the values can be changed from the outside, which could cause breaks
        // (for instance, a value would be set, but it would be impossible to change it).
        // Doing it indirectly does not break these.
        Binding
        {
            target: base
            property: "heightText"
            value: base.roundFloat(UM.ActiveTool.properties.getValue("ObjectHeight"), 4)
        }

        Binding
        {
            target: base
            property: "widthText"
            value: base.roundFloat(UM.ActiveTool.properties.getValue("ObjectWidth"), 4)
        }

        Binding
        {
            target: base
            property: "depthText"
            value:base.roundFloat(UM.ActiveTool.properties.getValue("ObjectDepth"), 4)
        }

        Binding
        {
            target: base
            property: "xPercentageText"
            value: base.roundFloat(100 * UM.ActiveTool.properties.getValue("ScaleX"), 4)
        }

        Binding
        {
            target: base
            property: "yPercentageText"
            value: base.roundFloat(100 * UM.ActiveTool.properties.getValue("ScaleY"), 4)
        }

        Binding
        {
            target: base
            property: "zPercentageText"
            value: base.roundFloat(100 * UM.ActiveTool.properties.getValue("ScaleZ"), 4)
        }
    }
}
