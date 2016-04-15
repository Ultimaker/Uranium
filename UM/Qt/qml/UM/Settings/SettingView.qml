// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

ScrollView
{
    id: base;

    style: UM.Theme.styles.scrollview;
    flickableItem.flickableDirection: Flickable.VerticalFlick;

    property Action configureSettings;
    signal showTooltip(Item item, point location, string text);
    signal hideTooltip();

    property variant expandedCategories: []

    Column
    {
        id: contents
        spacing: UM.Theme.getSize("default_lining").height;

        Repeater
        {
            model: UM.SettingCategoriesModel { id: categoriesModel; }

            delegate: Item
            {
                id: delegateItem;
                width: childrenRect.width;
                height: childrenRect.height;

                visible: model.visible;

                property string categoryId: model.id;
                property variant settingsModel: model.settings;

                SidebarCategoryHeader
                {
                    id: categoryHeader;
                    activeFocusOnTab: false
                    width: UM.Theme.getSize("sidebar").width;
                    height: UM.Theme.getSize("section").height;

                    text: model.name;
                    iconSource: UM.Theme.getIcon(model.icon);
                    checkable: true;

                    property string key: model.id;

                    property bool previousChecked: false
                    checked: base.expandedCategories.indexOf(model.id) != -1;
                    onClicked:
                    {
                        var categories = base.expandedCategories;
                        if(checked)
                        {
                            categories.push(model.id);
                        }
                        else
                        {
                            categories.splice(base.expandedCategories.indexOf(model.id), 1);
                        }
                        base.expandedCategories = categories;
                    }

                    onConfigureSettingVisibility: if(base.configureSettings) base.configureSettings.trigger(categoryHeader);
                    onShowAllHidenInheritedSettings: categoriesModel.showAllHidenInheritedSettings(key)
                }

                Column
                {
                    id: settings;

                    anchors.top: categoryHeader.bottom;

                    height: childrenHeight;
                    spacing: 0;
                    opacity: 1;

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

                    Repeater
                    {
                        model: delegateItem.settingsModel;

                        delegate: Loader
                        {
                            id: settingLoader;

                            width: UM.Theme.getSize("sidebar").width - UM.Theme.getSize("default_margin").width * 2

                            property bool settingVisible: model.visible && model.enabled;
                            height: settingVisible ? UM.Theme.getSize("setting").height + UM.Theme.getSize("default_lining").height : 0;
                            Behavior on height { NumberAnimation { duration: 75; } }
                            opacity: settingVisible ? 1 : 0;
                            Behavior on opacity { NumberAnimation { duration: 75; } }

                            property bool settingEnabled: categoryHeader.checked && settingVisible && model.enabled && !model.value_unused;

                            property bool loadComplete: status == Loader.Ready

                            asynchronous: true;

                            source: Qt.resolvedUrl("SettingItem.qml");

                            onLoaded:
                            {
                                item.name = model.name;
                                item.unit = model.unit;
                                item.depth = model.depth;
                                item.type = model.type;
                                item.key = model.key;
                                item.visible_depth = model.visible_depth
                                item.style = UM.Theme.styles.setting_item;

                                if(model.type == "enum")
                                {
                                    item.options = model.options;
                                }

                            }

                            Binding
                            {
                                when: loadComplete
                                target: item;
                                property: "valid"
                                value: model.valid
                            }

                            Binding
                            {
                                when: loadComplete
                                target: item;
                                property: "visible_depth"
                                value: model.visible_depth
                            }

                            Binding
                            {
                                when: loadComplete
                                target: item
                                property: "value"
                                value: model.value
                            }

                            Binding
                            {
                                when: loadComplete
                                target: item
                                property: "overridden"
                                value: model.overridden
                            }
                            Binding
                            {
                                when: loadComplete
                                target: item
                                property: "has_inherit_function"
                                value: model.has_inherit_function
                            }

                            Binding
                            {
                                when: loadComplete
                                target: item
                                property: "has_profile_value"
                                value: model.has_profile_value
                            }

                            Connections
                            {
                                target: item;
                                onItemValueChanged: delegateItem.settingsModel.setSettingValue(model.key, value);
                                onContextMenuRequested: {
                                    contextMenu.key = model.key;
                                    contextMenu.settingsModel = delegateItem.settingsModel;
                                    contextMenu.popup();

                                }
                                onResetRequested: delegateItem.settingsModel.resetSettingValue(model.key);
                                onResetToDefaultRequested: delegateItem.settingsModel.forceSettingValueToDefault(model.key);
                                onShowTooltip:
                                {
                                    var content = "<b>" + model.name + "</b><br/>" + model.description

                                    var required_by_content = delegateItem.settingsModel.getRequiredBySettingString(model.key);
                                    if(required_by_content.length > 0)
                                    {
                                        content += "<i><br/>" + catalog.i18nc("@label", "Affects:") + "<br/></i>" + required_by_content
                                    }
                                    var required_content = delegateItem.settingsModel.getRequiredSettingString(model.key);
                                    if (required_content.length > 0)
                                    {
                                        content += "<i><br/>" + catalog.i18nc("@label", "Is affected by:") + "<br/></i>" + required_content
                                    }

                                    base.showTooltip(settingLoader, Qt.point(0, settingLoader.height / 2), content);
                                }
                                onHideTooltip: base.hideTooltip();
                                onShowResetTooltip: base.showTooltip(settingLoader, Qt.point(0, settingLoader.height / 2), catalog.i18nc("@label", "This setting has a value that is different from the profile.\n\nClick to restore the value of the profile."))
                                onShowInheritanceTooltip: base.showTooltip(settingLoader, Qt.point(0, settingLoader.height / 2), catalog.i18nc("@label", "This setting is normally calculated, but it currently has an absolute value set.\n\nClick to restore the calculated value."))
                            }
                        }
                    }
                    Connections
                    {
                        target: categoryHeader
                        onHideTooltip: base.hideTooltip();
                        onShowTooltip: base.showTooltip(categoryHeader, Qt.point(0, categoryHeader.height / 2),  catalog.i18nc("@label","Some hidden settings use values different from their normal calculated value.\n\nClick to make these settings visible."))
                    }
                    states: State
                    {
                        name: "collapsed";
                        when: !categoryHeader.checked;

                        PropertyChanges
                        {
                            target: settings;
                            opacity: 0;
                            height: 0;
                            anchors.topMargin: 0;
                        }
                    }

                    transitions: Transition
                    {
                        to: "collapsed";
                        reversible: true;
                        enabled: !categoriesModel.resetting;
                        SequentialAnimation
                        {
                            NumberAnimation { property: "opacity"; duration: 75; }
                            ParallelAnimation
                            {
                                NumberAnimation { property: "height"; duration: 75; }
                                //NumberAnimation { property: "anchors.topMargin"; duration: 75; }
                            }
                        }
                    }
                }
            }
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }

        Menu
        {
            id: contextMenu;

            property string key;
            property variant settingsModel;

            MenuItem
            {
                //: Settings context menu action
                text: catalog.i18nc("@action:menu", "Hide this setting");
                onTriggered: contextMenu.settingsModel.hideSetting(contextMenu.key);
            }
            MenuItem
            {
                //: Settings context menu action
                text: catalog.i18nc("@action:menu", "Configure setting visiblity...");

                onTriggered: if(base.configureSettings) base.configureSettings.trigger(contextMenu);
            }
        }
    }
}
