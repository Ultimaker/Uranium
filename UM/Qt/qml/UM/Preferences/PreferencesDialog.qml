// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

import UM 1.1 as UM

Dialog {
    id: base;

    title: catalog.i18nc("@title:window", "Preferences")
    minimumWidth: 600;
    minimumHeight: 500;

    RowLayout {
        id: test
        anchors.fill: parent;

        TableView {
            id: pagesList;

            Layout.fillHeight: true;
            Layout.preferredWidth: Screen.devicePixelRatio * 100;

            alternatingRowColors: false;
            headerVisible: false;

            model: ListModel { id: configPagesModel; }

            TableViewColumn { role: "name" }

            onClicked: configPage.source = configPagesModel.get(row).page;
        }

        Loader {
            id: configPage;
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    leftButtons: Button {
        text: catalog.i18nc("@action:button", "Defaults");
        onClicked: configPage.item.reset();
    }

    rightButtons: Button {
        text: catalog.i18nc("@action:button", "Close");
        onClicked: base.visible = false;
    }

    function setPage(index)
    {
        configPage.source = configPagesModel.get(index).page;
        pagesList.selection.clear();
        pagesList.selection.select(index);
    }

    function insertPage(index, name, icon, page)
    {
        configPagesModel.insert(index, { "name": name, "icon": icon, "page": page });
    }

    function removePage(index)
    {
        configPagesModel.remove(index)
    }

    Component.onCompleted: {
        //This uses insertPage here because ListModel is stupid and does not allow using qsTr() on elements.

        //: General configuration page title
        insertPage(0, catalog.i18nc("@title:tab", "General"), "", "GeneralPage.qml");
        //: Machine configuration page title
        insertPage(1, catalog.i18nc("@title:tab", "Machine"), "", "../Settings/SettingsConfigurationPage.qml");
        //: Plugins configuration page title
        insertPage(2, catalog.i18nc("@title:tab", "Plugins"), "", "PluginsPage.qml");
        pagesList.selection.select(0);
        configPage.source = configPagesModel.get(0).page;
    }
}
