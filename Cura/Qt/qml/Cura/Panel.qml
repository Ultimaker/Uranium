import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

Rectangle {
    property alias title: titleBarLabel.text
    property alias contents: contentItem.children

    width: childrenRect.width
    height: childrenRect.height

    ColumnLayout {
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: childrenRect.height

            visible: titleBarLabel.text != ""

            color: "black"

            Label {
                id: titleBarLabel
                anchors.centerIn: parent
                color: "white"
            }
        }

        ColumnLayout {
            id: contentItem

            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
        }
    }
}
