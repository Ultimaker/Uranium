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

            delegate: ToolButton {
                text: model.name;
                iconSource: Cura.Resources.getIcon(model.icon);
                tooltip: model.name;

                checkable: true;
                checked: model.active;

                //Workaround since using ToolButton's onClicked would break the binding of the checked property, instead
                //just catch the click so we do not trigger that behaviour.
                MouseArea {
                    anchors.fill: parent;
                    onClicked: parent.checked ? Cura.Controller.setActiveTool(null) : Cura.Controller.setActiveTool(model.name);
                }
            }
        }
    }
}
