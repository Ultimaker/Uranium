//Copyright (c) 2022 Ultimaker B.V.
//Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.15
import QtQuick.Controls 2.15

import UM 1.5 as UM

/*
* A small dialog that shows a message, and zero or more buttons.
*
* The buttons can be set by setting the standardButtons property by
* combining zero or more standardButtons using the bitwise or ( | ) operator
* https://doc.qt.io/qt-5/qml-qtquick-controls2-dialog.html#standardButtons-prop
*
* Ordering of the buttons is determined by the buttonsModel.buttons list
* and is sorted on importance, where the "positive" button has a higher
* precidence compared to the "negative" button (e.g. "cancel" < "ok", "no" < "yes")
* The first button provided will be a Component of type primaryButton
* All following buttons will be a Component of type SecondaryButton
* Buttons fill the dialog footer from right to left
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
    id: root

    property alias text: content.text //The text to show in the body of the dialogue.

    width: UM.Theme.getSize("small_popup_dialog").width

    property alias buttonSpacing: buttonsRow.spacing
    padding: UM.Theme.getSize("default_margin").width

    // Overlay.overlay holds the "window overlay item"; the window container
    // https://doc.qt.io/qt-5/qml-qtquick-controls2-overlay.html#overlay-attached-prop
    anchors.centerIn: Overlay.overlay

    background: Rectangle
    {
        color: UM.Theme.getColor("detail_background")
    }

    header: UM.Label
    {
        text: root.title
        font: UM.Theme.getFont("medium_bold")
        topPadding: root.padding
        leftPadding: root.padding
        rightPadding: root.padding
    }

    modal: true

    contentItem: UM.Label
    {
        onLinkActivated: function(link)
        {
            Qt.openUrlExternally(link)
        }
        id: content
    }

    // the primaryButton and secondaryButtons are the components used to display the standard buttons
    // the default button (the button-action that gets actived when the return key is pressed) is rendered using the
    // primary button all other buttons are secondary buttons
    property Component primaryButton: Button
    {
        highlighted: true
        text: model.text
    }

    property Component secondaryButton: Button
    {
        text: model.text
    }

    // Change the buttonsModel in the event that the standardButtons property changes
    Connections {
        target: root
        function onStandardButtonsChanged()
        {
            buttonsModel.update();
        }
    }

    ListModel
    {
        id: buttonsModel

        // All possible buttons with i18n translated copy
        property var buttons: [
            { standardButton: Dialog.Ok, text: catalog.i18nc("@option", "OK") },
            { standardButton: Dialog.Open, text: catalog.i18nc("@option", "Open") },
            { standardButton: Dialog.Save, text: catalog.i18nc("@option", "Save") },
            { standardButton: Dialog.Cancel, text: catalog.i18nc("@option", "Cancel") },
            { standardButton: Dialog.Close, text: catalog.i18nc("@option", "Close") },
            { standardButton: Dialog.Discard, text: catalog.i18nc("@option", "Discard") },
            { standardButton: Dialog.Apply, text: catalog.i18nc("@option", "Apply") },
            { standardButton: Dialog.Reset, text: catalog.i18nc("@option", "Reset") },
            { standardButton: Dialog.RestoreDefaults, text: catalog.i18nc("@option", "Restore Defaults") },
            { standardButton: Dialog.Help, text: catalog.i18nc("@option", "Help") },
            { standardButton: Dialog.SaveAll, text: catalog.i18nc("@option", "Save All") },
            { standardButton: Dialog.Yes, text: catalog.i18nc("@option", "Yes") },
            { standardButton: Dialog.YesToAll, text: catalog.i18nc("@option", "Yes to All") },
            { standardButton: Dialog.No, text: catalog.i18nc("@option", "No") },
            { standardButton: Dialog.NoToAll, text: catalog.i18nc("@option", "No to All") },
            { standardButton: Dialog.Abort, text: catalog.i18nc("@option", "Abort") },
            { standardButton: Dialog.Retry, text: catalog.i18nc("@option", "Retry") },
            { standardButton: Dialog.Ignore, text: catalog.i18nc("@option", "Ignore") }
        ]

        Component.onCompleted: update()

        function update()
        {
            clear();

            for (let i = 0; i < buttons.length; i ++)
            {
                const button = buttons[i];
                if (root.standardButtons & button.standardButton)
                {
                    append(button);
                }
            }
        }
    }

    // map each standard button type to an action
    // https://doc.qt.io/qt-5/qml-qtquick-controls2-dialogbuttonbox.html#details
    function click(standardButton)
    {
        // close the dialog after a click event
        root.close();

        switch (standardButton)
        {
            case Dialog.Ok:
            case Dialog.Open:
            case Dialog.Save:
            case Dialog.SaveAll:
            case Dialog.Yes:
            case Dialog.YesToAll:
            case Dialog.Retry:
            case Dialog.Ignore:
                root.accepted();
                break;

            case Dialog.Cancel:
            case Dialog.Close:
            case Dialog.No:
            case Dialog.NoToAll:
            case Dialog.Abort:
                root.rejected();
                break;

            case Dialog.Discard:
                root.discarted();
                break;

            case Dialog.Apply:
                root.applied();
                break;

            case Dialog.Reset:
            case Dialog.RestoreDefaults:
                root.reset();
                break;

            case Dialog.Help:
                root.helpRequested();
                break;
        }
    }

    footer: Row
    {
        id: buttonsRow
        spacing: UM.Theme.getSize("default_margin").width
        leftPadding: root.padding
        rightPadding: root.padding
        bottomPadding: root.padding

        layoutDirection: Qt.RightToLeft
        anchors.left: parent.left
        anchors.bottom: parent.bottom

        Repeater
        {
            model: buttonsModel

            delegate: Item
            {
                height: childrenRect.height
                width: childrenRect.width

                Loader
                {
                    id: button
                    property bool isPrimary: index == 0
                    sourceComponent: isPrimary ? root.primaryButton : root.secondaryButton

                    onLoaded:
                    {
                        item.text = text;
                    }

                    Connections
                    {
                        target: root
                        function onVisibleChanged()
                        {
                            if (root.visible && button.isPrimary)
                            {
                                button.forceActiveFocus();
                            }
                        }
                    }
                }

                Keys.onReturnPressed: root.click(standardButton)

                MouseArea
                {
                    anchors.fill: parent
                    onClicked: root.click(standardButton)
                }
            }
        }
   }
}