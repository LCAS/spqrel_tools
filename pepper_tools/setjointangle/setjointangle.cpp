#include <iostream>

#include <alcommon/alproxy.h>
#include <alcommon/albroker.h>

#include <alproxies/almotionproxy.h>


int main(int argc, char **argv)
{
  
  if(argc != 5)
    {
      std::cerr << "Wrong number of arguments!" << std::endl;
      std::cerr << "Usage: setstate PEPPER_IP PEPPER_PORT joint angle" << std::endl;
      exit(2);
    }


  std::string pip = argv[1];
  int pport = atoi(argv[2]);
  std::string joint = argv[3];
  float angle = atof(argv[4]);

  // A broker needs a name, an IP and a port to listen:
  const std::string brokerName = "mybroker";
  // Create your own broker
  boost::shared_ptr<AL::ALBroker> broker =
    AL::ALBroker::createBroker(brokerName, "0.0.0.0", 54000, pip, pport);
  
  // Create a proxy to ALMotionProxy
  AL::ALMotionProxy proxyM(broker);
  
  // Example showing how to set angles, using a fraction of max speed
    // Example showing how to get the names of all the joints in the body.
  std::vector<std::string> bodyNames = proxyM.getBodyNames("Body");
  std::cout << "All joints in Body: " << std::endl;
  std::cout << bodyNames << std::endl;

  std::vector<float> sensorAngles = proxyM.getAngles(AL::ALValue(joint), true);
  std::cout << "Sensor angles before: " << std::endl;
  std::cout << sensorAngles << std::endl;

  proxyM.setAngles(AL::ALValue(joint), AL::ALValue(angle), 0.05f);

  //sleep because setAngle non blocking and getAngles after returns the same angle as before
  qi::os::sleep(1.0f);
  
  sensorAngles = proxyM.getAngles(AL::ALValue(joint), true);
  std::cout << "Sensor angles after: " << std::endl;
  std::cout << sensorAngles << std::endl;
  
  /*AL::ALValue names       = AL::ALValue::array("HeadYaw", "HeadPitch");
  AL::ALValue angles      = AL::ALValue::array(0.3f, -0.3f);
  float fractionMaxSpeed  = 0.1f;
  motion.setStiffnesses(names, AL::ALValue::array(1.0f, 1.0f));
  qi::os::sleep(1.0f);
  motion.setAngles(names, angles, fractionMaxSpeed);
  qi::os::sleep(1.0f);
  motion.setStiffnesses(names, AL::ALValue::array(0.0f, 0.0f));
  */
  return 0;
}
