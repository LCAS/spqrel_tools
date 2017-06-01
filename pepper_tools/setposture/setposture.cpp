/**
 * Copyright (c) 2011 Aldebaran Robotics. All Rights Reserved
 * \file sayhelloworld.cpp
 * \brief Make NAO say a short phrase.
 *
 * A simple example showing how to make NAO say a short phrase using the
 * specialized proxy ALTextToSpeechProxy.
 */


#include <iostream>
#include <alerror/alerror.h>
#include <alproxies/altexttospeechproxy.h>
#include <alproxies/alrobotpostureproxy.h>

#include <alcommon/alproxy.h>
#include <alcommon/albroker.h>

int main(int argc, char* argv[])
{
  if(argc != 4)
  {
    std::cerr << "Wrong number of arguments!" << std::endl;
    std::cerr << "Usage: setstate PEPPER_IP PEPPER_PORT posture" << std::endl;
    exit(2);
  }


  std::string pip = argv[1];
  int pport = atoi(argv[2]);//9559;
  std::string posture = argv[3];
  
  // A broker needs a name, an IP and a port to listen:
  const std::string brokerName = "mybroker";
  // Create your own broker
  boost::shared_ptr<AL::ALBroker> broker =
    AL::ALBroker::createBroker(brokerName, "0.0.0.0", 54000, pip, pport);

  // Create a proxy to ALTextToSpeechProxy
  AL::ALProxy proxyTTS(broker, "ALTextToSpeech");

  AL::ALRobotPostureProxy proxyRP(broker);
  std::string current_posture = proxyRP.getPosture();
  std::cerr << "Robot posture: " << current_posture << std::endl;
    
  /** The desired phrase to be said. */
  std::string phraseToSay = "Hello! My current posture is " + current_posture;
  // Call say method
  proxyTTS.callVoid("say", phraseToSay);
  
  std::vector<std::string> familypostures = proxyRP.getPostureFamilyList();
  for (size_t i=0; i<familypostures.size(); i++){
    std::string fposture = familypostures[i];
    std::cerr << "Posture Family: " << fposture << std::endl;
  }

  std::vector<std::string> postures = proxyRP.getPostureList();
  for (size_t i=0; i<postures.size(); i++){
    std::string posture = postures[i];
    std::cerr << "Possible postures: " << posture << std::endl;
  }


  if (current_posture != posture){
    phraseToSay = "Changing my posture to " + posture;
    proxyTTS.callVoid("say", phraseToSay);

    proxyRP.goToPosture(posture,1.0);

    current_posture = proxyRP.getPosture();
    std::cerr << "Robot posture: " << current_posture << std::endl;
  } else {
    phraseToSay = "Nothing to change here.";
    proxyTTS.callVoid("say", phraseToSay);
  }
  
  exit(0);
}
