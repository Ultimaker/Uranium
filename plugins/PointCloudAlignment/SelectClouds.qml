import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
Rectangle 
{
    width: 300; height: 100
    RowLayout 
    {
        ComboBox
        {
            id:selection1
            model:manager.cloudList
            currentIndex: {
                for(var i = 0; i < model.rowCount(); ++i) {
                    if(model.getItem(i).text == value /*From parent loader*/) {
                        return i;
                    }
                }

                return -1;
            }
            onCurrentIndexChanged: { console.log(currentText)}
        }
        ComboBox
        {
            id:selection2
            model:manager.cloudList
            currentIndex: {
                for(var i = 0; i < model.rowCount(); ++i) {
                    if(model.getItem(i).text == value /*From parent loader*/) {
                        return i;
                    }
                }

                return -1;
            }
            onCurrentIndexChanged: { console.log(currentText)}
        }
        Button 
        {
            text: "start manual align"
            enabled: selection1.currentIndex == selection2.currentIndex ? false:true
            onClicked: 
            {
                manager.startAlignProcess(selection1.currentIndex,selection2.currentIndex)
            }
        }
    }
}