// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.1

import UM 1.5 as UM

PreferencesPage
{
    id: base

    property alias model: objectList.model
    property alias section: objectList.section
    property alias delegate: objectList.delegate
    property string nameRole: "name"
    property string sectionRole: "group"
    property bool detailsVisible: true

    property variant objectList: objectList
    property variant currentItem: null
    property string scrollviewCaption: ""

    default property alias details: detailsPane.children

    signal itemActivated()
    signal hamburgeButtonClicked(Item hamburger_button)
    property alias hamburgerButtonVisible: hamburgerButton.visible

    resetEnabled: false

    property string activeId: ""
    property int activeIndex: -1


    Item
    {
        anchors.fill: parent
        UM.Label
        {
            id: captionLabel
            anchors
            {
                top: parent.top
                left: parent.left
            }
            visible: scrollviewCaption != ""
            text: scrollviewCaption
            width: objectListBackground.width
            elide: Text.ElideRight
            textFormat: Text.StyledText
        }

        UM.SimpleButton
        {
            id: hamburgerButton
            anchors.right: parent.right
            width: UM.Theme.getSize("medium_button_icon").width
            height: UM.Theme.getSize("medium_button_icon").height
            iconSource: UM.Theme.getIcon("Hamburger")
            hoverColor: UM.Theme.getColor("small_button_text_hover")
            color: UM.Theme.getColor("small_button_text")

            onClicked: base.hamburgeButtonClicked(hamburgerButton)
        }
        Rectangle
        {
            id: objectListBackground
            color: UM.Theme.getColor("main_background")
            border.width: UM.Theme.getSize("default_lining").width
            border.color: UM.Theme.getColor("thick_lining")
            anchors
            {
                top: captionLabel.visible ? captionLabel.bottom : parent.top
                topMargin: captionLabel.visible ? UM.Theme.getSize("default_margin").height : 0
                bottom: parent.bottom
                left: parent.left
            }
            width: base.detailsVisible ? Math.round(parent.width * 0.4) | 0 : parent.width
            ListView
            {
                id: objectList

                clip: true
                ScrollBar.vertical: UM.ScrollBar {}
                anchors.fill: parent
                anchors.margins: UM.Theme.getSize("default_margin").height
                anchors.topMargin: UM.Theme.getSize("narrow_margin").height
                currentIndex: activeIndex
                onCurrentIndexChanged:
                {
                    // Explicitly trigger onCurrentItemChanged
                    base.currentItem = null;
                    base.currentItem = (currentIndex != null) ? model.getItem(currentIndex) : null;
                }

                section.property: base.sectionRole
                section.criteria: ViewSection.FullString
                section.delegate: Rectangle
                {
                    width: objectList.width - objectList.ScrollBar.vertical.width
                    height: childrenRect.height + UM.Theme.getSize("narrow_margin").height
                    color: UM.Theme.getColor("background_1")

                    UM.Label
                    {
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
                        font.italic: model.id == activeId
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
            id: detailsPane

            anchors
            {
                left: objectListBackground.right
                leftMargin: UM.Theme.getSize("default_margin").width
                top: parent.top
                bottom: parent.bottom
                right: parent.right
            }

            visible: base.detailsVisible
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }

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
