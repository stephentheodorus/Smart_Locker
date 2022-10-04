import abc
from kink import inject, di
from abc import abstractmethod
from .emailer import *
from typing import List

### Convention
class Message:
    pass


class Observer:
    @abstractmethod
    def update(self, message: Message):
        pass


class Subject:
    @abstractmethod
    def subscribe(self, observer: Observer):
        pass

    @abstractmethod
    def unsubscribe(self, observer: Observer):
        pass

    @abstractmethod
    def notify(self, message: Message):
        pass


# END#


### Messages
@inject
class NewUserMessage(Message):
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


@inject
class NewPackageMessage(Message):
    def __init__(self, email, name, locker_id, item_type, item_size, verification):
        self.email = email
        self.name = name

        self.locker_id = locker_id
        self.item_type = item_type
        self.item_size = item_size
        self.verification = verification


@inject
class RetrievePackageReminderMessage(Message):
    def __init__(self, users):
        self.users = users


@inject
class WrongIdInputMessage(Message):
    def __init__(self):
        pass


# END#


### Observers

### Observing if there is a new user
@inject(alias=Observer)
class NewUser(Observer):
    def update(self, message: NewUserMessage):
        if type(message) == NewUserMessage:
            emailer = Emailer("schliessfach.post.box@gmail.com", "pntdmopplsvomrzq")
            emailer.send_email_to_new_user(message.id, message.name, message.email)


# END#

### Observing if there is a new package for a user
@inject(alias=Observer)
class NewPackage(Observer):
    def update(self, message: NewPackageMessage):
        if type(message) == NewPackageMessage:
            emailer = Emailer("schliessfach.post.box@gmail.com", "pntdmopplsvomrzq")
            emailer.notify_new_package(
                message.email,
                message.name,
                message.locker_id,
                message.item_type,
                message.item_size,
                message.verification,
            )


# END#

### Observing if there is only one empty locker left
@inject(alias=Observer)
class OneLockerLeft(Observer):
    def update(self, message: RetrievePackageReminderMessage):
        if type(message) == RetrievePackageReminderMessage:
            emailer = Emailer("schliessfach.post.box@gmail.com", "pntdmopplsvomrzq")
            for user in message.users:
                emailer.retrieve_package_reminder(user[0], user[1])


# END#

### Observing if ID inputted is wrong for five consecutive times
@inject(alias=Observer)
class WrongIdInputFiveTimes(Observer):
    def __init__(self):
        self.times = 0

    def update(self, message: WrongIdInputMessage):
        if type(message) == WrongIdInputMessage:
            if self.times == 4:
                emailer = Emailer("schliessfach.post.box@gmail.com", "pntdmopplsvomrzq")
                emailer.notify_operator_five_times_wrong_id_input()
                self.times = 0
            else:
                self.times += 1
        else:
            self.times = 0


# END#

# END#


### Subjects
@inject
class UserSubject(Subject):
    def __init__(self, observers: List[Observer]):
        self.observers = observers

    def subscribe(self, observer: Observer):
        self.observers.append(observer)

    def unsubscribe(self, observer: Observer):
        self.observers.remove(observer)

    def notify(self, message: Message):
        for observer in self.observers:
            observer.update(message)


@inject
class LockerSubject(Subject):
    def __init__(self, observers: List[Observer]):
        self.observers = observers

    def subscribe(self, observer: Observer):
        self.observers.append(observer)

    def unsubscribe(self, observer: Observer):
        self.observers.remove(observer)

    def notify(self, message: Message):
        for observer in self.observers:
            observer.update(message)


# END#
