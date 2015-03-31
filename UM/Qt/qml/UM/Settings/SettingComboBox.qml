import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

ComboBox
{
    signal valueChanged(string value);

    model: options //From parent loader

    currentIndex: {
        for(var i = 0; i < options.rowCount(); ++i) {
            if(options.getItem(i).text == value /*From parent loader*/) {
                return i;
            }
        }

        return -1;
    }
    style: ComboBoxStyle {
        background: Rectangle {
            color: control.hovered ? itemStyle.controlHighlightColor : itemStyle.controlColor;
            border.width: itemStyle.controlBorderWidth;
            border.color: itemStyle.controlBorderColor;
        }
    }

    onCurrentIndexChanged: if (currentIndex != value) valueChanged(currentText);
}
