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
        spacing: UM.Theme.sizes.default_lining.height;

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
                    width: UM.Theme.sizes.sidebar.width;
                    height: UM.Theme.sizes.section.height;

                    text: model.name;
                    iconSource: UM.Theme.icons[model.icon];
                    checkable: true;

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
                }

                Button
                {
                    id: hiddenSettingsWarning

                    anchors.top: categoryHeader.bottom
                    width: categoryHeader.width

                    opacity: categoryHeader.checked && model.hiddenValuesCount > 0 ? 1 : 0
                    height: categoryHeader.checked && model.hiddenValuesCount > 0 ? UM.Theme.sizes.lineHeight : 0

                    text: catalog.i18ncp("@label", "{0} hidden setting uses a custom value", "{0} hidden settings use custom values", model.hiddenValuesCount)
                    onClicked: { UM.ActiveProfile.showHiddenValues(model.id) }

                    style: ButtonStyle
                    {
                        background: Rectangle {}
                        label: Label
                        {
                            text: control.text

                            horizontalAlignment: Text.AlignHCenter
                            font: UM.Theme.fonts.default
                            color: control.hovered? UM.Theme.colors.text_hover : UM.Theme.colors.text
                        }
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

                        delegate: UM.SettingItem
                        {
                            id: item;

                            width: UM.Theme.sizes.sidebar.width - UM.Theme.sizes.default_margin.width * 2

                            height: settingVisible ? UM.Theme.sizes.setting.height + UM.Theme.sizes.default_lining.height : 0;
                            Behavior on height { NumberAnimation { duration: 75; } }
                            opacity: settingVisible ? 1 : 0;
                            Behavior on opacity { NumberAnimation { duration: 75; } }

                            enabled: categoryHeader.checked && settingVisible;

                            property bool settingVisible: model.visible && model.enabled;

                            name: model.name;
                            description: model.description;
                            value: model.value;
                            unit: model.unit;
                            valid: model.valid;
                            depth: model.depth
                            type: model.type;
                            options: model.type == "enum" ? model.options : null;
                            key: model.key;
                            overridden: model.overridden;

                            style: UM.Theme.styles.setting_item;

                            onItemValueChanged: delegateItem.settingsModel.setSettingValue(model.key, value);
                            onContextMenuRequested: contextMenu.popup();
                            onResetRequested: delegateItem.settingsModel.resetSettingValue(model.key)

                            onShowTooltip:
                            {
                                position = Qt.point(0, item.height);
                                base.showTooltip(item, position, "<b>"+model.name+"</b><br/>"+model.description)
                            }
                            onHideTooltip: base.hideTooltip()

                            Menu
                            {
                                id: contextMenu;

                                MenuItem
                                {
                                    //: Settings context menu action
                                    text: catalog.i18nc("@action:menu","Hide this setting");
                                    onTriggered: delegateItem.settingsModel.hideSetting(model.key);
                                }
                                MenuItem
                                {
                                    //: Settings context menu action
                                    text: catalog.i18nc("@action:menu","Configure setting visiblity...");

                                    onTriggered: {
                                        preferences.visible = true;
                                        preferences.setPage(2);
                                        preferences.getCurrentItem().scrollToSection(categoryId);
                                    }
                                }
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
    }
}
