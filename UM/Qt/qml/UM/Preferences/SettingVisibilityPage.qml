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
        settingsListView.positionViewAtIndex(definitionsModel.getIndex(key), ListView.Beginning)
    }

    function reset()
    {
        UM.Preferences.resetPreference("general/visible_settings")
    }
    resetEnabled: true;

    function updateToggleVisibleSettings()
    {
        var typeRoleId = settingsListView.model.roleId("type");
        var visibleRoleId = settingsListView.model.roleId("visible");
        var all_visible = true;
        var all_hidden = true;
        for(var i = 0; i < settingsListView.model.rowCount(); i++) {
            var type = settingsListView.model.data(settingsListView.model.index(i,0), typeRoleId);
            var visible = settingsListView.model.data(settingsListView.model.index(i,0), visibleRoleId);
            if(type && type != "category") {
                if(visible) {
                    all_hidden = false;
                } else {
                    all_visible = false;
                }
                if(!all_hidden && !all_visible) {
                    toggleVisibleSettings.partiallyCheckedEnabled = true
                    toggleVisibleSettings.checkedState = Qt.PartiallyChecked
                    return
                }
            }
        }
        toggleVisibleSettings.partiallyCheckedEnabled = false
        if(all_visible) {
            toggleVisibleSettings.checkedState = Qt.Checked
        } else {
            toggleVisibleSettings.checkedState = Qt.Unchecked
        }
    }

    Item
    {
        id: base;
        anchors.fill: parent;

        CheckBox
        {
            id: toggleVisibleSettings
            anchors
            {
                verticalCenter: filter.verticalCenter;
                left: parent.left;
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            text: catalog.i18nc("@label:textbox", "Check all")
            checkedState: Qt.PartiallyChecked
            partiallyCheckedEnabled: true
            onClicked:
            {
                if(toggleVisibleSettings.partiallyCheckedEnabled) {
                    toggleVisibleSettings.checked = true
                    toggleVisibleSettings.partiallyCheckedEnabled = false
                }
                var keys = [];
                var keyRoleId = settingsListView.model.roleId("key")
                for(var i = 0; i < settingsListView.model.rowCount(); i++) {
                    var key = settingsListView.model.data(settingsListView.model.index(i,0), keyRoleId);
                    if(key) keys.push(key)
                }
                settingsListView.model.setVisibleBulk(keys, checked);
            }
        }

        TextField
        {
            id: filter;

            anchors
            {
                top: parent.top
                left: toggleVisibleSettings.right
                leftMargin: UM.Theme.getSize("default_margin").width
                right: parent.right
            }

            placeholderText: catalog.i18nc("@label:textbox", "Filter...")

            onTextChanged: settingsListView.model.filter = {"label": "*" + text}
        }

        ScrollView
        {
            id: scrollView

            frameVisible: true

            anchors
            {
                top: filter.bottom;
                topMargin: UM.Theme.getSize("default_margin").height
                left: parent.left;
                right: parent.right;
                bottom: parent.bottom;
            }
            ListView
            {
                id: settingsListView
                Component.onCompleted: updateToggleVisibleSettings()
                model: UM.SettingDefinitionsModel {
                    id: definitionsModel
                    containerId: "fdmprinter"
                    showAll: true
                    exclude: ["machine_settings"]
                    visibilityHandler: UM.SettingPreferenceVisibilityHandler { }
                    onSettingsVisibilityChanged: updateToggleVisibleSettings()
                }
                delegate:Loader
                {
                    id: loader

                    width: parent.width
                    height: model.type != undefined ? UM.Theme.getSize("section").height : 0

                    property var definition: model
                    property var settingDefinitionsModel: definitionsModel

                    asynchronous: true
                    active: model.type != undefined
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
