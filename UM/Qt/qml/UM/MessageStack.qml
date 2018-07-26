// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

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
    spacing: UM.Theme.getSize("message_margin").height
    
    interactive: false;
    delegate: Rectangle
    {
        id: message

        property int labelTopBottomMargin: Math.round(UM.Theme.getSize("default_margin").height / 2)
        property int labelHeight: messageLabel.height + (UM.Theme.getSize("message_inner_margin").height * 2)
        property int progressBarHeight: totalProgressBar.height + UM.Theme.getSize("default_margin").height
        property int closeButtonHeight: UM.Theme.getSize("message_close").height
        property variant actions: model.actions
        property variant model_id: model.id

        property int totalMessageHeight: {
            if (message.actions == null || message.actions.rowCount() == 0)
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

        Button {
            id: closeButton;
            width: UM.Theme.getSize("message_close").width;
            height: UM.Theme.getSize("message_close").height;

            anchors {
                right: parent.right;
                rightMargin: UM.Theme.getSize("default_margin").width;
                top: parent.top;
                topMargin: UM.Theme.getSize("default_margin").width;
            }

            UM.RecolorImage {
                anchors.fill: parent;
                sourceSize.width: width
                sourceSize.height: width
                color: UM.Theme.getColor("message_text")
                source: UM.Theme.getIcon("cross1")
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

        Label {
            id: messageTitle

            anchors {
                left: parent.left;
                leftMargin: UM.Theme.getSize("message_inner_margin").width
                right: closeButton.left
                rightMargin: UM.Theme.getSize("message_inner_margin").width
                top: closeButton.top;
                topMargin: model.title != undefined ? -Math.round(UM.Theme.getSize("default_margin").height / 4) : 0;
            }

            text: model.title == undefined ? "" : model.title
            color: UM.Theme.getColor("message_text")
            font: UM.Theme.getFont("default_bold")
            wrapMode: Text.Wrap;
        }

        Label {
            id: messageLabel

            anchors {
                left: parent.left;
                leftMargin: UM.Theme.getSize("message_inner_margin").width
                right: closeButton.left;
                top: model.progress != null ? messageTitle.bottom : messageTitle.bottom;
                topMargin: message.labelTopBottomMargin;
            }

            function getProgressText(){
                var progress = Math.floor(model.progress)
                return "%1 %2%".arg(model.text).arg(progress)
            }

            text: model.progress > 0 ? messageLabel.getProgressText() : model.text == undefined ? "" : model.text
            onLinkActivated: {
                Qt.openUrlExternally(link);
            }
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

            anchors.top: messageLabel.bottom
            anchors.topMargin: Math.round(UM.Theme.getSize("message_inner_margin").height / 2)
            anchors.left: parent.left
            anchors.leftMargin: UM.Theme.getSize("message_inner_margin").width
            anchors.right: closeButton.right
        }

        //Right aligned Action Buttons
        RowLayout
        {
            id: actionButtons;

            anchors {
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
                    var sizeOfActions = message.actions == null ? 0 : message.actions.rowCount()
                    if(sizeOfActions == 0 ){
                        return 0;
                    }

                    for(var index = 0; index < sizeOfActions; index++){
                        var actionButton = message.actions.getItem(index)

                        var alignPosition = actionButton["button_align"]

                        //ActionButtonStyle.BUTTON_ALIGN_RIGHT == 3
                        if (alignPosition == 3){
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }
                delegate: Button {
                    id: messageStackButton
                    onClicked: base.model.actionTriggered(message.model_id, modelData.action_id)
                    text: modelData.name
                    style: ButtonStyle {
                        background: Item {
                            property int standardWidth: UM.Theme.getSize("message_button").width
                            property int responsiveWidth: messageStackButtonText.width + UM.Theme.getSize("message_inner_margin").width
                            implicitWidth: responsiveWidth > standardWidth ? responsiveWidth : standardWidth
                            implicitHeight: UM.Theme.getSize("message_button").height
                            Rectangle {
                                id: messageStackButtonBackground
                                width: parent.width
                                height: parent.height
                                color:
                                {
                                    if (modelData.button_style == 0)
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
                                    else{
                                        return "transparent";
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
                                    if (modelData.button_style == 0)
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
                                    else
                                    {
                                        return UM.Theme.getColor("text");
                                    }
                                }

                                font: {
                                    if (modelData.button_style == 0)
                                        return UM.Theme.getFont("default")
                                    else
                                    {
                                        var obj = UM.Theme.getFont("default")
                                        obj.underline = true
                                        return obj
                                    }
                                }
                            }
                        }
                        label: Label{
                            visible: false
                        }
                    }
                }
            }
        }

        //Left aligned Action Buttons
        RowLayout
        {
            id: leftActionButtons;

            anchors {
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
                    var sizeOfActions = message.actions == null ? 0 : message.actions.rowCount()
                    if(sizeOfActions == 0 ){
                        return 0;
                    }

                    for(var index = 0; index < sizeOfActions; index++){
                        var actionButton = message.actions.getItem(index)

                        var alignPosition = actionButton["button_align"]

                        //ActionButtonStyle.BUTTON_ALIGN_LEFT == 2
                        if (alignPosition == 2){
                            filteredModel.push(actionButton)
                        }
                    }
                    return filteredModel
                }
                delegate: Button {
                    id: messageStackButton
                    onClicked: base.model.actionTriggered(message.model_id, modelData.action_id)
                    text: modelData.name
                    style: ButtonStyle {
                        background: Item {
                            property int standardWidth: UM.Theme.getSize("message_button").width
                            property int responsiveWidth: messageStackButtonText.width + UM.Theme.getSize("message_inner_margin").width
                            implicitWidth: responsiveWidth > standardWidth ? responsiveWidth : standardWidth
                            implicitHeight: UM.Theme.getSize("message_button").height
                            Rectangle {
                                id: messageStackButtonBackground
                                width: parent.width
                                height: parent.height
                                color:
                                {
                                    if (modelData.button_style == 0)
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
                                    else{
                                        return "transparent";
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
                                    if (modelData.button_style == 0)
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
                                    else
                                    {
                                        return UM.Theme.getColor("text");
                                    }
                                }

                                font: {
                                    if (modelData.button_style == 0)
                                        return UM.Theme.getFont("default")
                                    else
                                    {
                                        var obj = UM.Theme.getFont("default")
                                        obj.underline = true
                                        return obj
                                    }
                                }
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
