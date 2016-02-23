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
                }

                UM.SimpleButton
                {
                    id: hiddenSettingsWarning

                    anchors.top: categoryHeader.bottom
                    width: categoryHeader.width

                    backgroundColor: UM.Theme.getColor("sidebar");

                    opacity: categoryHeader.checked && model.hiddenValuesCount > 0 ? 1 : 0
                    height: categoryHeader.checked && model.hiddenValuesCount > 0 ? UM.Theme.getSize("setting").height : 0

                    onClicked: { UM.ActiveProfile.showHiddenValues(model.id) }

                    Label {
                        anchors.fill: parent;

                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter

                        text: catalog.i18ncp("@label", "{0} hidden setting uses a custom value", "{0} hidden settings use custom values", model.hiddenValuesCount)
                        font: UM.Theme.getFont("default")
                        color: parent.hovered ? UM.Theme.getColor("text_hover") : UM.Theme.getColor("text")
                    }
                }

                Column
                {
                    id: settings;

                    anchors.top: hiddenSettingsWarning.bottom;

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

                            enabled: categoryHeader.checked && settingVisible;

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

                            Connections
                            {
                                target: item;
                                onItemValueChanged: delegateItem.settingsModel.setSettingValue(model.key, value);
                                onContextMenuRequested: { contextMenu.key = delegateItem.categoryId; contextMenu.popup(); }
                                onResetRequested: delegateItem.settingsModel.resetSettingValue(model.key);
                                onShowTooltip: base.showTooltip(settingLoader, Qt.point(0, settingLoader.height / 2), "<b>" + model.name + "</b><br/>" + model.description)
                                onHideTooltip: base.hideTooltip();
                            }
                        }
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

            MenuItem
            {
                //: Settings context menu action
                text: catalog.i18nc("@action:menu", "Hide this setting");
                onTriggered: delegateItem.settingsModel.hideSetting(key);
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
