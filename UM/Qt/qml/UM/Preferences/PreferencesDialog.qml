// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1 as OldControls
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

import UM 1.5 as UM

Dialog
{
    id: base;

    title: catalog.i18nc("@title:window", "Preferences")
    minimumWidth: UM.Theme.getSize("modal_window_minimum").width
    minimumHeight: UM.Theme.getSize("modal_window_minimum").height
    width: minimumWidth
    height: minimumHeight

    property alias currentPage: pagesList.currentIndex;

    Item
    {
        id: test
        anchors.fill: parent;

        Rectangle
        {
            id: pagesListContainer
            anchors
            {
                left: parent.left
                top: parent.top
                bottom: parent.bottom
            }
            width: 7 * UM.Theme.getSize("line").width

            color: UM.Theme.getColor("main_background")
            border.width: UM.Theme.getSize("default_lining").width
            border.color: UM.Theme.getColor("default_lining")

            ListView
            {
                id: pagesList
                anchors.fill: parent
                anchors.margins: parent.border.width

                ScrollBar.vertical: UM.ScrollBar {}
                clip: true
                model: ListModel { id: configPagesModel; }
                currentIndex: 0

                delegate: Rectangle
                {
                    width: parent ? parent.width : 0
                    height: pageLabel.height

                    color: ListView.isCurrentItem ? UM.Theme.getColor("primary") : "transparent"

                    UM.Label
                    {
                        id: pageLabel
                        width: parent.width
                        text: model.name
                    }
                    MouseArea
                    {
                        anchors.fill: parent
                        onClicked:
                        {
                            pagesList.currentIndex = index;
                        }
                    }
                }

                onCurrentIndexChanged:
                {
                    stackView.replace(configPagesModel.get(currentIndex).item);
                }
            }
        }

        StackView
        {
            id: stackView
            anchors
            {
                left: pagesListContainer.right
                leftMargin: (UM.Theme.getSize("default_margin").width / 2) | 0
                top: parent.top
                bottom: parent.bottom
                right: parent.right
            }

            initialItem: Item { property bool resetEnabled: false; }

            replaceEnter: Transition
            {
                NumberAnimation
                {
                    properties: "opacity"
                    from: 0
                    to: 1
                    duration: 100
                }
            }
            replaceExit: Transition
            {
                NumberAnimation
                {
                    properties: "opacity"
                    from: 1
                    to: 0
                    duration: 100
                }
            }
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    leftButtons: OldControls.Button
    {
        id: defaultsButton
        text: catalog.i18nc("@action:button", "Defaults");
        enabled: stackView.currentItem.resetEnabled;
        onClicked: stackView.currentItem.reset();
    }

    rightButtons: OldControls.Button
    {
        id: closeButton
        text: catalog.i18nc("@action:button", "Close");
        iconName: "dialog-close";
        onClicked: base.accept();
    }

    function setPage(index)
    {
        stackView.replace(configPagesModel.get(index).item);

        base.currentPage = index
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
        insertPage(0, catalog.i18nc("@title:tab", "General"), Qt.resolvedUrl("GeneralPage.qml"));
        insertPage(1, catalog.i18nc("@title:tab", "Settings"), Qt.resolvedUrl("SettingVisibilityPage.qml"));
        base.currentPage = 0;
    }
}
