import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

Window {
    id: base;

    //: Preferences dialog title
    title: qsTr("Preferences")
    flags: Qt.Dialog

    width: 640;
    height: 480;

    Rectangle {
        anchors.fill: parent;
        color: palette.window;

        ColumnLayout {
            anchors.fill: parent;

            RowLayout {
                Layout.fillWidth: true;
                Layout.fillHeight: true;

                Column {
                    Layout.fillHeight: true;

                    Repeater {
                        model: configPagesModel;
                        delegate: Button {
                            width: 100
                            height: 100
                            text: qsTr(model.name);
                            onClicked: configPage.source = model.page;
                        }
                    }
                }

                Loader {
                    id: configPage;
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    source: configPagesModel.get(0).page;
                }
            }

            Item {
                height: childrenRect.height;
                Layout.fillWidth: true;

                Button {
                    //: Close preferences dialog
                    text: qsTr("Close");

                    anchors.right: parent.right;

                    onClicked: base.visible = false;
                }
            }
        }
    }

    ListModel {
        id: configPagesModel;

        //: General configuration page title
        ListElement { name: QT_TR_NOOP("General"); page: "GeneralPage.qml"; }
        //: Machine configuration page title
        ListElement { name: QT_TR_NOOP("Machine"); page: "../Settings/SettingsConfigurationPage.qml"; }
        //: Plugins configuration page title
        ListElement { name: QT_TR_NOOP("Plugins"); page: "PluginsPage.qml"; }
    }

    function setPage(index) {
        configPage.source = configPagesModel.get(index).page;
    }

    SystemPalette { id: palette; colorGroup: SystemPalette.Active }
}
