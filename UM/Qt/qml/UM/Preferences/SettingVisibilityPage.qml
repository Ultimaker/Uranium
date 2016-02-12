// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.1 as UM

PreferencesPage {
    title: catalog.i18nc("@title:tab", "Setting Visibility");

    property int scrollToIndex: 0

    signal scrollToSection( string key )
    onScrollToSection: {
        scrollToIndex = Math.max(0, settingList.model.find("id", key));
        //Delay finding the scroll offset until the scrollview has had time to fill up
        scrollToTimer.start()
    }

    function reset() {
    }
    resetEnabled: false;

    Item {
        id: base;
        anchors.fill: parent;

        Timer {
            id: scrollToTimer
            interval: 1
            repeat: false
            onTriggered: scrollView.flickableItem.contentY = settingList.itemAt(scrollToIndex).mapToItem(settingList, 0, 0).y 
        }

        TextField {
            id: filter;

            anchors {
                top: parent.top;
                left: parent.left;
                right: parent.right;
            }

            placeholderText: catalog.i18nc("@label:textbox", "Filter...");

            onTextChanged: settingCategoriesModel.filter(text);
        }

        ScrollView {
            id: scrollView

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

                    model: UM.SettingCategoriesModel { id: settingCategoriesModel; }

                    delegate: Item {
                        id: delegateItem;

                        width: base.width - UM.Theme.sizes.default_margin.width * 2;
                        height: childrenRect.height;

                        ToolButton {
                            id: categoryHeader;
                            text: model.name;
                            checkable: true;
                            width: parent.width;
                            onCheckedChanged: settingsColumn.state != "" ? settingsColumn.state = "" : settingsColumn.state = "collapsed";

                            style: ButtonStyle {
                                background: Rectangle
                                {
                                    width: control.width;
                                    height: control.height;
                                    color: control.hovered ? palette.highlight : "transparent";
                                }
                                label: Row
                                {
                                    spacing: UM.Theme.sizes.default_margin.width;
                                    Image
                                    {
                                        anchors.verticalCenter: parent.verticalCenter;
                                        source: control.checked ? UM.Theme.icons.arrow_right : UM.Theme.icons.arrow_bottom;
                                    }
                                    Label
                                    {
                                        text: control.text;
                                        font.bold: true;
                                        color: control.hovered ? palette.highlightedText : palette.text;
                                    }
                                }
                            }
                        }

                        property variant settingsModel: model.settings;

                        Column {
                            id: settingsColumn;

                            anchors.top: categoryHeader.bottom;

                            property real childrenHeight:
                            {
                                var h = 0.0;
                                for(var i in children)
                                {
                                    var item = children[i];
                                    h += children[i].height;
                                    if(item.settingVisible)
                                    {
                                        if(i > 0)
                                        {
                                            h += spacing;
                                        }
                                    }
                                }
                                return h;
                            }

                            width: childrenRect.width;
                            height: childrenHeight;

                            Repeater
                            {
                                model: delegateItem.settingsModel;

                                delegate: UM.TooltipArea
                                {
                                    x: model.depth * UM.Theme.sizes.default_margin.width;
                                    text: model.description;

                                    width: childrenRect.width;
                                    height: childrenRect.height;

                                    CheckBox
                                    {
                                        id: check

                                        text: model.name;
                                        checked: model.visible;
                                        enabled: !model.prohibited;

                                        onClicked: delegateItem.settingsModel.setSettingVisible(model.key, checked);

                                        states: State
                                        {
                                            name: "filtered";
                                            when: model.filtered;
                                            PropertyChanges { target: check; opacity: 0; height: 0; }
                                        }
                                    }
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
        SystemPalette { id: palette; }
    }
}
