import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import Cura 1.0 as Cura

Panel {
    title: "Transform"

    contents: RowLayout {
        height: 50
        width: repeat.children.length * 50

        Repeater {
            id: repeat

            model: Cura.Models.toolModel

            delegate: ToolButton { text: model.name; onClicked: Cura.Controller.setActiveTool(text); }
        }
    }
}
