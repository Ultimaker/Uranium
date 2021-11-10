// Copyright (c) 2021 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.5 as UM

Item
{
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}
    UM.ImageButton
    {
        id: resetRotationButton

        anchors.left: parent.left;

        //: Reset Rotation tool button
        text: catalog.i18nc("@action:button", "Reset")
        imageSource: UM.Theme.getIcon("ArrowReset")
        imageWidth: UM.Theme.getSize("medium_button_icon").width
        imageHeight: UM.Theme.getSize("medium_button_icon").height
        property bool needBorder: true

        z: 2

        onClicked: UM.ActiveTool.triggerAction("resetRotation")
    }

    UM.ImageButton
    {
        id: layFlatButton

        anchors.left: resetRotationButton.right
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        //: Lay Flat tool button
        text: catalog.i18nc("@action:button", "Lay flat")
        imageSource: UM.Theme.getIcon("LayFlat")
        imageWidth: UM.Theme.getSize("medium_button_icon").width
        imageHeight: UM.Theme.getSize("medium_button_icon").height

        z: 1

        onClicked: UM.ActiveTool.triggerAction("layFlat");

        // (Not yet:) Alternative 'lay flat' when legacy OpenGL makes selection of a face in an indexed model impossible.
        // visible: ! UM.ActiveTool.properties.getValue("SelectFaceSupported");
    }

    UM.ImageButton
    {
        id: alignFaceButton

        anchors.left: layFlatButton.visible ? layFlatButton.right : resetRotationButton.right
        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        width: visible ? UM.Theme.getIcon("LayFlatOnFace").width : 0

        text: catalog.i18nc("@action:button", "Select face to align to the build plate")
        imageSource: UM.Theme.getIcon("LayFlatOnFace")

        imageWidth: UM.Theme.getSize("medium_button_icon").width
        imageHeight: UM.Theme.getSize("medium_button_icon").height
        enabled: UM.Selection.selectionCount == 1
        checked: UM.ActiveTool.properties.getValue("SelectFaceToLayFlatMode")
        onClicked: UM.ActiveTool.setProperty("SelectFaceToLayFlatMode", !checked)

        visible: UM.ActiveTool.properties.getValue("SelectFaceSupported") == true //Might be undefined if we're switching away from the RotateTool!
    }

    CheckBox
    {
        id: snapRotationCheckbox
        anchors.left: parent.left;
        anchors.top: resetRotationButton.bottom;
        anchors.topMargin: UM.Theme.getSize("default_margin").width;

        //: Snap Rotation checkbox
        text: catalog.i18nc("@action:checkbox","Snap Rotation");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.properties.getValue("RotationSnap");
        onClicked: UM.ActiveTool.setProperty("RotationSnap", checked);
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
