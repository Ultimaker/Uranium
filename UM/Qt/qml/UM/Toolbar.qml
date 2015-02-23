import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

import "."

Rectangle {
    id: base;

    color: Theme.primaryColor;
    height: Theme.toolbarHeight;

    default property alias content: contentLayout.children;

    Rectangle {
        anchors {
            bottom: parent.bottom;
            left: parent.left;
            right: parent.right;
        }

        height: Theme.toolbarBorderSize;
        color: Theme.toolbarBorderColor;
    }

    RowLayout {
        id: contentLayout;

        anchors.fill: parent;
        spacing: 0;
    }
}
