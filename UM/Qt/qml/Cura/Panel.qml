import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

Rectangle {
    property alias title: titleBarLabel.text
    property alias contents: contentItem.children

    width: childrenRect.width
    height: childrenRect.height

    MouseArea {
        //Used to filter mouse events so they do not pass into the background.
        anchors.fill: parent;

        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    }

    ColumnLayout {
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: childrenRect.height

            visible: titleBarLabel.text != ""

            gradient: Gradient 
            {
                GradientStop { position: 0 ; color: "#646464"}
                GradientStop { position: 1 ; color: "#353535" }
            }

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
