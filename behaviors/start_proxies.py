class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        self.movementdetection = ALProxy( "ALMovementDetection" )
        self.wavingdetection   = ALProxy( "ALWavingDetection" )
        self.zonesdetection = ALProxy("ALEngagementZones")
        self.peopledetection = ALProxy("ALPeoplePerception")
        self.sittingdetection = ALProxy("ALSittingPeopleDetection")

        ALMemory.subscribeToEvent("MovementDetection/MovementDetected", "", "")
        ALMemory.subscribeToEvent("WavingDetection/Waving","","")
        ALMemory.subscribeToEvent("EngagementZones/PersonEnteredZone1","self.getname()","","")
        ALMemory.subscribeToEvent("PeoplePerception/JustArrived","","")
        ALMemory.subscribeToEvent("SittingPeopleDetection/PersonSittingDown","","")

        # ADD AS MANY AS NEEDED
        # .
        pass

    def onUnload(self):
        #put clean-up code here
        pass

    def onInput_onStart(self):
        #self.onStopped() #activate the output of the box
        pass

    def onInput_onStop(self):
        self.onUnload() #it is recommended to reuse the clean-up as the box is stopped
        self.onStopped() #activate the output of the box
