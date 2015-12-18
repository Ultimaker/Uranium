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

    model: UM.Models.visibleMessagesModel;

    interactive: false;
    delegate: Rectangle
    {
        id: message
        width: UM.Theme.sizes.message.width
        property int labelHeight: messageLabel.height + (UM.Theme.sizes.default_margin.height * 2)
        property int progressBarHeight: totalProgressBar.height + UM.Theme.sizes.default_margin.height
        height: model.progress == null ? message.labelHeight : message.labelHeight + message.progressBarHeight
        anchors.horizontalCenter: parent.horizontalCenter;

        color: UM.Theme.colors.message_background
        border.width: UM.Theme.sizes.default_lining.width
        border.color: UM.Theme.colors.lining

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

            function getProgressText(){
                var progress = Math.floor(model.progress)
                return "%1 <font color='black'>%2%</font>".arg(model.text).arg(progress)
            }

            text: model.progress > 0 ? messageLabel.getProgressText() : model.text == undefined ? '' : model.text
            color: UM.Theme.colors.message_text;
            font: UM.Theme.fonts.default;
            wrapMode: Text.Wrap;

            ProgressBar {
                id: totalProgressBar;
                minimumValue: 0;
                maximumValue: model.max_progress;

                value: 0

                // Doing this in an explicit binding since the implicit binding breaks on occasion.
                Binding { target: totalProgressBar; property: "value"; value: model.progress }

                visible: model.progress == null ? false: true//if the progress is null (for example with the loaded message) -> hide the progressbar
                indeterminate: model.progress == -1 ? true: false //if the progress is unknown (-1) -> the progressbar is indeterminate
                style: UM.Theme.styles.progressbar

                anchors.top: parent.bottom;
                anchors.topMargin: UM.Theme.sizes.default_margin.width;
            }
        }

        Button {
            id: closeButton;
            width: UM.Theme.sizes.message_close.width;
            height: UM.Theme.sizes.message_close.height;
            anchors {
                right: parent.right;
                rightMargin: UM.Theme.sizes.default_margin.width / 2;
                top: parent.top;
                topMargin: UM.Theme.sizes.default_margin.width / 2;
            }
            UM.RecolorImage {
                anchors.fill: parent;
                sourceSize.width: width
                sourceSize.height: width
                color: UM.Theme.colors.message_dismiss
                source: UM.Theme.icons.cross2;
            }

            onClicked: UM.Models.visibleMessagesModel.hideMessage(model.id)
            visible: model.dismissable
            enabled: model.dismissable
            style: ButtonStyle {
                background: Rectangle {
                    color: UM.Theme.colors.message_background
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
                delegate: Button{
                    id: messageStackButton
                    onClicked:UM.Models.visibleMessagesModel.actionTriggered(message.model_id, model.action_id)
                    text: model.name
                    style: ButtonStyle {
                        background: Item{
                            property int standardWidth: UM.Theme.sizes.message_button.width
                            property int responsiveWidth: messageStackButtonText.width + UM.Theme.sizes.default_margin.width
                            implicitWidth: responsiveWidth > standardWidth ? responsiveWidth : standardWidth
                            implicitHeight: UM.Theme.sizes.message_button.height
                            Rectangle {
                                id: messageStackButtonBackground
                                width: parent.width
                                height: parent.height
                                color: control.pressed ? UM.Theme.colors.button_active : 
                                       control.hovered ? UM.Theme.colors.button_hover : UM.Theme.colors.button
                                Behavior on color { ColorAnimation { duration: 50; } }
                            }
                            Label {
                                id: messageStackButtonText
                                anchors.centerIn: parent
                                text: control.text
                                color: UM.Theme.colors.button_text
                                font: UM.Theme.fonts.default
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
