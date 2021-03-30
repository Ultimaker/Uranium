// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string xText
    property string yText
    property string zText
    property string lockPosition

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
        var output = "";
        if (input !== undefined)
        {
            output = input.toFixed(decimals).replace(/\.?0*$/, ""); //Match on periods, if any ( \.? ), followed by any number of zeros ( 0* ), then the end of string ( $ ).
        }
        if (output == "-0")
        {
            output = "0";
        }
        return output;
    }

    function selectTextInTextfield(selected_item){
        selected_item.selectAll()
        selected_item.focus = true
    }

    Grid
    {
        id: textfields;

        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.top: parent.top;

        columns: 2;
        flow: Grid.TopToBottom;
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2);

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "X";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("x_axis");
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Y";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("z_axis"); // This is intentional. The internal axis are switched.
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Z";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("y_axis"); // This is intentional. The internal axis are switched.
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }
        TextField
        {
            id: xTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: xText
            validator: DoubleValidator
            {
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("X", modified_text);
            }
            Keys.onBacktabPressed: selectTextInTextfield(zTextField)
            Keys.onTabPressed: selectTextInTextfield(yTextField)
        }
        TextField
        {
            id: yTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: yText
            validator: DoubleValidator
            {
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("Y", modified_text);
            }
            Keys.onBacktabPressed: selectTextInTextfield(xTextField)
            Keys.onTabPressed: selectTextInTextfield(zTextField)
        }
        TextField
        {
            id: zTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: zText
            validator: DoubleValidator
            {
                decimals: 4
                locale: "en_US"
            }
            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("Z", modified_text);
            }
            Keys.onBacktabPressed: selectTextInTextfield(yTextField)
            Keys.onTabPressed: selectTextInTextfield(xTextField)
        }
    }

    CheckBox
    {
        property var checkbox_state: 0; // if the state number is 2 then the checkbox has "partially" state

        // temporary property, which is used to recalculate checkbox state and keeps reference of the
        // binging object. If the binding object changes then checkBox state will be updated.
        property var temp_checkBox_value:{

            checkbox_state = getCheckBoxState()

            // returning the lockPosition the propery will keep reference, for updating
            return base.lockPosition
        }

        function getCheckBoxState(){

            if (base.lockPosition == "true"){
                lockPositionCheckbox.checked = true
                return 1;
            }
            else if (base.lockPosition == "partially"){
                lockPositionCheckbox.checked = true
                return 2;
            }
            else{
                lockPositionCheckbox.checked = false
                return 0;
            }
        }


        id: lockPositionCheckbox
        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        text: catalog.i18nc("@option:check","Lock Model");
        style: UM.Theme.styles.partially_checkbox;

        onClicked: {

            // If state is partially, then set Checked
            if (checkbox_state == 2){
                lockPositionCheckbox.checked = true
                UM.ActiveTool.setProperty("LockPosition", true);
            }
            else{
                UM.ActiveTool.setProperty("LockPosition", lockPositionCheckbox.checked);
            }

            // After clicking the base.lockPosition is not refreshed, fot this reason manually update the state
            // Set zero because only 2 will show partially icon in checkbox
            checkbox_state = 0;
        }
    }

    // We have to use indirect bindings, as the values can be changed from the outside, which could cause breaks
    // (for instance, a value would be set, but it would be impossible to change it).
    // Doing it indirectly does not break these.
    Binding
    {
        target: base
        property: "xText"
        value: base.roundFloat(UM.ActiveTool.properties.getValue("X"), 4)
    }

    Binding
    {
        target: base
        property: "yText"
        value: base.roundFloat(UM.ActiveTool.properties.getValue("Y"), 4)
    }

    Binding
    {
        target: base
        property: "zText"
        value:base.roundFloat(UM.ActiveTool.properties.getValue("Z"), 4)
    }

    Binding
    {
        target: base
        property: "lockPosition"
        value: UM.ActiveTool.properties.getValue("LockPosition")
    }
}
