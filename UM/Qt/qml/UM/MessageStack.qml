// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.1

import UM 1.0 as UM
import "."

ListView {
    boundsBehavior: ListView.StopAtBounds;
    verticalLayoutDirection: ListView.BottomToTop;

    model: UM.Models.visibleMessagesModel;

    interactive: false;

    delegate: UM.AngledCornerRectangle
    {
        id: message
        width: UM.Theme.sizes.message.width
        property int labelHeight: messageLabel.height + (UM.Theme.sizes.default_margin.height * 2)
        property int progressBarHeight: totalProgressBar.height + UM.Theme.sizes.default_margin.height
        height: model.progress == null ? message.labelHeight : message.labelHeight + message.progressBarHeight
        cornerSize: UM.Theme.sizes.default_margin.width;

        anchors.horizontalCenter: parent.horizontalCenter;

        color: UM.Theme.colors.message

        property variant actions: model.actions;
        property variant model_id: model.id

        Label {
            id: messageLabel
            anchors {
                left: parent.left;
                leftMargin: UM.Theme.sizes.default_margin.width;

                top: model.progress != null ? parent.top : undefined;
                topMargin: UM.Theme.sizes.default_margin.width;

                right: actionButtons.left;
                rightMargin: UM.Theme.sizes.default_margin.width;

                verticalCenter: model.progress != null ? undefined : parent.verticalCenter;
                bottomMargin: UM.Theme.sizes.default_margin.width;
            }

            text: model.text;
            color: UM.Theme.colors.message_text;
            font: UM.Theme.fonts.default;
            wrapMode: Text.Wrap;

            ProgressBar {
                id: totalProgressBar;

                minimumValue: 0;
                maximumValue: model.max_progress;
                value: model.progress == null ? 0 : model.progress

                visible: model.progress == null ? false: true//if the progress is null (for example with the loaded message) -> hide the progressbar
                indeterminate: model.progress == -1 ? true: false //if the progress is unknown (-1) -> the progressbar is indeterminate
                style: UM.Theme.styles.progressbar

                anchors.top: parent.bottom;
                anchors.horizontalCenter: parent.horizontalCenter;
                anchors.topMargin: UM.Theme.sizes.default_margin.width;
                anchors.bottomMargin: UM.Theme.sizes.default_margin.width;
            }
        }

        ToolButton
        {
            id: closeButton;

            anchors {
                right: parent.right;
                top: parent.top;
            }

            width: UM.Theme.sizes.message_close.width;
            height: UM.Theme.sizes.message_close.height;

            text: "x"
            onClicked: UM.Models.visibleMessagesModel.hideMessage(model.id)
            visible: model.dismissable
            enabled: model.dismissable
            style: ButtonStyle {
                background: Rectangle {
                    color: control.hovered ? UM.Theme.colors.primary : "transparent";
                }
            }
        }

        ColumnLayout
        {
            id: actionButtons;

            anchors {
                right: parent.right;
                rightMargin: UM.Theme.sizes.default_margin.width * 2;
                verticalCenter: parent.verticalCenter;
            }

            Repeater
            {
                model: message.actions
                delegate: ToolButton
                {
                    text: model.name

                    style: ButtonStyle {
                        background: Rectangle {
                            color: control.hovered ? UM.Theme.colors.primary_hover : UM.Theme.colors.primary;
                        }
                        label: Label {
                            text: control.text;
                            color: UM.Theme.colors.primary_text;
                        }
                    }

                    onClicked:UM.Models.visibleMessagesModel.actionTriggered(message.model_id, model.action_id)
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
