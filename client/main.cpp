//#include "projectadder.h"
#include <QQmlApplicationEngine>
//#include <QGuiApplication>
//#include <QQuickView>
#include <QQmlComponent>
#include <QtCore/QtCore>
#include <QApplication>


int main(int argc, char *argv[])
{
#if defined(Q_OS_WIN)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif

    QGuiApplication app(argc, argv);
//    qmlRegisterType<ProjectAdder>("Api", 1, 0, "ProjectAdder");
    QQmlApplicationEngine engine;
    engine.load(QStringLiteral("qrc:/main.qml"));
    if(engine.rootObjects().isEmpty()){
        return -1;
    }
    return app.exec();
}
