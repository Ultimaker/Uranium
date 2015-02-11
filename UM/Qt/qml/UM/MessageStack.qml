import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM
import "."

ListView {
    boundsBehavior: ListView.StopAtBounds;
    verticalLayoutDirection: ListView.BottomToTop;

    model: UM.Models.jobsModel;

    delegate: Rectangle {
        width: ListView.view.width;
        height: 50;
        radius: Theme.defaultMargin;
        color: Theme.messageBackgroundColor;

        ColumnLayout {
            anchors.fill: parent;
            anchors.margins: Theme.defaultMargin;

            Label { text: model.description; color: Theme.messageTextColor; Layout.fillWidth: true;  }

            ProgressBar { minimumValue: 0; maximumValue: 100; value: model.progress; Layout.fillWidth: true; }
        }
    }

    add: Transition {
        ParallelAnimation {
            NumberAnimation { property: 'y'; duration: 200; }
            NumberAnimation { property: 'opacity'; from: 0; to: 1; duration: 200; }
        }
    }

    displaced: Transition {
        NumberAnimation { property: 'y'; duration: 200; }
    }

    remove: Transition {
        NumberAnimation { property: 'opacity'; to: 0; duration: 200; }
    }
}
