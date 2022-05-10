import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.5 as UM

TextField
{
    id: control
    property alias unit: unitLabel.text

    selectByMouse: true
    selectedTextColor: UM.Theme.getColor("text_field_text")
    selectionColor: UM.Theme.getColor("text_selection")
    font: UM.Theme.getFont("default")
    color: UM.Theme.getColor("text")
    background: UM.UnderlineBackground
    {
        borderColor: control.activeFocus ? UM.Theme.getColor("text_field_border_active") : "transparent"
        liningColor:
        {
            if(control.activeFocus)
            {
                return UM.Theme.getColor("text_field_border_active");
            }
            if(control.hovered)
            {
                return UM.Theme.getColor("text_field_border_hovered");
            }
            return UM.Theme.getColor("border_field_light")
        }

        UM.Label
        {
            id: unitLabel
            anchors.right: parent.right
            anchors.rightMargin: UM.Theme.getSize("setting_unit_margin").width
            anchors.verticalCenter: parent.verticalCenter
            color: UM.Theme.getColor("setting_unit")
        }
    }
}