// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.1 as UM

PreferencesPage {
    title: catalog.i18nc("@title:tab", "Setting Visibility");

    function reset() {
    }

    Item {
        anchors.fill: parent;
        TextField {
            id: filter;

            anchors {
                top: parent.top;
                left: parent.left;
                right: parent.right;
            }

            placeholderText: catalog.i18nc("@label", "Filter...");
        }

        ScrollView {
            anchors {
                top: filter.bottom;
                left: parent.left;
                right: parent.right;
                bottom: parent.bottom;
            }

            Column {
                width: childrenRect.width;
                height: childrenRect.height;

                Repeater {
                    id: settingList;

                    model: UM.SettingCategoriesModel { }

                    delegate: Item {
                        id: delegateItem;

                        width: childrenRect.width;
                        height: childrenRect.height;

                        ToolButton {
                            id: categoryHeader;
                            text: model.name;
                            checkable: true;
                            onClicked: settingsColumn.state != "" ? settingsColumn.state = "" : settingsColumn.state = "collapsed";

                            style: ButtonStyle {
                                background: Item { }
                                label: Row {
                                    spacing: UM.Theme.sizes.default_margin.width;
                                    Label { text: control.checked ? ">" : "v"; }
                                    Label { text:  control.text; font.bold: true; }
                                }
                            }
                        }

                        property variant settingsModel: model.settings;

                        Column {
                            id: settingsColumn;

                            anchors.top: categoryHeader.bottom;

                            width: childrenRect.width;
                            height: childrenRect.height;
                            Repeater {
                                model: delegateItem.settingsModel;

                                delegate: CheckBox {
                                    x: model.depth * UM.Theme.sizes.default_margin.width;
                                    text: model.name;
                                    checked: model.visible;

                                    onClicked: delegateItem.settingsModel.setSettingVisible(model.key, checked);
                                }
                            }

                            states: State {
                                name: "collapsed";

                                PropertyChanges { target: settingsColumn; opacity: 0; height: 0; }
                            }

                            transitions: Transition {
                                to: "collapsed";
                                SequentialAnimation {
                                    NumberAnimation { property: "opacity"; duration: 75; }
                                    NumberAnimation { property: "height"; duration: 75; }
                                }
                            }
                        }
                    }
                }
            }
        }

        UM.I18nCatalog { name: "uranium"; }
    }
}
