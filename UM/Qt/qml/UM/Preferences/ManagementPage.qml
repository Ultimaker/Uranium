// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage
{
    id: base;

    property alias model: objectList.model;
    property string nameRole: "name";
    property bool detailsVisible: true;

    property variant objectList: objectList;
    property variant currentItem: objectList.currentItem != null ? objectList.model.getItem(objectList.currentIndex) : null;
    property string scrollviewCaption: "";

    default property alias details: detailsPane.children;

    signal itemActivated();
    signal addObject();
    signal removeObject();
    signal renameObject();

    property alias addEnabled: addButton.enabled;
    property alias removeEnabled: removeButton.enabled;
    property alias renameEnabled: renameButton.enabled;

    property alias buttons: buttons.children;

    property alias addText: addButton.text;

    resetEnabled: false;

    Row
    {
        id: buttons;

        width: childrenRect.width;
        height: childrenRect.height;

        Button
        {
            id: addButton;
            text: catalog.i18nc("@action:button", "Add");
            iconName: "list-add";
            onClicked: base.addObject();
        }
        Button
        {
            id: removeButton;
            text: catalog.i18nc("@action:button", "Remove");
            iconName: "list-remove";
            onClicked: base.removeObject();
        }
        Button
        {
            id: renameButton;
            text: catalog.i18nc("@action:button", "Rename");
            iconName: "edit-rename";
            onClicked: base.renameObject();
        }
    }

    Item
    {
        anchors
        {
            top: buttons.bottom;
            topMargin: UM.Theme.sizes.default_margin.height;
            left: parent.left;
            right: parent.right;
            bottom: parent.bottom;
        }

        Label
        {
            id: captionLabel
            anchors 
            {
                top: parent.top;
                left: parent.left;
            }
            visible: scrollviewCaption != ""
            text: scrollviewCaption
        }

        ScrollView
        {
            id: objectListContainer
            anchors
            {
                top: captionLabel.visible ? captionLabel.bottom : parent.top;
                topMargin: captionLabel.visible ? UM.Theme.sizes.default_margin.height : 0;
                bottom: parent.bottom;
                left: parent.left;
            }

            width: base.detailsVisible ? parent.width / 2 : parent.width;
            frameVisible: true;

            Rectangle {
                parent: viewport
                anchors.fill: parent
                color: palette.light
            }

            ListView
            {
                id: objectList;

                delegate: Rectangle
                {
                    width: objectListContainer.viewport.width;
                    height: childrenRect.height;
                    color: ListView.isCurrentItem ? palette.highlight : index % 2 ? palette.light : palette.midlight

                    Label
                    {
                        anchors.left: parent.left;
                        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
                        text: model.name
                        color: parent.ListView.isCurrentItem ? palette.highlightedText : palette.text;
                    }

                    MouseArea
                    {
                        anchors.fill: parent;
                        onClicked:
                        {
                            if(!parent.ListView.isCurrentItem)
                            {
                                parent.ListView.view.currentIndex = index;
                                base.itemActivated();
                            }
                        }
                    }
                }
            }
        }

        Item
        {
            id: detailsPane;

            anchors
            {
                left: objectListContainer.right;
                leftMargin: UM.Theme.sizes.default_margin.width;
                top: parent.top;
                bottom: parent.bottom;
                right: parent.right;
            }

            visible: base.detailsVisible;
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
        SystemPalette { id: palette }
    }
}
