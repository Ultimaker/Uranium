// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Dialogs

import UM 1.5 as UM

Window
{
    id: base

    modality: Qt.ApplicationModal
    flags: (Qt.platform.os == "windows" ? Qt.Dialog : Qt.Window)  // <-- Ugly workaround for a bug in Windows, where the close-button doesn't show up unless we have a Dialog (but _not_ a Window).
        | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint

    minimumWidth: screenScaleFactor * 640;
    minimumHeight: screenScaleFactor * 480;
    width: minimumWidth
    height: minimumHeight

    property int margin: UM.Theme.getSize("default_margin").width
    property bool closeOnAccept: true;  // Automatically close the window when the window is "accepted" (eg using the return key)

    default property alias contents: contentItem.children;

    property alias loader: contentLoader

    property list<Item> leftButtons
    property list<Item> rightButtons
    property alias backgroundColor: background.color

    property real buttonSpacing: 0

    property Component buttonRow: RowLayout
    {
        height: childrenRect.height
        Layout.fillWidth: true

        RowLayout
        {
            Layout.alignment: Qt.AlignLeft
            spacing: base.buttonSpacing
            children: leftButtons
        }

        RowLayout
        {
            Layout.alignment: Qt.AlignRight
            spacing: base.buttonSpacing
            children: rightButtons
        }
    }

    property Component footerComponent: Item
    {
        anchors.leftMargin: base.margin
        anchors.rightMargin: base.margin
        anchors.bottomMargin: base.margin
        anchors.left: parent.left
        anchors.right: parent.right
        height: childrenRect.height + base.margin
        Loader
        {
            sourceComponent: buttonRow
            width: parent.width
            height: childrenRect.height
        }
    }

    property alias headerComponent: header.sourceComponent

    signal accepted()
    signal rejected()

    function accept()
    {
        if (base.closeOnAccept) {
            base.visible = false;
        }
        base.accepted();
    }

    function reject() {
        //If we don't have a close button we don't want to allow the user to close the window by rejecting it (escape key).
        if (base.flags & Qt.WindowCloseButtonHint)
        {
            base.visible = false;
            base.rejected();
        }
    }

    function open()
    {
        base.visible = true;
    }

    Rectangle
    {
        id: background
        anchors.fill: parent
        color: UM.Theme.getColor("main_background")
    }

    ColumnLayout
    {
        spacing: 0
        focus: base.visible
        anchors.fill: background

        Keys.onEscapePressed: base.reject()

        Keys.onReturnPressed: base.accept()

        Loader
        {
            id: header
            visible: status != Loader.Null
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: childrenRect.height
        }

        Item
        {
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width

            Item
            {
                id: contentItem

                anchors.fill: parent
                anchors.margins: base.margin

                Loader
                {
                    id: contentLoader
                    visible: status != Loader.Null
                    anchors.fill: parent
                    property var manager: null
                }
            }
        }

        Loader
        {
            id: footer
            visible: status != Loader.Null
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: childrenRect.height
            sourceComponent: footerComponent
        }
    }
}
