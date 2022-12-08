import QtQuick 2.7
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

import UM 1.7 as UM

RowLayout
{
    id: root

    // alias all slider properties to the slider component
    property alias from: slider.from
    property alias handle: slider.handle
    property alias horizontal: slider.horizontal
    property alias implicitHandleHeight: slider.implicitHandleHeight
    property alias implicitHandleWidth: slider.implicitHandleWidth
    property alias live: slider.live
    property alias orientation: slider.orientation
    property alias position: slider.position
    property alias pressed: slider.pressed
    property alias snapMode: slider.snapMode
    property alias stepSize: slider.stepSize
    property alias to: slider.to
    property alias touchDragThreshold: slider.touchDragThreshold
    property alias value: slider.value
    property alias vertical: slider.vertical
    property alias visualPosition: slider.visualPosition

    property var onPressedChanged
    property alias backgroundTickCount: ticks.model

    spacing: UM.Theme.getSize("default_margin").width

    states: [
        State {
            name: "disabled"
            when: !enabled
            PropertyChanges { target: fromLabel; color: UM.Theme.getColor("text_disabled") }
            PropertyChanges { target: toLabel; color: UM.Theme.getColor("text_disabled") }
            PropertyChanges { target: handleButton; border.color: UM.Theme.getColor("background_2") }
            PropertyChanges { target: percentageBackground; color: UM.Theme.getColor("background_2") }
            PropertyChanges { target: percentageLabel; color: UM.Theme.getColor("text_disabled") }
            PropertyChanges { target: backgroundLine; color: UM.Theme.getColor("background_2") }
            PropertyChanges { target: ticks; color: UM.Theme.getColor("background_2") }
        }
    ]

    UM.Label { id: fromLabel; Layout.fillWidth: false; text: slider.from }

    Slider
    {
        id: slider

        Layout.fillWidth: true

        onPressedChanged: {
            if (typeof(root.onPressedChanged) === "function")
            {
                root.onPressedChanged(pressed);
            }
        }

        //Draw line
        background: Rectangle
        {
            id: backgroundLine
            height: UM.Theme.getSize("slider_widget_groove").height
            width: parent.width - UM.Theme.getSize("slider_widget_handle").width
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            color: UM.Theme.getColor("lining")

            Repeater
            {
                id: ticks
                anchors.fill: parent
                property var color: UM.Theme.getColor("lining")
                model: 11

                Rectangle
                {
                    id: tick
                    color: ticks.color
                    implicitWidth: UM.Theme.getSize("slider_widget_tickmarks").width
                    implicitHeight: UM.Theme.getSize("slider_widget_tickmarks").height
                    anchors.verticalCenter: parent.verticalCenter

                    x: Math.round(backgroundLine.width / (ticks.count - 1) * index - width / 2)

                    radius: Math.round(width / 2)
                }
            }
        }

        handle: Rectangle
        {
            id: handleButton
            x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
            anchors.verticalCenter: parent.verticalCenter
            implicitWidth: UM.Theme.getSize("slider_widget_handle").width
            implicitHeight: UM.Theme.getSize("slider_widget_handle").height
            radius: Math.round(width / 2)
            color: UM.Theme.getColor("main_background")
            border.color: UM.Theme.getColor("primary")
            border.width: UM.Theme.getSize("wide_lining").height
        }

        UM.PointingRectangle
        {
            id: percentageBackground
            arrowSize: UM.Theme.getSize("button_tooltip_arrow").width
            width: childrenRect.width
            height: childrenRect.height
            target: Qt.point(handleButton.x + handleButton.width / 2, handleButton.y + handleButton.height / 2)
            x: handleButton.x + Math.round((handleButton.width - width) / 2)
            y: handleButton.y - height - UM.Theme.getSize("button_tooltip_arrow").height - UM.Theme.getSize("narrow_margin").height
            color: UM.Theme.getColor("tooltip");

            UM.Label
            {
                id: percentageLabel
                text: `${slider.value}%`
                horizontalAlignment: TextInput.AlignHCenter
                leftPadding: UM.Theme.getSize("narrow_margin").width
                rightPadding: UM.Theme.getSize("narrow_margin").width
                color: UM.Theme.getColor("tooltip_text");
            }
        }
    }

    UM.Label { id: toLabel; Layout.fillWidth: false; text: slider.to }
}