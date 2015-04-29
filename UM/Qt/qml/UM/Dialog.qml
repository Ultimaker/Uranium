import QtQuick 2.2
import QtQuick.Window 2.1

import UM 1.0 as UM

Window {
    id: base

    modality: Qt.WindowModal;
    flags: Qt.Dialog;

    width: 640;
    height: 480;

    default property alias contents: contentItem.children;

    property alias buttons:

    Rectangle {
        id: contentItem;

        anchors.fill: parent;
        color: "pink";

        Row {
            anchors.bottom: parent.bottom;
            anchors.left: parent.left;
            anchors.right: parent.right;
        }
    }

    SystemPalette { id: palette; }
}
