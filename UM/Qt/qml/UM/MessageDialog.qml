//Copyright (c) 2022 Ultimaker B.V.
//Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick.Controls 2.15

import UM 1.5 as UM

/*
 * A small dialog that shows a message to the user, and provides several options on how to proceed.
 *
 * This functions as a normal dialog with its standard buttons, but also allows defining a text to show in the dialog.
 */
Dialog
{
    /*
    Other properties you might want to set from Dialog itself:
    - title
    - standardButtons
    - onAccepted
    - onRejected
    */
    property alias text: content.text //The text to show in the body of the dialogue.

    width: UM.Theme.getSize("small_popup_dialog").width

    // Overlay.overlay holds the "window overlay item"; the window container
    // https://doc.qt.io/qt-5/qml-qtquick-controls2-overlay.html#overlay-attached-prop
    anchors.centerIn: Overlay.overlay

    modal: true

    contentItem: UM.Label
    {
        onLinkActivated: function (link)
        {
            Qt.openUrlExternally(link)
        }
        id: content
    }
}