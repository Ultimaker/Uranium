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
    property alias section: objectList.section;
    property alias delegate: objectList.delegate;
    property string nameRole: "name";
    property bool detailsVisible: true;

    property variant objectList: objectList;
    property variant currentItem: null
    property string scrollviewCaption: "";

    default property alias details: detailsPane.children;

    signal itemActivated();

    property alias buttons: buttonRow.children;

    resetEnabled: false;

    property string activeId: ""
    property int activeIndex: -1

    Row
    {
        id: buttonRow;

        anchors
        {
            left: parent.left
            right: parent.right
            top: parent.top
        }

        height: childrenRect.height;
    }

    Item
    {
        anchors
        {
            top: buttonRow.bottom;
            topMargin: UM.Theme.getSize("default_margin").height;
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
            width: objectListContainer.width
            elide: Text.ElideRight
        }

        ScrollView
        {
            id: objectListContainer
            anchors
            {
                top: captionLabel.visible ? captionLabel.bottom : parent.top;
                topMargin: captionLabel.visible ? UM.Theme.getSize("default_margin").height : 0;
                bottom: parent.bottom;
                left: parent.left;
            }

            width: base.detailsVisible ? parent.width * 0.4 : parent.width;
            frameVisible: true;

            Rectangle {
                parent: viewport
                anchors.fill: parent
                color: palette.light
            }

            ListView
            {
                id: objectList;
                currentIndex: activeIndex
                onCurrentIndexChanged:
                {
                    // Explicitly trigger onCurrentItemChanged
                    base.currentItem = null;
                    base.currentItem = (currentIndex != null) ? model.getItem(currentIndex) : null;
                }

                section.property: "group"
                section.criteria: ViewSection.FullString
                section.delegate: Rectangle
                {
                    width: objectListContainer.viewport.width;
                    height: childrenRect.height;
                    color: palette.light

                    Label
                    {
                        anchors.left: parent.left;
                        anchors.leftMargin: UM.Theme.getSize("default_lining").width;
                        text: section
                        font.bold: true
                        color: palette.text;
                    }
                }

                delegate: Rectangle
                {
                    width: objectListContainer.viewport.width;
                    height: childrenRect.height;
                    color: ListView.isCurrentItem ? palette.highlight : index % 2 ? palette.base : palette.alternateBase

                    Label
                    {
                        anchors.left: parent.left;
                        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
                        anchors.right: parent.right;
                        text: model.name
                        elide: Text.ElideRight
                        font.italic: model.id == activeId
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
                leftMargin: UM.Theme.getSize("default_margin").width;
                top: parent.top;
                bottom: parent.bottom;
                right: parent.right;
            }

            visible: base.detailsVisible;
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
        SystemPalette { id: palette }

        Connections
        {
            target: objectList.model

            onDataChanged:
            {
                if(topLeft.row <= objectList.currentIndex || bottomRight.row <= objectList.currentIndex)
                {
                    base.currentItem = objectList.currentItem != null ? objectList.model.getItem(objectList.currentIndex) : null;
                }
            }
        }
    }
}
