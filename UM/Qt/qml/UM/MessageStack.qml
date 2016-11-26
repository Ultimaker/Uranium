// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.1

import UM 1.0 as UM
import "."

ListView {
    id: base
    boundsBehavior: ListView.StopAtBounds;
    verticalLayoutDirection: ListView.BottomToTop;
    visible: true

    model: UM.VisibleMessagesModel { }
    spacing: UM.Theme.getSize("default_lining").height

    interactive: false;
    delegate: Rectangle
    {
        id: message
        width: UM.Theme.getSize("message").width
        property int labelHeight: messageLabel.height + (UM.Theme.getSize("default_margin").height * 2)
        property int progressBarHeight: totalProgressBar.height + UM.Theme.getSize("default_margin").height
        property int actionButtonsHeight: actionButtons.height > 0 ? actionButtons.height + UM.Theme.getSize("default_margin").height : 0
        height:
        {
            if (model.progress == null)
            {
                return Math.max(message.labelHeight, actionButtons.y + message.actionButtonsHeight)
            }
            else
            {
                return message.labelHeight + message.progressBarHeight + message.actionButtonsHeight
            }
        }
        anchors.horizontalCenter: parent.horizontalCenter;

        color: UM.Theme.getColor("message_background")
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("message_border")

        property variant actions: model.actions;
        property variant model_id: model.id

        Label {
            id: messageLabel
            anchors {
                left: parent.left;
                leftMargin: UM.Theme.getSize("default_margin").width;

                top: model.progress != null ? parent.top : undefined;
                topMargin: UM.Theme.getSize("default_margin").width;

                right: actionButtons.left;
                rightMargin: UM.Theme.getSize("default_margin").width;

                verticalCenter: model.progress != null ? undefined : parent.verticalCenter;
                bottomMargin: UM.Theme.getSize("default_margin").width;
            }

            function getProgressText(){
                var progress = Math.floor(model.progress)
                return "%1 %2%".arg(model.text).arg(progress)
            }

            text: model.progress > 0 ? messageLabel.getProgressText() : model.text == undefined ? "" : model.text
            color: UM.Theme.getColor("message_text")
            font: UM.Theme.getFont("default")
            wrapMode: Text.Wrap;
        }

        ProgressBar
        {
            id: totalProgressBar;
            minimumValue: 0;
            maximumValue: model.max_progress;

            value: 0

            // Doing this in an explicit binding since the implicit binding breaks on occasion.
            Binding { target: totalProgressBar; property: "value"; value: model.progress }

            visible: model.progress == null ? false: true//if the progress is null (for example with the loaded message) -> hide the progressbar
            indeterminate: model.progress == -1 ? true: false //if the progress is unknown (-1) -> the progressbar is indeterminate
            style: UM.Theme.styles.progressbar

            property string backgroundColor: UM.Theme.getColor("message_progressbar_background")
            property string controlColor: UM.Theme.getColor("message_progressbar_control")

            anchors.top: messageLabel.bottom;
            anchors.topMargin: UM.Theme.getSize("default_margin").width;
            anchors.left: parent.left;
            anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        }

        Button {
            id: closeButton;
            width: UM.Theme.getSize("message_close").width;
            height: UM.Theme.getSize("message_close").height;
            anchors {
                right: parent.right;
                rightMargin: UM.Theme.getSize("default_margin").width / 2;
                top: parent.top;
                topMargin: UM.Theme.getSize("default_margin").width / 2;
            }
            UM.RecolorImage {
                anchors.fill: parent;
                sourceSize.width: width
                sourceSize.height: width
                color:
                {
                    if(closeButton.pressed)
                    {
                        return UM.Theme.getColor("message_button_active");
                    }
                    else if(closeButton.hovered)
                    {
                        return UM.Theme.getColor("message_button_hover");
                    }
                    else
                    {
                        return UM.Theme.getColor("message_button");
                    }
                }
                source: UM.Theme.getIcon("cross2")
            }

            onClicked: base.model.hideMessage(model.id)
            visible: model.dismissable
            enabled: model.dismissable
            style: ButtonStyle {
                background: Rectangle {
                    color: UM.Theme.getColor("message_background")
                }
            }
        }

        ColumnLayout
        {
            id: actionButtons;

            anchors {
                right: parent.right
                rightMargin: UM.Theme.getSize("default_margin").width
                top:
                {
                    if (totalProgressBar.visible)
                    {
                        return totalProgressBar.bottom;
                    }
                    else if (closeButton.visible)
                    {
                        return closeButton.bottom;
                    }
                    return message.top;
                }
                topMargin: UM.Theme.getSize("default_margin").height
            }

            Repeater
            {
                model: message.actions
                delegate: Button{
                    id: messageStackButton
                    onClicked: base.model.actionTriggered(message.model_id, model.action_id)
                    text: model.name
                    style: ButtonStyle {
                        background: Item{
                            property int standardWidth: UM.Theme.getSize("message_button").width
                            property int responsiveWidth: messageStackButtonText.width + UM.Theme.getSize("default_margin").width
                            implicitWidth: responsiveWidth > standardWidth ? responsiveWidth : standardWidth
                            implicitHeight: UM.Theme.getSize("message_button").height
                            Rectangle {
                                id: messageStackButtonBackground
                                width: parent.width
                                height: parent.height
                                color:
                                {
                                    if(control.pressed)
                                    {
                                        return UM.Theme.getColor("message_button_active");
                                    }
                                    else if(control.hovered)
                                    {
                                        return UM.Theme.getColor("message_button_hover");
                                    }
                                    else
                                    {
                                        return UM.Theme.getColor("message_button");
                                    }
                                }
                                Behavior on color { ColorAnimation { duration: 50; } }
                            }
                            Label {
                                id: messageStackButtonText
                                anchors.centerIn: parent
                                text: control.text
                                color:
                                {
                                    if(control.pressed)
                                    {
                                        return UM.Theme.getColor("message_button_text_active");
                                    }
                                    else if(control.hovered)
                                    {
                                        return UM.Theme.getColor("message_button_text_hover");
                                    }
                                    else
                                    {
                                        return UM.Theme.getColor("message_button_text");
                                    }
                                }
                                font: UM.Theme.getFont("default")
                            }
                        }
                        label: Label{
                            visible: false
                        }
                    }
                }
            }
        }
    }

    add: Transition {
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
