// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

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
        label: Item {
            Label {
                anchors.left: parent.left;
                anchors.leftMargin: itemStyle.controlBorderWidth * 2;
                anchors.right: downArrow.left;
                anchors.rightMargin: itemStyle.controlBorderWidth;
                anchors.verticalCenter: parent.verticalCenter;

                text: control.currentText;
                font: itemStyle.controlFont;

                elide: Text.ElideRight;
                verticalAlignment: Text.AlignVCenter;
            }

            Label {
                id: downArrow;

                anchors.right: parent.right;
                anchors.rightMargin: itemStyle.controlBorderWidth * 2;
                anchors.verticalCenter: parent.verticalCenter;

                color: itemStyle.controlBorderColor;
                font: itemStyle.controlFont;

                text: "▼";
            }
        }
    }

    onCurrentIndexChanged: if (currentIndex != value) valueChanged(currentText);
}
