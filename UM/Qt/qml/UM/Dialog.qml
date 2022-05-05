// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Dialogs

import UM 1.0 as UM


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

    property int margin: screenScaleFactor * 8;
    property bool closeOnAccept: true;  // Automatically close the window when the window is "accepted" (eg using the return key)

    default property alias contents: contentItem.children;

    property alias loader: contentLoader

    property alias buttonArea: buttonRow
    property alias leftButtons: leftButtonRow.children
    property alias rightButtons: rightButtonRow.children
    property alias backgroundColor: background.color

    property real buttonSpacing: 0

    signal accepted();
    signal rejected();

    function accept() {
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

    function open() {
        base.visible = true;
    }

    Rectangle {
        id: background
        color: UM.Theme.getColor("detail_background")
        anchors.fill: parent;

        focus: base.visible;

        Keys.onEscapePressed:{
            base.reject();
        }

        Keys.onReturnPressed: {
            base.accept();
        }

        Item {
            id: contentItem;

            anchors {
                left: parent.left;
                leftMargin: base.margin;
                right: parent.right;
                rightMargin: base.margin;
                top: parent.top;
                topMargin: base.margin;
                bottom: buttonRow.top;
                bottomMargin: base.margin;
            }

            Loader
            {
                id: contentLoader
                anchors.fill: parent
                property var manager: null
            }
        }

        RowLayout {
            id: buttonRow

            anchors {
                bottom: parent.bottom
                bottomMargin: base.margin
                left: parent.left
                leftMargin: base.margin
                right: parent.right
                rightMargin: base.margin
            }
            height: childrenRect.height

            RowLayout {
                id: leftButtonRow
                Layout.alignment: Qt.AlignLeft
                spacing: base.buttonSpacing
            }

            RowLayout {
                id: rightButtonRow
                Layout.alignment: Qt.AlignRight
                spacing: base.buttonSpacing
            }
        }
    }
}
