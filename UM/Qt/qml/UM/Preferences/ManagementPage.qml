// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.1
import QtQuick.Dialogs

import UM 1.5 as UM

PreferencesPage
{
    id: base

    property alias model: objectList.model
    property alias section: objectList.section
    property alias delegate: objectList.delegate
    property alias sectionRole: objectList.section.property

    property bool detailsVisible: true

    property variant objectList: objectList
    property variant currentItem: null
    property alias detailsPlaneCaption: detailsPlaneCaptionLabel.text
    property alias scrollviewCaption: scrollViewCaptionLabel.text

    default property alias content: detailsPane.children
    property alias listContent: objectListBackground.children

    signal itemActivated()
    signal hamburgeButtonClicked(Item hamburger_button)
    property alias hamburgerButtonVisible: hamburgerButton.visible

    property var isActiveModelFunction: function(model, id) { return model.id == id }

    resetEnabled: false

    property string activeId: ""
    property int activeIndex: -1

    UM.Label
    {
        id: scrollViewCaptionLabel
        anchors
        {
            top: parent.top
            left: parent.left
        }
        visible: text != ""
        width: objectListBackground.width
        elide: Text.ElideRight
        textFormat: Text.StyledText
    }

    Rectangle
    {
        id: objectListBackground
        color: UM.Theme.getColor("main_background")
        border.width: UM.Theme.getSize("default_lining").width
        border.color: UM.Theme.getColor("thick_lining")
        anchors
        {
            top: scrollViewCaptionLabel.visible ? scrollViewCaptionLabel.bottom : parent.top
            topMargin: scrollViewCaptionLabel.visible ? UM.Theme.getSize("default_margin").height : 0
            bottom: parent.bottom
            left: parent.left
        }
        width: base.detailsVisible ? Math.round(parent.width * 0.3) : parent.width
        ListView
        {
            id: objectList

            clip: true
            ScrollBar.vertical: UM.ScrollBar {}
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").height
            anchors.topMargin: UM.Theme.getSize("narrow_margin").height
            currentIndex: activeIndex
            boundsBehavior: Flickable.StopAtBounds
            onCurrentIndexChanged:
            {
                // Explicitly trigger onCurrentItemChanged
                base.currentItem = null;
                base.currentItem = (currentIndex != null) ? model.getItem(currentIndex) : null;
            }


            section.criteria: ViewSection.FullString
            section.delegate: Rectangle
            {
                width: objectList.width - objectList.ScrollBar.vertical.width
                height: sectionLabel.height + UM.Theme.getSize("narrow_margin").height
                color: UM.Theme.getColor("background_1")

                UM.Label
                {
                    id: sectionLabel
                    anchors.left: parent.left
                    anchors.leftMargin: UM.Theme.getSize("default_lining").width
                    anchors.verticalCenter: parent.verticalCenter
                    text: section
                    font: UM.Theme.getFont("default_bold")
                    color: UM.Theme.getColor("text_default")
                }
            }

            delegate: Rectangle
            {
                width: objectList.width - objectList.ScrollBar.vertical.width
                height: childrenRect.height
                color: ListView.isCurrentItem ? UM.Theme.getColor("text_selection") : UM.Theme.getColor("main_background")
                UM.Label
                {
                    anchors.left: parent.left
                    anchors.leftMargin: UM.Theme.getSize("default_margin").width
                    anchors.right: parent.right
                    text: model.name
                    elide: Text.ElideRight
                    font: isActiveModelFunction(model, activeId) ? UM.Theme.getFont("default_italic") : UM.Theme.getFont("default")
                    wrapMode: Text.NoWrap
                }

                MouseArea
                {
                    anchors.fill: parent
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
        id: detailsPlaneCaption
        height: childrenRect.height

        anchors
        {
            left: objectListBackground.right
            leftMargin: UM.Theme.getSize("default_margin").width
            top: parent.top
            right: parent.right
        }

        UM.Label
        {
            id: detailsPlaneCaptionLabel
            anchors.verticalCenter: hamburgerButton.verticalCenter
            font: UM.Theme.getFont("large_bold")
        }

        UM.ToolbarButton
        {
            id: hamburgerButton
            anchors.right: parent.right
            toolItem: UM.ColorImage
            {
                source: UM.Theme.getIcon("Hamburger")
                color: UM.Theme.getColor("icon")
            }
            onClicked: base.hamburgeButtonClicked(hamburgerButton)
        }
    }

    Item
    {
        id: detailsPane

        anchors
        {
            left: objectListBackground.right
            leftMargin: UM.Theme.getSize("default_margin").width
            top: detailsPlaneCaption.bottom
            topMargin: UM.Theme.getSize("narrow_margin").width
            bottom: parent.bottom
            right: parent.right
        }

        visible: base.detailsVisible
    }

    Item
    {
        Connections
        {
            target: objectList.model

            function onItemsChanged()
            {
                var itemIndex = -1;
                if (base.currentItem === null)
                {
                    return;
                }
                for (var i = 0; i < objectList.model.count; ++i)
                {
                    if (objectList.model.getItem(i).id == base.currentItem.id)
                    {
                        itemIndex = i;
                        break;
                    }
                }

                objectList.currentIndex = itemIndex;
                base.currentItem = itemIndex >= 0 ? objectList.model.getItem(itemIndex) : null;
            }
        }
    }
}
