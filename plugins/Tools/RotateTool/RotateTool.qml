// Copyright (c) 2021 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import UM 1.5 as UM

Item
{
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

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

        onClicked: UM.ActiveTool.triggerAction("resetRotation")
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

        onClicked: UM.ActiveTool.triggerAction("layFlat");

        // (Not yet:) Alternative 'lay flat' when legacy OpenGL makes selection of a face in an indexed model impossible.
        // visible: ! UM.ActiveTool.properties.getValue("SelectFaceSupported");
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
        checked: UM.ActiveTool.properties.getValue("SelectFaceToLayFlatMode")
        onClicked: UM.ActiveTool.setProperty("SelectFaceToLayFlatMode", checked)

        visible: UM.ActiveTool.properties.getValue("SelectFaceSupported") == true //Might be undefined if we're switching away from the RotateTool!
    }

    UM.CheckBox
    {
        id: snapRotationCheckbox
        anchors.top: resetRotationButton.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").width

        //: Snap Rotation checkbox
        text: catalog.i18nc("@action:checkbox","Snap Rotation")

        checked: UM.ActiveTool.properties.getValue("RotationSnap")
        onClicked: UM.ActiveTool.setProperty("RotationSnap", checked)
    }

    Binding
    {
        target: snapRotationCheckbox
        property: "checked"
        value: UM.ActiveTool.properties.getValue("RotationSnap")
    }

    Binding
    {
        target: alignFaceButton
        property: "checked"
        value: UM.ActiveTool.properties.getValue("SelectFaceToLayFlatMode")
    }
}
