// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2

import UM 1.7 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string xText
    property string yText
    property string zText

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
        var output = ""
        if (input !== undefined)
        {
            output = input.toFixed(decimals).replace(/\.?0*$/, ""); //Match on periods, if any ( \.? ), followed by any number of zeros ( 0* ), then the end of string ( $ ).
        }
        if (output == "-0")
        {
            output = "0"
        }
        return output
    }

    function selectTextInTextfield(selected_item){
        selected_item.selectAll()
        selected_item.focus = true
    }

    Grid
    {
        id: textfields

        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: parent.top

        columns: 2
        flow: Grid.TopToBottom
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2)

        UM.Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "X"
            color: UM.Theme.getColor("x_axis")
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        UM.Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "Y"
            color: UM.Theme.getColor("z_axis"); // This is intentional. The internal axis are switched.
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        UM.Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "Z"
            color: UM.Theme.getColor("y_axis"); // This is intentional. The internal axis are switched.
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }
        UM.TextFieldWithUnit
        {
            id: xTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "mm"
            text: xText
            validator: UM.FloatValidator
            {
                maxBeforeDecimal: 8
                maxAfterDecimal: 4
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("X", modified_text)
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    xText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    xText = 0
                }
            }
            Keys.onBacktabPressed: selectTextInTextfield(zTextField)
            Keys.onTabPressed: selectTextInTextfield(yTextField)
        }
        UM.TextFieldWithUnit
        {
            id: yTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "mm"
            text: yText
            validator: UM.FloatValidator
            {
                maxBeforeDecimal: 8
                maxAfterDecimal: 4
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("Y", modified_text)
            }

            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    yText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    yText = 0
                }
            }
            Keys.onBacktabPressed: selectTextInTextfield(xTextField)
            Keys.onTabPressed: selectTextInTextfield(zTextField)
        }
        UM.TextFieldWithUnit
        {
            id: zTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "mm"
            text: zText
            validator: UM.FloatValidator
            {
                maxBeforeDecimal: 8
                maxAfterDecimal: 4
            }
            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("Z", modified_text)
            }

            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    zText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    zText = 0
                }
            }
            Keys.onBacktabPressed: selectTextInTextfield(yTextField)
            Keys.onTabPressed: selectTextInTextfield(xTextField)
        }
    }

    Flow
    {
        id: checkboxes

        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height
        anchors.right: parent.right
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        UM.CheckBox
        {
            id: lockPositionCheckbox
            text: catalog.i18nc("@option:check", "Lock Model")

            property string binded_state
            tristate: true
            nextCheckState: function() {
                const new_state = checkState !== Qt.Checked;
                UM.ActiveTool.setProperty("LockPosition", new_state)
                return new_state ? Qt.Checked : Qt.Unchecked
            }

            width: parent.width //Use a width instead of anchors to allow the flow layout to resolve positioning.
        }

        UM.CheckBox
        {
            id: autoDropDownCheckbox
            text: catalog.i18nc("@option:check", "Drop Down Model")

            tristate: true
            nextCheckState: function() {
                const new_state = checkState !== Qt.Checked;
                UM.ActiveTool.setProperty("AutoDropDown", new_state)
                return new_state ? Qt.Checked : Qt.Unchecked
            }

            width: parent.width //Use a width instead of anchors to allow the flow layout to resolve positioning.
        }

        function getCheckBoxState(property) {
            const value = UM.ActiveTool.properties.getValue(property)
            if (value) {
                return Qt.Checked
            }
            else if (value === undefined){
                return Qt.PartiallyChecked
            }
            else {
                return Qt.Unchecked
            }
        }

        Binding
        {
            target: lockPositionCheckbox
            property: "checkState"
            value: checkboxes.getCheckBoxState("LockPosition")
        }

        Binding
        {
            target: autoDropDownCheckbox
            property: "checkState"
            value: checkboxes.getCheckBoxState("AutoDropDown")
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
}
