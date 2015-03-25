import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

SettingItem {
    id: base;

    control: TextField
    {
        anchors.fill: parent;
        maximumLength: 5;

        text: base.value
        onEditingFinished: base.model.settingChanged(base.index, base.key, text)
        validator: DoubleValidator { }

        style: TextFieldStyle
        {
            textColor: "black"
            background: Rectangle
            {
                implicitHeight: control.height;
                implicitWidth: control.width;
                border.width: 1
                color:  {
                    switch(base.valid)
                    {
                        case 0:
                            return "red"
                        case 1:
                            return "red"
                        case 2:
                            return "red"
                        case 3:
                            return "yellow"
                        case 4:
                            return "yellow"
                        case 5:
                            return "white"

                        default:
                            console.log(base.valid)
                            return "black"
                    }
                }

                Label {
                    anchors.right: parent.right;
                    anchors.rightMargin: UM.Styles.defaultMargin
                    anchors.verticalCenter: parent.verticalCenter;
                    text: base.unit;
                    color: "#999";
                }
            }
        }
    }
}
