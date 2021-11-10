import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.0 as UM

TextField
{
    id: control
    property alias unit: unitLabel.text
    background: Rectangle
    {

        border.width: UM.Theme.getSize("default_lining").width
        border.color: control.hovered ? UM.Theme.getColor("setting_control_border_highlight") : UM.Theme.getColor("setting_control_border")
        radius: UM.Theme.getSize("setting_control_radius").width

        color: UM.Theme.getColor("setting_validation_ok")

        Label
        {
            id: unitLabel
            anchors.right: parent.right
            anchors.rightMargin: UM.Theme.getSize("setting_unit_margin").width
            anchors.verticalCenter: parent.verticalCenter
            color: UM.Theme.getColor("setting_unit")
            font: UM.Theme.getFont("default")
            renderType: Text.NativeRendering
        }
    }
}