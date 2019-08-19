#include "projectadder.h"

#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>

int main(int argc, char *argv[])
{
#if defined(Q_OS_WIN)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif

    QGuiApplication app(argc, argv);
    qmlRegisterType<ProjectAdder>("Api", 1, 0, "ProjectAdder");
    QQuickView *view = new QQuickView;
    view->setSource(QStringLiteral("qrc:/main.qml"));

    QObject *item = view->rootObject();
    item->setProperty("sourceURL", "http://avdatabase.library.illinois.edu:8000/");
    view->show();
    return app.exec();
}
