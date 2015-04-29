import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import UM 1.0 as UM

ColumnLayout {
    property alias title: titleLabel.text;
    property alias contents: contentsItem.children;

    function reset()
    {
    }

    Label {
        id: titleLabel;

        Layout.fillWidth: true;

        font.pointSize: 18;
    }

    Item {
        id: contentsItem;
        Layout.fillWidth: true;
        Layout.fillHeight: true;
        clip: true;
    }
}
