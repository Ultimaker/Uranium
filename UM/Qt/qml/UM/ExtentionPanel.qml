import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

Panel {
    title: ""

    contents: RowLayout {
        height: 50
        width: repeat.children.length * 50

        Repeater {
            id: repeat

            model: UM.Models.extensionModel

            delegate: ToolButton 
            {
                text: model.name;
                iconSource: UM.Resources.getIcon(model.icon);
                tooltip: model.description;

                onClicked:
                {
                    repeat.model.buttonClicked(model.name)
                }

            }
        }
    }
}
