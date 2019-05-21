// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

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
    minimumWidth: UM.Theme.getSize("modal_window_minimum").width
    minimumHeight: UM.Theme.getSize("modal_window_minimum").height
    width: minimumWidth
    height: minimumHeight

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

            width: 7 * UM.Theme.getSize("line").width;

            alternatingRowColors: false;
            headerVisible: false;

            model: ListModel { id: configPagesModel; }

            TableViewColumn { role: "name" }

            onClicked:
            {
                if(base.currentPage != row)
                {
                    stackView.replace(configPagesModel.get(row).item);
                    base.currentPage = row;
                }
            }
        }

        StackView {
            id: stackView
            anchors {
                left: pagesList.right
                leftMargin: (UM.Theme.getSize("default_margin").width / 2) | 0
                top: parent.top
                bottom: parent.bottom
                right: parent.right
            }

            initialItem: Item { property bool resetEnabled: false; }

            delegate: StackViewDelegate
            {
                function transitionFinished(properties)
                {
                    properties.exitItem.opacity = 1
                }

                pushTransition: StackViewTransition
                {
                    PropertyAnimation
                    {
                        target: enterItem
                        property: "opacity"
                        from: 0
                        to: 1
                        duration: 100
                    }
                    PropertyAnimation
                    {
                        target: exitItem
                        property: "opacity"
                        from: 1
                        to: 0
                        duration: 100
                    }
                }
            }
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    leftButtons: Button
    {
        id: defaultsButton
        text: catalog.i18nc("@action:button", "Defaults");
        enabled: stackView.currentItem.resetEnabled;
        onClicked: stackView.currentItem.reset();
    }

    rightButtons: Button
    {
        id: closeButton
        text: catalog.i18nc("@action:button", "Close");
        iconName: "dialog-close";
        onClicked: base.accept();
    }

    function setPage(index)
    {
        pagesList.selection.clear();
        pagesList.selection.select(index);

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

        setPage(0)
    }
}
