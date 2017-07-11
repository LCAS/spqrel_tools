import time
from naoqi import ALProxy, ALBroker, ALModule
from abc import ABCMeta, abstractmethod


class EventAbstractClass(ALModule):
    __metaclass__ = ABCMeta

    def __init__(self, inst, ip, port):
        self.inst = inst
        self.name = inst.__class__.__name__ + "_inst"
        self._make_global(self.name, self)
        self.broker = self._connect(self.name, ip, port)
        super(EventAbstractClass, self).__init__(self.name)

        self.memory = self._make_global("memory", ALProxy("ALMemory"))

    def _connect(self, name, ip, port):
        try:
            broker = ALBroker(name + "_broker",
                              "0.0.0.0",  # listen to anyone
                              0,  # find a free port and use it
                              ip,  # parent broker IP
                              port)
            print "Connected to %s:%s" % (ip, str(port))
            return broker
        except RuntimeError:
            print "Cannot connect to %s:%s. Retrying in 1 second." % (ip, str(port))
            time.sleep(1)
            return self._connect(name, ip, port)

    def _make_global(self, name, var):
        globals()[name] = var
        return globals()[name]

    def update_globals(self, glob):
        glob[self.name] = self

    def subscribe(self, event, callback):
        self.memory.subscribeToEvent(
            event,
            self.name,
            callback.func_name
        )

    def unsubscribe(self, event):
        self.memory.unsubscribeToEvent(
            event,
            self.name
        )

    def remove_subscribers(self, event):
        subscribers = self.memory.getSubscribers(event)
        if subscribers:
            print event + " already in use by another node"
            for module in subscribers:
                self.__stop_module(module, event)

    def __stop_module(self, module, event):
        print "Unsubscribing '{}' from " + event.format(
            module)
        try:
            self.memory.unsubscribeToEvent(event, module)
        except RuntimeError:
            print "Could not unsubscribe from " + event

    @abstractmethod
    def start(self, *args, **kwargs):
        """
        All subscribing goes in here.
        """
        return
