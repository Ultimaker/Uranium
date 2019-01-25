// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.1

import UM 1.0 as UM
import "."

ListView
{
    id: base
    boundsBehavior: ListView.StopAtBounds
    verticalLayoutDirection: ListView.BottomToTop

    model: UM.VisibleMessagesModel { }
    spacing: UM.Theme.getSize("message_margin").height

    // Messages can have actions, which are displayed by means of buttons. The message stack supports 3 styles
    // of buttons "Primary", "Secondary" and "Link" (aka; "tertiary")
    property Component primaryButton: Component
    {
        Button
        {
            text: model.name
        }
    }

    property Component secondaryButton: Component
    {
        Button
        {
            text: model.name
        }
    }

    property Component link: Component
    {
        Button
        {
            text: model.name
            style: ButtonStyle
            {
                background: Item {}

                label: Label
                {
                    text: control.text
                    font:
                    {
                        var defaultFont = UM.Theme.getFont("default")
                        defaultFont.underline = true
                        return defaultFont
                    }
                    color: UM.Theme.getColor("text_link")
                }
            }
        }
    }

    interactive: false

    delegate: Rectangle
    {
        id: message

        property int labelTopBottomMargin: Math.round(UM.Theme.getSize("default_margin").height / 2)
        property int labelHeight: messageLabel.height + (UM.Theme.getSize("message_inner_margin").height * 2)
        property int progressBarHeight: totalProgressBar.height + UM.Theme.getSize("default_margin").height
        property int closeButtonHeight: UM.Theme.getSize("message_close").height
        property variant actions: model.actions
        property variant model_id: model.id

        property int totalMessageHeight:
        {
            if (message.actions == null || message.actions.count == 0)
            {
                return message.labelHeight
            }
            return messageLabel.height + Math.max(actionButtons.height, leftActionButtons.height) + messageTitle.height + Math.round(UM.Theme.getSize("message_inner_margin").height * 1.5)
        }

        property int totalProgressBarHeight : Math.round(message.labelHeight + message.progressBarHeight + UM.Theme.getSize("default_margin").height / 2) + actionButtons.height

        width: UM.Theme.getSize("message").width
        height: (model.progress == null) ? totalMessageHeight : totalProgressBarHeight
        anchors.horizontalCenter: parent.horizontalCenter

        color: UM.Theme.getColor("message_background")
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("message_border")
        radius: UM.Theme.getSize("message_radius").width

        Button
        {
            id: closeButton
            width: UM.Theme.getSize("message_close").width
            height: UM.Theme.getSize("message_close").height

            anchors
            {
                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width
                top: parent.top
                topMargin: UM.Theme.getSize("default_margin").width
            }

            style: ButtonStyle
            {
                background: UM.RecolorImage
                {
                    width: UM.Theme.getSize("message_close").width
                    sourceSize.width: width
                    color: control.hovered ? UM.Theme.getColor("message_close_hover") : UM.Theme.getColor("message_close")
                    source: UM.Theme.getIcon("cross1")
                }

                label: Label {}
            }

            onClicked: base.model.hideMessage(model.id)
            visible: model.dismissable
            enabled: model.dismissable
        }

        Label
        {
            id: messageTitle

            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("message_inner_margin").width
                right: closeButton.left
                rightMargin: UM.Theme.getSize("message_inner_margin").width
                top: closeButton.top
                topMargin: model.title != undefined ? -Math.round(UM.Theme.getSize("default_margin").height / 4) : 0
            }

            text: model.title == undefined ? "" : model.title
            color: UM.Theme.getColor("message_text")
            font: UM.Theme.getFont("default_bold")
            wrapMode: Text.Wrap
            renderType: Text.NativeRendering
        }

        Label
        {
            id: messageLabel

            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("message_inner_margin").width
                right: closeButton.left
                top: model.progress != null ? messageTitle.bottom : messageTitle.bottom
                topMargin: message.labelTopBottomMargin;
            }

            function getProgressText()
            {
                var progress = Math.floor(model.progress)
                return "%1 %2%".arg(model.text).arg(progress)
            }

            text: model.progress > 0 ? messageLabel.getProgressText() : model.text == undefined ? "" : model.text
            onLinkActivated:
            {
                Qt.openUrlExternally(link);
            }
            color: UM.Theme.getColor("message_text")
            font: UM.Theme.getFont("default")
            wrapMode: Text.Wrap
            renderType: Text.NativeRendering
        }

        ProgressBar
        {
            id: totalProgressBar;
            minimumValue: 0;
            maximumValue: model.max_progress;

            value: 0

            // Doing this in an explicit binding since the implicit binding breaks on occasion.
            Binding { target: totalProgressBar; property: "value"; value: model.progress }

            visible: model.progress == null ? false: true //if the progress is null (for example with the loaded message) -> hide the progressbar
            indeterminate: model.progress == -1 ? true: false //if the progress is unknown (-1) -> the progressbar is indeterminate
            style: UM.Theme.styles.progressbar

            property string backgroundColor: UM.Theme.getColor("message_progressbar_background")
            property string controlColor: UM.Theme.getColor("message_progressbar_control")

            anchors.top: messageLabel.bottom
            anchors.topMargin: Math.round(UM.Theme.getSize("message_inner_margin").height / 2)
            anchors.left: parent.left
            anchors.leftMargin: UM.Theme.getSize("message_inner_margin").width
            anchors.right: closeButton.right
        }

        //Right aligned Action Buttons
        RowLayout
        {
            id: actionButtons

            anchors
            {
                right: closeButton.right
                top:
                {
                    if(model.progress != undefined)
                    {
                        return totalProgressBar.bottom
                    }
                    else
                    {
                        return messageLabel.bottom
                    }
                }
                topMargin: Math.round(UM.Theme.getSize("default_margin").width / 2)
            }

            Repeater
            {
                model:
                {
                    var filteredModel = new Array()
                    var sizeOfActions = message.actions == null ? 0 : message.actions.count
                    if(sizeOfActions == 0)
                    {
                        return 0;
                    }

                    for(var index = 0; index < sizeOfActions; index++)
                    {
                        var actionButton = message.actions.getItem(index)

                        var alignPosition = actionButton["button_align"]

                        //ActionButtonStyle.BUTTON_ALIGN_RIGHT == 3
                        if (alignPosition == 3)
                        {
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }

                // Put the delegate in a loader so we can connect to it's signals.
                // We also need to use a different component based on the style of the action.
                delegate: Loader
                {
                    id: actionButton
                    sourceComponent:
                    {
                        if (modelData.button_style == 0)
                        {
                            return base.primaryButton
                        } else if (modelData.button_style == 1)
                        {
                            return base.link
                        } else if (modelData.button_style == 2)
                        {
                            return base.secondaryButton
                        }
                        return base.primaryButton // We got to use something, so use primary.
                    }
                    property var model: modelData
                    Connections
                    {
                        target: actionButton.item
                        onClicked: base.model.actionTriggered(message.model_id, modelData.action_id)
                    }
                }
            }
        }

        //Left aligned Action Buttons
        RowLayout
        {
            id: leftActionButtons

            anchors
            {
                left: messageLabel.left
                leftMargin: -UM.Theme.getSize("message_inner_margin").width / 2
                top:
                {
                    if(model.progress != undefined)
                    {
                        return totalProgressBar.bottom
                    }
                    else
                    {
                        return messageLabel.bottom
                    }
                }
                topMargin: Math.round(UM.Theme.getSize("default_margin").width / 2)
            }

            Repeater
            {
                model:
                {
                    var filteredModel = new Array()
                    var sizeOfActions = message.actions == null ? 0 : message.actions.count
                    if(sizeOfActions == 0)
                    {
                        return 0;
                    }

                    for(var index = 0; index < sizeOfActions; index++)
                    {
                        var actionButton = message.actions.getItem(index)

                        var alignPosition = actionButton["button_align"]

                        //ActionButtonStyle.BUTTON_ALIGN_LEFT == 2
                        if (alignPosition == 2)
                        {
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }

                // Put the delegate in a loader so we can connect to it's signals.
                // We also need to use a different component based on the style of the action.
                delegate: Loader
                {
                    id: actionButton
                    sourceComponent:
                    {
                        if (modelData.button_style == 0)
                        {
                            return base.primaryButton
                        } else if (modelData.button_style == 1)
                        {
                            return base.link
                        } else if (modelData.button_style == 2)
                        {
                            return base.secondaryButton
                        }
                        return base.primaryButton // We got to use something, so use primary.
                    }
                    property var model: modelData
                    Connections
                    {
                        target: actionButton.item
                        onClicked: base.model.actionTriggered(message.model_id, modelData.action_id)
                    }
                }
            }
        }
    }

    add: Transition
    {
        NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200; }
    }

    displaced: Transition
    {
        NumberAnimation { property: "y"; duration: 200; }
    }

    remove: Transition
    {
        NumberAnimation { property: "opacity"; to: 0; duration: 200; }
    }

}
