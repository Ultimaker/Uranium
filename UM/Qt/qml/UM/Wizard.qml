// Copyright (c) 2015 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQml 2.2

import UM 1.0 as UM

UM.Dialog {
    id: rootElement
    property int currentPage: 0
    property string file
    property bool firstRun
    signal finalClicked()

    function getChosenModel(){
        for (var i = 0; i < UM.Models.addMachinesModel.rowCount(); i++) {
            if (UM.Models.addMachinesModel.getItem(i).file == rootElement.file){
                progressList.model = UM.Models.addMachinesModel.getItem(i).pages
            }
        }
    }

    minimumWidth: 600;
    minimumHeight: 500;

    RowLayout {
        anchors.fill: parent;
        SystemPalette{id: palette}

        Rectangle {
            id: wizardProgress
            visible: progressList.model.rowCount() > 1 ? true : false
            Layout.fillHeight: true;
            Layout.preferredWidth: Screen.devicePixelRatio * 150;
            color: palette.light

            Component {
                id: wizardDelegate
                Item {
                    height: childrenRect.height
                    Button {
                        id: progressButton
                        width: wizardProgress.width
                        text: title
                        style: ButtonStyle {
                            background: Rectangle {
                                border.width: 0
                                color: "transparent"
                            }
                            label: Text {
                                id: progressText
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.Wrap
                                renderType: Text.NativeRendering
                                text: control.text
                                font.underline: title == progressList.model.getItem(rootElement.currentPage).title || progressButton.hovered ? true : false
                                color: title == progressList.model.getItem(rootElement.currentPage).title ? palette.text : palette.mid
                            }
                        }
                        onClicked: {
                            for (var i = 0; i < progressList.model.rowCount(); i++) {
                                if (progressList.model.getItem(i).title == title){
                                   rootElement.currentPage = i
                                   break
                                }
                            }
                        }
                    }
                    Label {
                        id: progressArrow
                        anchors.top: progressButton.bottom
                        x: (wizardProgress.width-progressArrow.width)/2
                        text: "▼"
                        visible: title != progressList.model.getItem(progressList.model.rowCount() - 1).title ? true : false
                        color: palette.mid
                    }
                }
            }

            ListView {
                id: progressList
                property var index: 0
                model: getChosenModel()
                keyNavigationWraps: true
                delegate: wizardDelegate
                anchors.fill: parent
                anchors.top: parent.top
                anchors.topMargin: UM.Theme.sizes.default_margin.height
            }
        }

        Loader {
            id: pageLoader
            y: UM.Theme.sizes.default_margin.height
            x: wizardProgress.width + UM.Theme.sizes.default_margin.width

            function getPageSource(index){
                var page = progressList.model.getItem(index).page + '.qml'
                return UM.Resources.getPath(UM.Resources.WizardPagesLocation, page)
            }

            function getPageSource2(index){
                if (wizardModel.get(index) != undefined){
                    var page = wizardModel.get(index).page
                    return UM.Resources.getPath(UM.Resources.WizardPagesLocation, page)
                }
                else{
                    return ""
                }
            }
            source: getPageSource(rootElement.currentPage)
            onStatusChanged: pageLoader.item.title = progressList.model.getItem(rootElement.currentPage).title
        }

        Connections {
            target: pageLoader.item
            ignoreUnknownSignals: true
            onOpenFile: {
                rootElement.file = fileName
                getChosenModel()
            }
            onCloseWizard: rootElement.visible = false
        }
    }

    rightButtons: [
        Button {
            id: backButton
            //: Add Printer wizard Button: 'Back'
            text: qsTr("< Back");
            enabled: rootElement.currentPage <= 0 ? false : true
            visible: rootElement.firstRun ? false : true
            onClicked: {
                if (rootElement.currentPage > 0){
                    rootElement.currentPage -= 1
                }
            }
        },
        Button {
            id: nextButton

            text: {
                if (rootElement.currentPage < progressList.model.rowCount() - 1){
                    //: Add Printer wizard button: 'Next'
                    return qsTr("Next >")
                } else if (rootElement.currentPage == progressList.model.rowCount() - 1){
                    //: Add Printer wizard button: 'Finish'
                    return qsTr("Finish ✓")
                }
            }

            onClicked: {
                if (rootElement.currentPage < progressList.model.rowCount() - 1){
                    rootElement.currentPage += 1
                }else if (rootElement.currentPage == progressList.model.rowCount() - 1){
                    rootElement.finalClicked()
                }
            }
        },
        Button {
            id: cancelButton
            //: Add Printer wizard button: "Cancel"
            text: qsTr("Cancel X")
            onClicked: rootElement.visible = false
            visible: rootElement.firstRun ? false : true
        }
    ]
}