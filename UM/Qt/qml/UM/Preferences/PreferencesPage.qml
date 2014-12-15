import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

ColumnLayout {
    property alias title: titleLabel.text;
    property alias contents: contentsItem.children;

    Label {
        id: titleLabel;
    }

    Item {
        id: contentsItem;
        Layout.fillWidth: true;
        Layout.fillHeight: true;
        clip: true;
    }
}
