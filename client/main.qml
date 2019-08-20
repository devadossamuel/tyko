import QtQuick 2.9
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.3
import Api 1.0
import Qt.labs.settings 1.0

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 640
    height: 480
    property int dataRefreshRate: 4000
    property url sourceURL
    Settings{
        property alias sourceURL: mainWindow.sourceURL
    }
    SystemPalette { id: appPalette; colorGroup: SystemPalette.Active }
    title: "Current :" + mainWindow.sourceURL

    ConfigDialog{
        id: setttingsDialog
        sourceURL: mainWindow.sourceURL
        onAccepted:{
            mainWindow.sourceURL = sourceURL
        }
    }

    Action{
        id: changeConfigAction
        text: "Settings"
        onTriggered: {
            setttingsDialog.open()
        }
    }
    menuBar: MenuBar{
        Menu{
            title: "Settings"
            MenuItem{
                text: "Configure"
                action: changeConfigAction
            }
        }
    }
    header: TabBar{
        id: bar
        width: parent.width

        TabButton {
            text: "Projects"
        }
        TabButton {
            text: "Collections"
        }
        TabButton {
            text: "Vendors"
        }
        TabButton {
            text: "Items"
        }
        TabButton {
            text: "Contacts"
        }
    }
    StackLayout{
        anchors.fill: parent
        currentIndex: bar.currentIndex
        ProjectsPage{
            sourceURL: mainWindow.sourceURL
        }
        Rectangle{
            color: "light blue"
            Label{
                text: "Do something here"
            }
        }
    }
    footer:ToolBar{
        RowLayout{
            Label{
                id: statusMessage
            }
        }
    }

    Component.onCompleted: {
        if(sourceURL == ""){
            setttingsDialog.open()
        }
    }
}
