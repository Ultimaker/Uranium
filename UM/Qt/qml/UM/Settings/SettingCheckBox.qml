import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

CheckBox
{
    signal valueChanged(bool value);

    checked: value //From parent loader
    onCheckedChanged: valueChanged(checked);

    style: CheckBoxStyle {
        background: Item { }
        indicator: Rectangle {
            implicitWidth:  control.height;
            implicitHeight: control.height;

            color: control.hovered ? itemStyle.controlHighlightColor : itemStyle.controlColor;
            border.width: itemStyle.controlBorderWidth;
            border.color: itemStyle.controlBorderColor;

            Label {
                anchors.centerIn: parent;
                color: itemStyle.controlTextColor;
                font: itemStyle.controlFont;

                text: "✓";

                opacity: control.checked ? 1 : 0;
                Behavior on opacity { NumberAnimation { duration: 100; } }
            }
        }
    }
}
