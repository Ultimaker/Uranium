// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.2
import QtQuick.Window 2.2

import UM 1.1 as UM

Item {
    id: base;

    width: 0;
    height: 0;

    property variant position: mapToItem(null, 0, 0)

    property int currentIndex;

    Item {
        id: settingsPanel;

        z: 3;

        width: childrenRect.width;
        height: childrenRect.height;

        opacity: 0;
        Behavior on opacity { NumberAnimation { } }

        Rectangle {
            id: arrow;
            width: 35;
            height: 35;
            rotation: 45;
            anchors.verticalCenter: parent.verticalCenter;
        }

        Rectangle {
            width: childrenRect.width;
            height: childrenRect.height;

            anchors.left: arrow.horizontalCenter;

            DropArea {
                anchors.fill: parent;
            }

            Column {
                spacing: UM.Theme.sizes.default_margin.width;

                UM.SettingItem {
                    width: UM.Theme.sizes.setting.width;
                    height: UM.Theme.sizes.setting.height;

                    name: catalog.i18nc("@label", "Profile")
                    type: "enum"

                    style: UM.Theme.styles.setting_item;

                    options: UM.ProfilesModel { addUseGlobal: true }

                    value: UM.ActiveTool.properties.Model.getItem(base.currentIndex).profile

                    onItemValueChanged: {
                        var item = UM.ActiveTool.properties.Model.getItem(base.currentIndex);
                        UM.ActiveTool.properties.Model.setObjectProfile(item.id, value)
                    }
                }

                Repeater {
                    id: settings;

                    model: UM.ActiveTool.properties.Model.getItem(base.currentIndex).settings

                    UM.SettingItem {
                        width: UM.Theme.sizes.setting.width;
                        height: UM.Theme.sizes.setting.height;

                        name: model.label;
                        type: model.type;
                        value: model.value;
                        description: model.description;
                        unit: model.unit;
                        valid: model.valid;

                        style: UM.Theme.styles.setting_item;

                        onItemValueChanged: {
                            settings.model.setSettingValue(model.key, value)
                        }

                        Button {
                            anchors.right: parent.right;
                            text: "x";
                            opacity: parent.hovered || hovered ? 1 : 0;
                            onClicked: UM.ActiveTool.properties.Model.removeSettingOverride(UM.ActiveTool.properties.Model.getItem(base.currentIndex).id, model.key)

                            style: ButtonStyle { }
                        }
                    }
                }

                Button {
                    text: catalog.i18nc("@action:button", "Override Profile");

                    style: ButtonStyle {
                        background: Item { }
                        label: Label {
                            text: control.text;
                            color: control.hovered ? "blue" : "black"
                        }
                    }

                    onClicked: settingPickDialog.visible = true;
                }
            }
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    Repeater {
        model: UM.ActiveTool.properties.Model;
        delegate: Button {
            x: ((model.x + 1.0) / 2.0) * UM.Application.mainWindow.width - base.position.x - width / 2
            y: -((model.y + 1.0) / 2.0) * UM.Application.mainWindow.height + (UM.Application.mainWindow.height - base.position.y) + height / 2

            width: 35;
            height: 35;

            text: "+";
            onClicked: {
                base.currentIndex = index;

                if(x < UM.Application.mainWindow.width / 2) {
                    settingsPanel.anchors.left = right;
                } else {
                    settingsPanel.anchors.right = left;
                }
                settingsPanel.anchors.verticalCenter = verticalCenter;

                settingsPanel.opacity = 1;
            }

            style: ButtonStyle {
                background: Rectangle {
                    width: control.width;
                    height: control.height;
                    radius: control.height / 2;

                    color: "white";

                    border.color: "black";
                    border.width: 1;
                }
            }
        }
    }

    UM.Dialog {
        id: settingPickDialog

        title: catalog.i18nc("@title:window", "Pick a Setting to Override")

        ScrollView {
            anchors.fill: parent;

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
                            onCheckedChanged: settingsColumn.state != "" ? settingsColumn.state = "" : settingsColumn.state = "collapsed";

                            style: ButtonStyle {
                                background: Item { }
                                label: Row {
                                    spacing: UM.Theme.sizes.default_margin.width;
                                    Label { text: control.checked ? ">" : "v"; }
                                    Label { text: control.text; font.bold: true; }
                                }
                            }
                        }

                        property variant settingsModel: model.settings;

                        visible: model.visible;

                        Column {
                            id: settingsColumn;

                            anchors.top: categoryHeader.bottom;

                            width: childrenRect.width;
                            height: childrenRect.height;
                            Repeater {
                                model: delegateItem.settingsModel;

                                delegate: ToolButton {
                                    x: model.depth * UM.Theme.sizes.default_margin.width;
                                    text: model.name;
                                    visible: model.visible;

                                    onClicked: {
                                        var object_id = UM.ActiveTool.properties.Model.getItem(base.currentIndex).id;
                                        UM.ActiveTool.properties.Model.addSettingOverride(object_id, model.key);
                                        settingPickDialog.visible = false;
                                    }
                                }
                            }

                            states: State {
                                name: "collapsed";

                                PropertyChanges { target: settingsColumn; opacity: 0; height: 0; }
                            }
                        }
                    }
                }
            }
        }

        rightButtons: [
            Button {
                text: catalog.i18nc("@action:button", "Cancel");
                onClicked: {
                    settingPickDialog.visible = false;
                }
            }
        ]
    }
}
