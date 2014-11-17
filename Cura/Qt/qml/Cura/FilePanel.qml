import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.2

Panel {
    title: "Files"

    contents: ColumnLayout {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400

        Button {
            Layout.fillWidth: true
            text: "Open File"
            onClicked: fileDialog.open()
        }

        TableView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TableViewColumn { role: "text" }

            headerVisible: false

            model: ListModel {
                id: fileModel
            }
        }

        Button {
            Layout.fillWidth: true
            text: "Machine"
            onClicked: messageDialog.open()
        }
    }

    FileDialog {
        id: fileDialog

        title: "Choose files"
        modality: Qt.NonModal
        selectMultiple: true

        onAccepted: {
            for(var i in fileDialog.fileUrls) {
                fileModel.append({ "text": fileDialog.fileUrls[i] })
            }
        }
    }
}
