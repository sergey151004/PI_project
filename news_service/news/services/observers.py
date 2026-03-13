observers = []


def register(observer):
    observers.append(observer)


def notify(news):
    for observer in observers:
        observer.update(news)


class LoggerObserver:

    def update(self, news):
        print("New article:", news.title)