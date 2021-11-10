import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.0 as UM

CheckBox
{
    id: control

    indicator: Rectangle
    {
        implicitWidth:  UM.Theme.getSize("checkbox").width
        implicitHeight: UM.Theme.getSize("checkbox").height

        color: (control.hovered || control._hovered) ? UM.Theme.getColor("checkbox_hover") : (control.enabled ? UM.Theme.getColor("checkbox") : UM.Theme.getColor("checkbox_disabled"))
        Behavior on color { ColorAnimation { duration: 50; } }

        radius: control.exclusiveGroup ? Math.round(UM.Theme.getSize("checkbox").width / 2) : UM.Theme.getSize("checkbox_radius").width
        anchors.verticalCenter: parent.verticalCenter
        border.width: UM.Theme.getSize("default_lining").width
        border.color: (control.hovered || control._hovered) ? UM.Theme.getColor("checkbox_border_hover") : UM.Theme.getColor("checkbox_border")

        UM.RecolorImage
        {
            anchors.centerIn: parent
            width: Math.round(parent.width / 2.5)
            height: Math.round(parent.height / 2.5)

            sourceSize.height: width
            color: UM.Theme.getColor("checkbox_mark")
            source: control.exclusiveGroup ? UM.Theme.getIcon("Dot") : UM.Theme.getIcon("Check")
            opacity: control.checked
            Behavior on opacity { NumberAnimation { duration: 100; } }
        }
    }
    contentItem: Label
    {
        text: control.text
        height: contentHeight
        color: UM.Theme.getColor("checkbox_text")
        font: UM.Theme.getFont("default")
        elide: Text.ElideRight
        renderType: Text.NativeRendering
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width
    }
}