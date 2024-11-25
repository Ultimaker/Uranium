// Copyright (c) 2021 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import UM 1.7 as UM

Item
{
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string xText
    property string yText
    property string zText

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
        id: textfields

        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: snapRotationCheckbox.bottom

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
            id: xangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: xText

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.Controller.setProperty("RX", modified_text)
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    xText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    xText = 0
                }
            }
        }
        UM.TextFieldWithUnit
        {
            id: yangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: yText

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.Controller.setProperty("RY", modified_text)
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    yText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    yText = 0
                }
            }
        }
        UM.TextFieldWithUnit
        {
            id: zangleTextField
            width: UM.Theme.getSize("setting_control").width
            height: UM.Theme.getSize("setting_control").height
            unit: "degrees"
            text: zText

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.Controller.setProperty("RZ", modified_text)
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    zText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    zText = 0
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
}
