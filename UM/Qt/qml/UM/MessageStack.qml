// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.3
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.1

import UM 1.5 as UM

ListView
{
    id: base
    boundsBehavior: ListView.StopAtBounds
    verticalLayoutDirection: ListView.BottomToTop

    model: UM.VisibleMessagesModel { }
    spacing: UM.Theme.getSize("default_margin").height

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
            id: control
            text: model.name
            background: Item {}
            contentItem: Label
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

    interactive: false

    delegate: Rectangle
    {
        id: message

        property variant actions: model.actions
        property variant model_id: model.id

        width: UM.Theme.getSize("message").width
        // Height is the size of the children + a margin on top & bottom.
        height: childrenRect.height + 2 * UM.Theme.getSize("default_margin").height

        anchors.horizontalCenter: parent !== null ? parent.horizontalCenter : undefined

        color: UM.Theme.getColor("message_background")
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("message_border")
        radius: UM.Theme.getSize("message_radius").width

        RowLayout
        {
            id: titleBar
            spacing: UM.Theme.getSize("default_margin").width

            anchors
            {
                top: parent.top
                left: parent.left
                right: parent.right
                margins: UM.Theme.getSize("default_margin").width
            }

            height: Math.max(messageTypeIcon.height, messageTitle.height)
            UM.StatusIcon
            {
                id: messageTypeIcon
                visible: status != UM.StatusIcon.Status.NEUTRAL
                height: visible ? UM.Theme.getSize("message_type_icon").height: 0
                width: visible ? UM.Theme.getSize("message_type_icon").height : 0
                status:
                {
                    switch (model.message_type)
                    {
                        case 0:
                            return UM.StatusIcon.Status.POSITIVE
                        case 1:
                            return UM.StatusIcon.Status.NEUTRAL
                        case 2:
                            return UM.StatusIcon.Status.WARNING
                        case 3:
                            return UM.StatusIcon.Status.ERROR
                        default:
                            return UM.StatusIcon.Status.NEUTRAL
                    }
                    return UM.StatusIcon.Status.WARNING
                }
            }

            UM.Label
            {
                id: messageTitle
                Layout.fillWidth: true

                text: model.title == undefined ? "" : model.title
                font: UM.Theme.getFont("default_bold")
                elide: Text.ElideRight
                maximumLineCount: 2
            }
            UM.SimpleButton
            {
                id: closeButton
                implicitWidth: UM.Theme.getSize("message_close").width
                implicitHeight: UM.Theme.getSize("message_close").height
                Layout.alignment: Qt.AlignTop
                onClicked: base.model.hideMessage(model.id)
                visible: model.dismissable
                enabled: model.dismissable
                color: UM.Theme.getColor("message_close")
                hoverColor: UM.Theme.getColor("message_close_hover")
                iconSource: UM.Theme.getIcon("Cancel")
            }
        }
        Column
        {
            id: imageItem
            visible: messageImage.progress == 1.0
            height: visible ? childrenRect.height: 0
            width: childrenRect.width
            spacing: UM.Theme.getSize("narrow_margin").height

            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width

                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width

                top: titleBar.bottom
                topMargin: visible ? UM.Theme.getSize("default_margin").height: 0
            }
            Image
            {
                id: messageImage
                height: UM.Theme.getSize("message_image").height
                fillMode: Image.PreserveAspectFit
                anchors
                {
                    horizontalCenter: parent.horizontalCenter
                }
                source: model.image_source
                sourceSize
                {
                    height: messageImage.height
                    width: messageImage.width
                }
                mipmap: true
            }

            UM.Label
            {
                id: imageCaption
                anchors
                {
                    horizontalCenter: messageImage.horizontalCenter
                }

                text: model.image_caption
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font: UM.Theme.getFont("large_bold")
                height: text != "" ? contentHeight : 0
                linkColor: UM.Theme.getColor("text_link")
            }
        }

        UM.Label
        {
            id: messageLabel
            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width

                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width

                top: imageItem.bottom
                topMargin: UM.Theme.getSize("default_margin").height
            }

            height: text == "" ? 0 : contentHeight

            function getProgressText()
            {
                return "%1 %2%".arg(model.text).arg(Math.floor(model.progress))
            }

            text: model.progress > 0 ? messageLabel.getProgressText() : model.text == undefined ? "" : model.text
            onLinkActivated: Qt.openUrlExternally(link)
        }

        UM.CheckBox
        {
            id: optionToggle
            anchors
            {
                top: messageLabel.bottom
                topMargin: visible ? UM.Theme.getSize("narrow_margin").height: 0
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width
            }
            text: model.option_text
            visible: text != ""
            height: visible ? undefined: 0
            checked: model.option_state
            onCheckedChanged: base.model.optionToggled(message.model_id, checked)
        }

        UM.ProgressBar
        {
            id: totalProgressBar
            value: 0

            // Doing this in an explicit binding since the implicit binding breaks on occasion.
            Binding
            {
                target: totalProgressBar
                property: "value"
                value: model.progress / model.max_progress
            }

            visible: model.progress == null ? false: true // If the progress is null (for example with the loaded message) -> hide the progressbar
            indeterminate: model.progress == -1 ? true: false //If the progress is unknown (-1) -> the progressbar is indeterminate

            anchors
            {
                top: optionToggle.bottom
                topMargin: visible ? UM.Theme.getSize("narrow_margin").height: 0

                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width

                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width
            }
        }

        RowLayout
        {
            id: actionButtons

            anchors
            {
                left: parent.left
                leftMargin: UM.Theme.getSize("narrow_margin").width
                right: parent.right
                rightMargin: UM.Theme.getSize("narrow_margin").width
                top: totalProgressBar.bottom
                topMargin: UM.Theme.getSize("narrow_margin").width
            }
            spacing: UM.Theme.getSize("narrow_margin").width

            //Left-aligned buttons.
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
                        // ActionButtonStyle.BUTTON_ALIGN_LEFT == 2
                        if (alignPosition == 2)
                        {
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }

                // Put the delegate in a loader so we can connect to it's signals.
                // We also need to use a different component based on the style of the action.
                // But since loaders can't get a size assigned by the layout, wrap that in an item to get the size of.
                delegate: Item
                {
                    id: actionButtonSize
                    Layout.maximumWidth: childrenRect.width
                    Layout.preferredWidth: 9999 //Something very high to make it scale the spacer first.
                    Layout.preferredHeight: actionButton.item.height
                    Layout.fillWidth: true
                    Loader
                    {
                        id: actionButton
                        sourceComponent:
                        {
                            if (modelData.button_style == 0)
                            {
                                return base.primaryButton
                            }
                            else if (modelData.button_style == 1)
                            {
                                return base.link
                            }
                            else if (modelData.button_style == 2)
                            {
                                return base.secondaryButton
                            }
                            return base.primaryButton // We got to use something, so use primary.
                        }
                        onLoaded:
                        {
                            item.maximumWidth = Qt.binding(function() { return parent.width; });
                        }
                        property var model: modelData
                        Connections
                        {
                            target: actionButton.item
                            function onClicked() { base.model.actionTriggered(message.model_id, modelData.action_id) }
                        }
                    }
                }
            }

            //Spacer in the middle the fills the remaining space. Causes right-aligned buttons to be aligned right!
            Item
            {
                Layout.fillWidth: true
                Layout.preferredWidth: 0
            }

            //Right-aligned buttons.
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
                        // ActionButtonStyle.BUTTON_ALIGN_RIGHT == 3
                        if (alignPosition == 3)
                        {
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }

                // Put the delegate in a loader so we can connect to it's signals.
                // We also need to use a different component based on the style of the action.
                // But since loaders can't get a size assigned by the layout, wrap that in an item to get the size of.
                delegate: Item
                {
                    id: actionButtonSize
                    Layout.maximumWidth: childrenRect.width
                    Layout.preferredWidth: 9999 //Something very high to make it scale the spacer first.
                    Layout.preferredHeight: actionButton.item.height
                    Layout.fillWidth: true
                    Loader
                    {
                        id: actionButton
                        sourceComponent:
                        {
                            if (modelData.button_style == 0)
                            {
                                return base.primaryButton
                            }
                            else if (modelData.button_style == 1)
                            {
                                return base.link
                            }
                            else if (modelData.button_style == 2)
                            {
                                return base.secondaryButton
                            }
                            return base.primaryButton // We got to use something, so use primary.
                        }
                        onLoaded:
                        {
                            item.maximumWidth = Qt.binding(function() { return parent.width; });
                        }
                        property var model: modelData
                        Connections
                        {
                            target: actionButton.item
                            function onClicked() { base.model.actionTriggered(message.model_id, modelData.action_id) }
                        }
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
