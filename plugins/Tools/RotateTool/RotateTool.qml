// Copyright (c) 2019 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.15
import QtQuick.Controls 2.15

import UM 1.3 as UM

Item
{
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    XToolButton
    {
        id: resetRotationButton

        anchors.left: parent.left;

        //: Reset Rotation tool button
        xtext: catalog.i18nc("@action:button", "Reset")
        icon.source: UM.Theme.getIcon("ArrowReset");
        property bool needBorder: true

        // style: UM.Theme.styles.tool_button;
        z: 2

        onClicked: UM.ActiveTool.triggerAction("resetRotation");
    }

    XToolButton
    {
        id: layFlatButton

        anchors.left: resetRotationButton.right;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;

        //: Lay Flat tool button
        xtext: catalog.i18nc("@action:button", "Lay flat")
        icon.source: UM.Theme.getIcon("LayFlat");
        property bool needBorder: true

        // style: UM.Theme.styles.tool_button;
        z: 1

        onClicked: UM.ActiveTool.triggerAction("layFlat");

        // (Not yet:) Alternative 'lay flat' when legacy OpenGL makes selection of a face in an indexed model impossible.
        // visible: ! UM.ActiveTool.properties.getValue("SelectFaceSupported");
    }

    XToolButton
    {
        id: alignFaceButton

        anchors.left: layFlatButton.visible ? layFlatButton.right : resetRotationButton.right;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        width: visible ? UM.Theme.getIcon("LayFlatOnFace").width : 0;

        xtext: catalog.i18nc("@action:button", "Select face to align to the build plate")
        icon.source: UM.Theme.getIcon("LayFlatOnFace")
        property bool needBorder: true

        // style: UM.Theme.styles.tool_button;

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

        // style: UM.Theme.styles.checkbox;

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
