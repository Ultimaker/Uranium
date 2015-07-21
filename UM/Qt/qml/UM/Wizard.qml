// Copyright (c) 2015 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

UM.Dialog {
    id: base

    property string wizardName
    property bool showProgress
    property int currentPage: 0
    property alias nextButton: nextButton //this property alias is needed so the loaded pages can access the next-button -> mainly the text and behaviour of the next/finish button

    minimumWidth: 600;
    minimumHeight: 500;
    title: wizardModel.title


    RowLayout {
        anchors.fill: parent;
        SystemPalette{id: palette}

        Rectangle {
            id: wizardProgress
            visible: base.showProgress
            Layout.fillHeight: true;
            Layout.preferredWidth: Screen.devicePixelRatio * 150;
            color: palette.light

            ListModel {
                id: wizardModel

                //: Add Ultimaker Original dialog title
                property string title: "Add Ultimaker Original"

                ListElement {
                    title: "Add new Printer"
                    page: "AddMachine"
                }
                ListElement {
                    title: "Select Upgrades"
                    page: "AddOriginalPage1"
                }
                ListElement {
                    title: "Upgrade Firmware"
                    page: "AddOriginalPage2"
                }
                ListElement {
                    title: "Ultimaker Checkup"
                    page: "AddOriginalPage3"
                }
                ListElement {
                    title: "Bedleveling"
                    page: "AddOriginalPage4"
                }
            }

            Component {
                id: wizardDelegate
                Item {
                    id: test
                    height: childrenRect.height
                    Button {
                        id: progressButton
                        text: title
                        x: (wizardProgress.width-progressButton.width)/2
                        style: ButtonStyle {
                            background: Rectangle {
                                border.width: 0
                                color: "transparent"
                            }
                            label: Text {
                                id: progressText
                                renderType: Text.NativeRendering
                                text: control.text
                                font.underline: title == wizardModel.get(base.currentPage).title || progressButton.hovered ? true : false
                                //font.weight: title == wizardModel.get(base.currentPage).title ? Font.DemiBold : Font.Normal
                                //color: title == wizardModel.get(base.currentPage).title ? palette.text : UM.Theme.colors.button
                                color: title == wizardModel.get(base.currentPage).title ? palette.text : palette.mid
                            }
                        }
                        onClicked: {
                            for (var i = 0; i < wizardModel.count; i++) {
                                if (wizardModel.get(i).title == title){
                                   base.currentPage = i
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
                        visible: title != wizardModel.get(wizardModel.count - 1).title ? true : false
                        color: palette.mid
                    }
                }
            }

            ListView {
                id: progressList
                property var index: 0
                model: UM.Models.wizardModel
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
                if (base.wizardName == ''){
                    return "WizardPages/AddMachine.qml"
                }
                else {
                    return "WizardPages/" + wizardModel.get(index).page + ".qml"
                }
            }
            source: pageLoader.getPageSource(currentPage)
        }
    }

    rightButtons: [
        Button {
            id: backButton
            //: Add Printer wizard Button: 'Back'
            text: qsTr("< Back");
            visible: base.currentPage <= 0 ? false : true
            onClicked: {
                if (base.currentPage > 0){
                    base.currentPage = base.currentPage -1
                }
            }
        },
        Button {
            id: nextButton
            //: Add Printer wizard button: 'Next'

            function nextButtonText(){
                if (base.currentPage < wizardModel.count - 1){
                    //: Add Printer wizard button: 'Next'
                    return qsTr("Next >")
                } else if (base.currentPage == wizardModel.count -1){
                    //: Add Printer wizard button: 'Finish'
                    return qsTr("Finish ✓")
                }
            }

            text: nextButtonText()
            onClicked: {
                if (base.currentPage < wizardModel.count - 1){
                    base.currentPage = base.currentPage + 1
                }else if (base.currentPage == wizardModel.count - 1){
                    base.visible = false
                }
            }
        },
        Button {
            id: cancelButton
            //: Add Printer wizard button: "Cancel"
            text: qsTr("Cancel X");
            onClicked: base.visible = false;
        }
    ]
}