// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.2 as UM

PreferencesPage
{
    title: catalog.i18nc("@title:tab", "Setting Visibility");

    property int scrollToIndex: 0

    signal scrollToSection( string key )
    onScrollToSection:
    {
        scrollToIndex = Math.max(0, settingList.model.find("id", key));
        //Delay finding the scroll offset until the scrollview has had time to fill up
        scrollToTimer.start()
    }

    function reset()
    {
        UM.Preferences.resetPreference("general/setting_visibility")
    }
    resetEnabled: true;

    Item
    {
        id: base;
        anchors.fill: parent;

        Timer
        {
            id: scrollToTimer
            interval: 1
            repeat: false
            onTriggered: scrollView.flickableItem.contentY = settingList.itemAt(scrollToIndex).mapToItem(settingList, 0, 0).y 
        }

        TextField
        {
            id: filter;

            anchors
            {
                top: parent.top;
                left: parent.left;
                right: parent.right;
            }

            placeholderText: catalog.i18nc("@label:textbox", "Filter...");

            onTextChanged: settingsListView.model.setLabelFilter(text);
        }

        ScrollView
        {
            id: scrollView

            anchors
            {
                top: filter.bottom;
                left: parent.left;
                right: parent.right;
                bottom: parent.bottom;
            }
            ListView
            {
                id: settingsListView
                model: UM.SettingDefinitionsModel { id: definitionsModel; containerId: "fdmprinter"; showAll: true; }
                delegate:Loader
                {
                    id: loader

                    width: parent.width
                    height: model.type ? UM.Theme.getSize("section").height : 0

                    property var definition: model
                    property var settingDefinitionsModel: definitionsModel

                    asynchronous: true
                    source:
                    {
                        switch(model.type)
                        {
                            case "category":
                                return "SettingVisibilityCategory.qml"
                            default:
                                return "SettingVisibilityItem.qml"
                        }
                    }
                }
            }
        }

        UM.I18nCatalog { name: "uranium"; }
        SystemPalette { id: palette; }
    }
}
