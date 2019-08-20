#include "projectadder.h"
#include "configDialog.h"

#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>
#include <QQmlComponent>



int main(int argc, char *argv[])
{
#if defined(Q_OS_WIN)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif

    QGuiApplication app(argc, argv);
    qmlRegisterType<ProjectAdder>("Api", 1, 0, "ProjectAdder");
    QQmlApplicationEngine engine;
//    QQmlEngine engine;

//    QStringLiteral("qrc:/main.qml");

//    QQuickWindow *itm = qobject_cast<QQuickWindow*>(engine.rootObjects().value(0));
//    QQmlComponent configWindowType(&engine, QStringLiteral("qrc:/Config.qml"));
//    if( not configWindowType.isReady()){
//        return 0;
//    }
//    QObject *object = configWindowType.create();
//    QQuickView mainView;
//    mainView.setSource(QStringLiteral("qrc:/main.qml"));
////    mainView.show();
//
//    Config config(engine, mainView);
//
//
//    QObject::connect(object, SIGNAL(openDatabase(QUrl)),
//                     &config, SLOT(startProgram(QUrl)));
//
//    QObject::connect(object, SIGNAL(rejected()),
//                     &config, SLOT(cancel()));
//

//    QQuickView *configView = new QQuickView;

//    configView->setSource(QStringLiteral("qrc:/Config.qml"));
////    configView->setSource(QStringLiteral("qrc:/main.qml"));

////    QObject *item = configView->rootObject();
//    configView->setTitle("Config");
////    configView->setModality(Qt::WindowModality::WindowModal);
//    configView->show();


//    QQuickView *mainView = new QQuickView;
//    mainView->setSource(QStringLiteral("qrc:/main.qml"));
//    mainView->show();
//    QObject *item = mainView.rootObject();
//    QObject *item = mainView->rootObject();
//    item->setProperty("sourceURL", QUrl("http://avdatabase.library.illinois.edu:8000/"));
//    mainView->show();
    engine.load(QStringLiteral("qrc:/main.qml"));
    if(engine.rootObjects().isEmpty()){
        return -1;
    }
    return app.exec();
}
