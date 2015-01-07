import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

ListView {
    model: UM.Models.jobsModel

    verticalLayoutDirection: ListView.BottomToTop

    delegate: Rectangle {
        width: 200
        height: 30

        Label {
            anchors.margins: 10
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            text: model.description;
        }
    }

    add: Transition {
        NumberAnimation { property: 'opacity'; from: 0.0; to: 1.0; }
    }

    remove: Transition {
        NumberAnimation { property: 'opacity'; to: 0.0; }
    }
}
