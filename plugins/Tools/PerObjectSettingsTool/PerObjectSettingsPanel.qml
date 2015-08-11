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

    property int currentIndex;

    Rectangle {
        id: settingsPanel;

        x: 500;
        y: -500;
        width: childrenRect.width;
        height: childrenRect.height;
        opacity: 0;
        Behavior on opacity { NumberAnimation { } }

        Column {
            spacing: UM.Theme.sizes.default_margin.width;

            Row {
                Label {
                    text: "Material";
                }

                ComboBox {
                    model: materialModel;
                    currentIndex: {
                        var material = objectsModel.get(base.currentIndex).material;
                        for(var i = 0; i < materialModel.count; ++i) {
                            if(materialModel.get(i).text == material) {
                                return i;
                            }
                        }
                        return -1;
                    }

                    onActivated: UM.ActiveTool.set
//                     onActivated: objectsModel.setProperty(base.currentIndex, "material", currentText);
                }
            }

            Row {
                Label {
                    text: "Profile"
                }

                ComboBox {
                    anchors.verticalCenter: parent.verticalCenter;
                    model: UM.ProfilesModel { selectGlobal: true; }
                    textRole: "name"
                    currentIndex: {
                        var profile = objectsModel.get(base.currentIndex).profile;
                        var index = model.find("name", profile);
                        if(index == -1) {
                            return 0;
                        } else {
                            return index;
                        }
                    }
//                     onActivated: objectsModel.setProperty(base.currentIndex, "profile", currentText);
                }
            }

            Button {
                text: "+ Override Setting";
            }

            Button {
                text: "Close";
                onClicked: {
                    settingsPanel.opacity = 0;
                }
            }
        }
    }

    Repeater {
        model: UM.ActiveTool.properties.Model;
        delegate: Button {
            x: position.x;
            y: position.y;

            property variant position: mapFromItem(null, model.x + Screen.width / 2, model.y + Screen.height / 2);
            onPositionChanged: console.log(position.x, position.y);

//             property color material: materialModel.getMaterial(model.material).color;

            width: 35;
            height: 35;

            text: "+";
            onClicked: {
                base.currentIndex = index;
                settingsPanel.x = x + width;
                settingsPanel.y = (y + height / 2) - settingsPanel.height / 2;
                settingsPanel.opacity = 1;
            }

            style: ButtonStyle {
                background: Rectangle {
                    width: control.width;
                    height: control.height;
                    radius: control.height / 2;

//                     color: control.material;
                    color: "white";

                    border.color: "black";
                    border.width: 1;
                }
            }

            Component.onCompleted: console.log("Created button for " + model.id);
        }

    }

//     ListModel {
//         id: objectsModel;
//
//         ListElement {
//             x: 300;
//             y: 300;
//             material: "PLA";
//             profile: "High Quality";
//         }
//
//         ListElement {
//             x: 600;
//             y: 300;
//             material: "PVA";
//             profile: "Low Quality";
//         }
//
//         ListElement {
//             x: 600;
//             y: 600;
//             material: "UPET";
//             profile: "";
//         }
//     }

    ListModel {
        id: materialModel;

        ListElement { text: "PLA"; color: "red"; }
        ListElement { text: "PVA"; color: "green"; }
        ListElement { text: "UPET"; color: "blue"; }

        function getMaterial(name) {
            for(var i = 0; i < count; ++i) {
                if(get(i).text == name)
                    return get(i);
            }
        }
    }
}
