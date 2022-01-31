import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.5 as UM

TextField
{
    id: control
    property alias unit: unitLabel.text

    selectByMouse: true

    background: Rectangle
    {

        border.width: UM.Theme.getSize("default_lining").width
        border.color: control.hovered ? UM.Theme.getColor("setting_control_border_highlight") : UM.Theme.getColor("setting_control_border")
        radius: UM.Theme.getSize("setting_control_radius").width

        color: UM.Theme.getColor("setting_validation_ok")

        UM.Label
        {
            id: unitLabel
            anchors.right: parent.right
            anchors.rightMargin: UM.Theme.getSize("setting_unit_margin").width
            color: UM.Theme.getColor("setting_unit")
        }
    }
}