import QtQuick 2.7
import QtQuick.Controls 2.15

import UM 1.7 as UM

Slider
{
    id: slider
    //Draw line
    background: Rectangle
    {
        id: backgroundLine
        height: UM.Theme.getSize("print_setup_slider_groove").height
        width: parent.width - UM.Theme.getSize("print_setup_slider_handle").width
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        color: UM.Theme.getColor("lining")

        Repeater
        {
            id: repeater
            anchors.fill: parent
            model: 11

            Rectangle
            {
                color: UM.Theme.getColor("lining")
                implicitWidth: UM.Theme.getSize("print_setup_slider_tickmarks").width
                implicitHeight: UM.Theme.getSize("print_setup_slider_tickmarks").height
                anchors.verticalCenter: parent.verticalCenter

                x: Math.round(backgroundLine.width / (repeater.count - 1) * index - width / 2)

                radius: Math.round(width / 2)
            }
        }
    }

    handle: Rectangle
    {
        id: handleButton
        x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
        anchors.verticalCenter: parent.verticalCenter
        implicitWidth: UM.Theme.getSize("print_setup_slider_handle").width
        implicitHeight: UM.Theme.getSize("print_setup_slider_handle").height
        radius: Math.round(width / 2)
        color: UM.Theme.getColor("main_background")
        border.color: UM.Theme.getColor("primary")
        border.width: UM.Theme.getSize("wide_lining").height
    }

    UM.PointingRectangle
    {
        arrowSize: UM.Theme.getSize("button_tooltip_arrow").width
        width: childrenRect.width
        height: childrenRect.height
        target: Qt.point(handleButton.x + handleButton.width / 2, handleButton.y + handleButton.height / 2)
        x: handleButton.x + Math.round((handleButton.width - width) / 2)
        y: handleButton.y - height - UM.Theme.getSize("button_tooltip_arrow").height - UM.Theme.getSize("narrow_margin").height
        color: UM.Theme.getColor("tooltip");

        UM.Label
        {
            text: `${slider.value}%`
            horizontalAlignment: TextInput.AlignHCenter
            leftPadding: UM.Theme.getSize("narrow_margin").width
            rightPadding: UM.Theme.getSize("narrow_margin").width
            color: UM.Theme.getColor("tooltip_text");
        }
    }
}