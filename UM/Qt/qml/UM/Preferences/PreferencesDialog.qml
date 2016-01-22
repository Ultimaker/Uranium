// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

import UM 1.1 as UM

Dialog
{
    id: base;

    title: catalog.i18nc("@title:window", "Preferences")
    minimumWidth: UM.Theme.sizes.modal_window_minimum.width;
    minimumHeight: UM.Theme.sizes.modal_window_minimum.height;

    property int currentPage: 0;

    Item
    {
        id: test
        anchors.fill: parent;

        TableView
        {
            id: pagesList;

            anchors {
                left: parent.left;
                top: parent.top;
                bottom: parent.bottom;
            }

            width: 7 * UM.Theme.sizes.line.width;

            alternatingRowColors: false;
            headerVisible: false;

            model: ListModel { id: configPagesModel; }

            TableViewColumn { role: "name" }

            onClicked:
            {
                if(base.currentPage != row)
                {
                    stackView.pop()
                    stackView.push(configPagesModel.get(row).item);
                    base.currentPage = row;
                }
            }
        }

        StackView {
            id: stackView
            anchors {
                left: pagesList.right;
                top: parent.top;
                bottom: parent.bottom;
                right: parent.right;
            }

            initialItem: Item { property bool resetEnabled: false; }

            delegate: StackViewDelegate {
                pushTransition: StackViewTransition { }
            }
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    leftButtons: Button
    {
        text: catalog.i18nc("@action:button", "Defaults");
        enabled: stackView.currentItem.resetEnabled;
        onClicked: stackView.currentItem.reset();
    }

    rightButtons: Button
    {
        text: catalog.i18nc("@action:button", "Close");
        iconName: "dialog-close";
        onClicked: base.accept();
    }

    function setPage(index)
    {
        pagesList.selection.clear();
        pagesList.selection.select(index);

        stackView.pop()
        stackView.push(configPagesModel.get(index).item);
    }

    function insertPage(index, name, item)
    {
        configPagesModel.insert(index, { "name": name, "item": item });
    }

    function removePage(index)
    {
        configPagesModel.remove(index)
    }

    function getCurrentItem(key)
    {
        return stackView.currentItem
    }

    Component.onCompleted:
    {
        //This uses insertPage here because ListModel is stupid and does not allow using qsTr() on elements.
        insertPage(0, catalog.i18nc("@title:tab", "General"), generalPage);
        insertPage(1, catalog.i18nc("@title:tab", "Settings"), settingVisibilityPage);
        insertPage(2, catalog.i18nc("@title:tab", "Printers"), machinesPage);
        insertPage(3, catalog.i18nc("@title:tab", "Profiles"), profilesPage);
        insertPage(4, catalog.i18nc("@title:tab", "Plugins"), pluginsPage);

        setPage(0)
    }

    Item
    {
        visible: false
        GeneralPage { id: generalPage }
        SettingVisibilityPage { id: settingVisibilityPage }
        MachinesPage { id: machinesPage }
        ProfilesPage { id: profilesPage }
        PluginsPage { id: pluginsPage }
    }
}
