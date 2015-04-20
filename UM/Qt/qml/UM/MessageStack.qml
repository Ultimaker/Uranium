import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM
import "."

ListView {
    boundsBehavior: ListView.StopAtBounds;
    verticalLayoutDirection: ListView.BottomToTop;

    model: UM.Models.visibleMessagesModel;

    delegate: Rectangle 
    {
        width: ListView.view.width;
        height: 50;
        radius: Styles.defaultMargin;
        color: Styles.messageBackgroundColor;

        ColumnLayout 
        {
            anchors.fill: parent;
            anchors.margins: Styles.defaultMargin;

            Label { text: model.text; color: Styles.messageTextColor; Layout.fillWidth: true; }
            Button
            {
                onClicked:UM.Models.visibleMessagesModel.hideMessage(model.id)
                text: "b-gone"
                ProgressBar 
                { 
                    minimumValue: 0;
                    maximumValue: model.maximumValue; 
                    value: model.progress;
                    Layout.fillWidth: true;
                    visible: model.maximumValue != 0 ? true: false
                    
                }
            }
            //ProgressBar { minimumValue: 0; maximumValue: 100; value: model.progress; Layout.fillWidth: true; }
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
