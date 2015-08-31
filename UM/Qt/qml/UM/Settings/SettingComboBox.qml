// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

//import ".." as UM
import UM 1.1 as UM

ComboBox
{
    signal valueChanged(string value);
    id: base
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
            color:
            {
                if(control.hovered || base.activeFocus)
                {
                    return itemStyle.controlHighlightColor
                }
                else
                {
                    return itemStyle.controlColor
                }
            }
            border.width: itemStyle.controlBorderWidth;
            border.color: itemStyle.controlBorderColor;
        }
        label: Item {
            Label {
                anchors.left: parent.left;
                anchors.leftMargin: itemStyle.controlBorderWidth
                anchors.right: downArrow.left;
                anchors.rightMargin: itemStyle.controlBorderWidth;
                anchors.verticalCenter: parent.verticalCenter;

                text: control.currentText;
                font: itemStyle.controlFont;
                color: itemStyle.controlTextColor;

                elide: Text.ElideRight;
                verticalAlignment: Text.AlignVCenter;
            }

            UM.RecolorImage {
                id: downArrow
                anchors.right: parent.right;
                anchors.rightMargin: itemStyle.controlBorderWidth * 2;
                anchors.verticalCenter: parent.verticalCenter;

                source: UM.Theme.icons.arrow_bottom
                width: UM.Theme.sizes.standard_arrow.width
                height: UM.Theme.sizes.standard_arrow.height
                sourceSize.width: width + 5
                sourceSize.height: width + 5

                color: itemStyle.controlTextColor;

            }
        }
    }

    onCurrentIndexChanged: if (currentIndex != value) valueChanged(currentText);
}
