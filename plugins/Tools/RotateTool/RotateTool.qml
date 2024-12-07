// Copyright (c) 2021 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import UM 1.7 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string snapText

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

    UM.ToolbarButton
    {
        id: resetRotationButton

        anchors.left: parent.left;

        text: catalog.i18nc("@action:button", "Reset")
        toolItem: UM.ColorImage
        {
            source: UM.Theme.getIcon("ArrowReset")
            color: UM.Theme.getColor("icon")
        }
        property bool needBorder: true

        z: 2

        onClicked: UM.Controller.triggerAction("resetRotation")
    }

    UM.ToolbarButton
    {
        id: layFlatButton

        anchors.left: resetRotationButton.right
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        //: Lay Flat tool button
        text: catalog.i18nc("@action:button", "Lay flat")

        toolItem: UM.ColorImage
        {
            source: UM.Theme.getIcon("LayFlat")
            color: UM.Theme.getColor("icon")
        }

        z: 1

        onClicked: UM.Controller.triggerAction("layFlat");

        // (Not yet:) Alternative 'lay flat' when legacy OpenGL makes selection of a face in an indexed model impossible.
        // visible: ! UM.Controller.properties.getValue("SelectFaceSupported");
    }

    UM.ToolbarButton{
        id: alignFaceButton

        anchors.left: layFlatButton.visible ? layFlatButton.right : resetRotationButton.right
        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        width: visible ? UM.Theme.getIcon("LayFlatOnFace").width : 0

        text: catalog.i18nc("@action:button", "Select face to align to the build plate")

        toolItem: UM.ColorImage
        {
            source: UM.Theme.getIcon("LayFlatOnFace")
            color: UM.Theme.getColor("icon")
        }

        checkable: true

        enabled: UM.Selection.selectionCount == 1
        checked: UM.Controller.properties.getValue("SelectFaceToLayFlatMode")
        onClicked: UM.Controller.setProperty("SelectFaceToLayFlatMode", checked)

        visible: UM.Controller.properties.getValue("SelectFaceSupported") == true //Might be undefined if we're switching away from the RotateTool!
    }

    Grid
    {
        id: textfields

        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: snapRotationCheckbox.bottom
        visible: snapRotationCheckbox.checked

        columns: 2
        flow: Grid.TopToBottom
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2)

        UM.Label
        {
            height: UM.Theme.getSize("setting_control").height
            text: "Snap Angle"
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

		UM.TextFieldWithUnit
        {
            id: angleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: snapText

            validator: UM.FloatValidator
            {
                maxBeforeDecimal: 3
                maxAfterDecimal: 2
            }
            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                if(text !="")
                {
                    UM.Controller.setProperty("RotationSnapAngle", modified_text)
                }
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    snapText = 0.1; // Need to change it to something else so we can force it to getvalue
                    snapText = UM.Controller.properties.getValue("RotationSnapAngle")
                }
            }
        }
    }

    UM.CheckBox
    {
        id: snapRotationCheckbox
        anchors.top: resetRotationButton.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").width

        //: Snap Rotation checkbox
        text: catalog.i18nc("@action:checkbox","Snap Rotation")

        checked: UM.Controller.properties.getValue("RotationSnap")
        onClicked: UM.Controller.setProperty("RotationSnap", checked)
    }

    Grid
    {
        id: manualInputTextFields

        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: snapRotationCheckbox.bottom

        columns: 2
        flow: Grid.TopToBottom
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2)
        visible: !snapRotationCheckbox.checked

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
            id: xangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: ""

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                if(text !="")
                {
                    UM.Controller.setProperty("RX", modified_text)
                    text =""
                }
            }
        }

        UM.TextFieldWithUnit
        {
            id: yangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: ""

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                if(text !="")
                {
                    // Yes this is intentional. Y & Z are flipped between model axes and build plate axes
                    UM.Controller.setProperty("RZ", modified_text)
                    text =""
                }
            }
        }

        UM.TextFieldWithUnit
        {
            id: zangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: ""

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                if(text !="")
                {
                    // Yes this is intentional. Y & Z are flipped between model axes and build plate axes
                    UM.Controller.setProperty("RY", modified_text)
                    text = ""
                }
            }
        }

	}

    Binding
    {
        target: snapRotationCheckbox
        property: "checked"
        value: UM.Controller.properties.getValue("RotationSnap")
    }

    Binding
    {
        target: alignFaceButton
        property: "checked"
        value: UM.Controller.properties.getValue("SelectFaceToLayFlatMode")
    }

    Binding
    {
        target: base
        property: "snapText"
        value: base.roundFloat(UM.Controller.properties.getValue("RotationSnapAngle"), 2)
    }
}
