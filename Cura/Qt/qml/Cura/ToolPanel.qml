import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

Panel {
    title: "Transform"

    contents: RowLayout {
        height: 50
        width: repeat.children.length * 50

        Repeater {
            id: repeat
            model: ListModel {
                ListElement { name: "Move" }
                ListElement { name: "Rotate" }
                ListElement { name: "Scale" }
                ListElement { name: "Mirror" }
            }

            delegate: ToolButton { text: model.name }
        }
    }
}
