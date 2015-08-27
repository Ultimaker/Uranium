// Copyright (c) 2015 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQml 2.2

import UM 1.1 as UM

UM.Dialog
{
    id: elementRoot
    property string wizardTitle
    property var wizardPages
    property int currentPage: 0
    property variant wizardModel: createPageModel(elementRoot.wizardPages)

    property bool firstRun: false

    signal nextClicked()
    signal resize(int pageWidth, int pageHeight)

    minimumWidth: UM.Theme.sizes.modal_window_minimum.width
    minimumHeight: UM.Theme.sizes.modal_window_minimum.height
    title: elementRoot.wizardTitle

    function createPageModel(objectsArray)
    {
        //create a new qt listmodel with the javascript array of objects it is given
        var newListModel = Qt.createQmlObject('import QtQuick 2.2; \
            ListModel {}', elementRoot)
        for (var i = 0; i < objectsArray.length; i++)
        {
            newListModel.append({
                "page": objectsArray[i].page,
                "title": objectsArray[i].title
            });
        }
        return newListModel
    }


    function insertPage(page, title, position)
    {
        elementRoot.wizardModel.insert(position, {"page": page, "title": title})
    }

    function removePage(index)
    {
        elementRoot.wizardModel.remove(index)
    }

    function getPageSource(index)
    {
        //returns the actual source of a page
        var page = progressList.model.get(index).page
        return UM.Resources.getPath(UM.Resources.WizardPagesLocation, page)
    }

    function getPageCount()
    {
        return elementRoot.wizardModel.count
    }

    Row
    {
        UM.I18nCatalog { id: catalog; name:"uranium"}
        anchors.fill: parent;
        SystemPalette{id: palette}
        spacing:  UM.Theme.sizes.default_margin.width
        Connections
        {
            target: Printer
            onRequestAddPrinter:
            {
                addMachineWizard.visible = true
            }
        }

        Rectangle
        {
            id: wizardProgress
            visible: progressList.model.count > 1 ? true : false
            width: UM.Theme.sizes.wizard_progress.width
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            color: palette.light

            Component
            {
                id: wizardDelegate
                Item
                {
                    height: childrenRect.height
                    Button
                    {
                        id: progressButton
                        width: wizardProgress.width
                        text: title
                        style: ButtonStyle
                        {
                            background: Rectangle
                            {
                                border.width: 0
                                color: "transparent"
                            }
                            label: Text
                            {
                                id: progressText
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.Wrap
                                renderType: Text.NativeRendering
                                text: control.text
                                font.underline: title == progressList.model.get(elementRoot.currentPage).title || progressButton.hovered ? true : false
                                color: title == progressList.model.get(elementRoot.currentPage).title ? palette.text : palette.mid
                            }
                        }
                        onClicked:
                        {
                            for (var i = 0; i < progressList.model.count; i++)
                            {
                                if (progressList.model.get(i).title == title)
                                {
                                   elementRoot.currentPage = i
                                   break
                                }
                            }
                        }
                    }
                    Label
                    {
                        id: progressArrow
                        anchors.top: progressButton.bottom
                        x: (wizardProgress.width-progressArrow.width)/2
                        text: "▼"
                        visible: title != progressList.model.get(progressList.model.count - 1).title ? true : false
                        color: palette.mid
                    }
                }
            }
            ListView
            {
                id: progressList
                property var index: 0
                model: elementRoot.wizardModel
                delegate: wizardDelegate
                anchors.fill: parent
                anchors.top: parent.top
                anchors.topMargin: UM.Theme.sizes.default_margin.height
            }
        }

        Loader
        {
            id: pageLoader
            anchors.top: parent.top
            width: parent.width - wizardProgress.width - (2 *  UM.Theme.sizes.default_margin.width)
            height: parent.height
            source: elementRoot.getPageSource(elementRoot.currentPage)

        }

        Connections
        {
            target: pageLoader.item
            ignoreUnknownSignals: true
            onReloadModel:
            {
                elementRoot.wizardModel = newModel
            }
        }
    }

    rightButtons: [
        Button
        {
            id: backButton
            //: Add Printer wizard Button: 'Back'
            text: catalog.i18nc("@action:button","< Back");
            enabled: elementRoot.currentPage <= 0 ? false : true
            visible: elementRoot.firstRun ? false : true
            onClicked:
            {
                if (elementRoot.currentPage > 0)
                {
                    elementRoot.currentPage -= 1
                }
            }
        },
        Button
        {
            id: nextButton
            text:
            {
                if (elementRoot.currentPage < progressList.model.count - 1)
                {
                    //: Add Printer wizard button: 'Next'
                    return catalog.i18nc("@action:button","Next >")
                } else if (elementRoot.currentPage == progressList.model.count - 1)
                {
                    //: Add Printer wizard button: 'Finish'
                    return catalog.i18nc("@action:button","Finish ✓")
                }
            }

            onClicked:
            {
                if (elementRoot.currentPage < progressList.model.count - 1)
                {
                    elementRoot.nextClicked()
                    elementRoot.currentPage += 1
                }else if (elementRoot.currentPage == progressList.model.count - 1)
                {
                    elementRoot.nextClicked()
                }
            }
        },
        Button
        {
            id: cancelButton
            //: Add Printer wizard button: "Cancel"
            text: catalog.i18nc("@action:button","Cancel X")
            onClicked:
            {
                elementRoot.wizardModel = createPageModel(elementRoot.wizardPages)
                elementRoot.visible = false
            }
            visible: elementRoot.firstRun ? false : true
        }
    ]
}

