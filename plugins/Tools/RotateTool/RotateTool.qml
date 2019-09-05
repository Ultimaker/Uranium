// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}
    Button
    {
        id: resetRotationButton

        anchors.left: parent.left;

        //: Reset Rotation tool button
        text: catalog.i18nc("@action:button","Reset")
        iconSource: UM.Theme.getIcon("rotate_reset");
        property bool needBorder: true

        style: UM.Theme.styles.tool_button;
        z: 2

        onClicked: UM.ActiveTool.triggerAction("resetRotation");
    }

    Button
    {
        id: layFlatButton

        anchors.left: resetRotationButton.right;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;

        //: Lay Flat tool button
        text: catalog.i18nc("@action:button","Lay flat")
        iconSource: UM.Theme.getIcon("rotate_layflat");
        property bool needBorder: true

        style: UM.Theme.styles.tool_button;
        z: 1

        onClicked: UM.ActiveTool.triggerAction("layFlat");
    }

    Button
    {
        id: alignFaceButton

        anchors.left: layFlatButton.right;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;

        text: catalog.i18nc("@action:button","Align selected face with bottom")
        iconSource: UM.Theme.getIcon("rotate_layflat");  // TODO!
        property bool needBorder: true

        style: UM.Theme.styles.tool_button;

        enabled: UM.Selection.hasFaceSelected;
        onClicked: CuraActions.bottomFaceSelection();

        visible: UM.ActiveTool.properties.getValue("SelectFaceSupported");
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

    CheckBox
    {
        id: selectFaceCheckbox
        anchors.left: parent.left
        anchors.top: snapRotationCheckbox.bottom;
        anchors.topMargin: UM.Theme.getSize("default_margin").width;

        text: catalog.i18nc("@action:checkbox","Select face on click");

        style: UM.Theme.styles.checkbox;

        checked: UM.Selection.faceSelectMode
        onClicked: UM.Selection.setFaceSelectMode(checked)

        visible: UM.ActiveTool.properties.getValue("SelectFaceSupported");
    }

    Binding
    {
        target: snapRotationCheckbox
        property: "checked"
        value: UM.ActiveTool.properties.getValue("RotationSnap")
    }

    Binding
    {
        target: selectFaceCheckbox
        property: "checked"
        value: UM.Selection.faceSelectMode
    }
}
