import QtQuick 2.2
import QtQuick.Window 2.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

Window {
    id: base

    modality: Qt.WindowModal;
    flags: Qt.Dialog;

    width: 640;
    height: 480;

    property int margin: Screen.pixelDensity * 2;

    default property alias contents: contentItem.children;

    property alias buttons: buttonRow.children;

    Rectangle {
        anchors.fill: parent;
        color: palette.window;

        Item {
            id: contentItem;

            anchors {
                left: parent.left;
                leftMargin: base.margin;
                right: parent.right;
                rightMargin: base.margin;
                top: parent.top;
                topMargin: base.margin;
                bottom: buttonRow.top;
                bottomMargin: base.margin;
            }
        }

        RowLayout {
            id: buttonRow;

            anchors {
                bottom: parent.bottom;
                bottomMargin: base.margin;
                left: parent.left;
                leftMargin: base.margin;
                right: parent.right;
                rightMargin: base.margin;
            }
            height: childrenRect.height;

            Item { Layout.fillWidth: true; }
        }
    }

    SystemPalette { id: palette; }
}
