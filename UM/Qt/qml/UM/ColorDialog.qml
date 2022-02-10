import QtQuick 2.10
import QtQuick.Controls 2.2
import QtQuick.Window 2.1
import QtQuick.Layouts 1.1

import UM 1.5 as UM
import Cura 1.1 as Cura


UM.Dialog
{
    id: base

    height: UM.Theme.getSize("small_popup_dialog").height
    width: UM.Theme.getSize("small_popup_dialog").width / 1.5


    property string color: "#FFFFFF"

    margin: UM.Theme.getSize("default_margin").width
    buttonSpacing: UM.Theme.getSize("default_margin").width

    Item
    {
        anchors.fill: parent

        UM.Label
        {
            id: colorLabel
            font: UM.Theme.getFont("large")
            text: "Color Code (HEX)"
        }

        TextField
        {
            id: colorInput
            anchors.top: colorLabel.bottom
            anchors.topMargin: UM.Theme.getSize("default_margin").height
            text: base.color
            validator: RegExpValidator { regExp: /^#([a-fA-F0-9]{6})$/ }
            onTextChanged: base.color = text
        }

        Rectangle
        {
            id: swatch
            color: base.color
            anchors.leftMargin: UM.Theme.getSize("default_margin").width
            anchors {
                left: colorInput.right
                top: colorInput.top
                bottom: colorInput.bottom

            }
            width: height

        }
    }

    rightButtons:
    [
        Cura.PrimaryButton {
            id: btnOk
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
        },
        Cura.SecondaryButton {
            id: btnCancel
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.close()
        }
    ]
}