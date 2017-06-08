#include "naoqi_localizer.h"
#include <qi/clock.hpp>

NAOqiLocalizer::NAOqiLocalizer(qi::SessionPtr session){
  _session = session;
  if (! _session)
    throw std::runtime_error("Error: No memory service provided");
  
  _restarted = true;
  _old_odom_pose.setZero();
  
  _forced_max_range = 10;
  _squared_endpoint_distance = 0.1*0.1;
  _show_distance_map = false;
  _force_redisplay=false;
  _set_pose = false;
  _use_gui=false;
  _map_origin.setZero();
  //_broadcaster = 0;
  _timers.resize(10);
  _last_timer_slot=0;
  _laser_pose.setZero();

  
}

void NAOqiLocalizer::initGUI(){
  _use_gui=true;
  cv::namedWindow( "pepper_localizer", 0 );
  cv::setMouseCallback( "pepper_localizer", &NAOqiLocalizer::onMouse, this );
  cerr << "GUI initialized" << endl;
}


Vector2fVector NAOqiLocalizer::rawPointsToRobotFrame(Vector2fVector& rawPoints){
  Vector2fVector framePoints(rawPoints.size());
  
  for (size_t i=0; i<rawPoints.size(); i++){
    Eigen::Vector2f rawPoint = rawPoints[i];
    if (i<15){
      //Right Laser point
      float lX = -0.01800;
      float lY = -0.08990;
      float lt = -1.57079;
      float tX = rawPoint[0]*cos(lt) - rawPoint[1]*sin(lt) + lX;
      float tY = rawPoint[0]*sin(lt) + rawPoint[1]*cos(lt) + lY;
      Eigen::Vector2f transformedPoint(tX,tY);
      framePoints[i] = transformedPoint;
      continue;
    }
    if (i<30){
      //Front Laser point
      float lX = 0.05620;
      float lY = 0.0;
      float lt = 0.0;
      float tX = rawPoint[0]*cos(lt) - rawPoint[1]*sin(lt) + lX;
      float tY = rawPoint[0]*sin(lt) + rawPoint[1]*cos(lt) + lY;
      Eigen::Vector2f transformedPoint(tX,tY);
      framePoints[i] = transformedPoint;
      continue;
    }
    if (i<45){
      //Leftt Laser point
      float lX = -0.01800;
      float lY =  0.08990;
      float lt =  1.57079;
      float tX = rawPoint[0]*cos(lt) - rawPoint[1]*sin(lt) + lX;
      float tY = rawPoint[0]*sin(lt) + rawPoint[1]*cos(lt) + lY;
      Eigen::Vector2f transformedPoint(tX,tY);
      framePoints[i] = transformedPoint;
      continue;
    }
  }
  return framePoints;
}


void NAOqiLocalizer::subscribeServices(){
  qi::AnyObject memory_service = _session->service("ALMemory");
  qi::AnyObject motion_service = _session->service("ALMotion");

  _stop_thread=false;
  _servicesMonitorThread = std::thread(&NAOqiLocalizer::servicesMonitorThread, this, memory_service, motion_service);
  std::cout << "Services Monitor Thread launched." << std::endl;
}

void NAOqiLocalizer::unsubscribeServices(){
  _stop_thread=true;
  _servicesMonitorThread.join();
}



void NAOqiLocalizer::servicesMonitorThread(qi::AnyObject memory_service, qi::AnyObject motion_service) {
  std::vector<std::string> laserKeysVector(laserMemoryKeys, std::end(laserMemoryKeys)); 
  while (!_stop_thread){
    qi::SteadyClock::time_point time_start = qi::SteadyClock::now();
    qi::AnyValue result =  motion_service.call<qi::AnyValue>("getRobotPosition", false);
    std::vector<float> robotpose = result.toList<float>();
    Eigen::Vector3f odom_pose(robotpose[0], robotpose[1], robotpose[2]);
    
    if (!_restarted) {
      Eigen::Vector3f control=t2v(v2t(_old_odom_pose).inverse()*v2t(odom_pose));
      predict(control);
    }
    
    _old_odom_pose=odom_pose;
    
    qi::AnyValue readings = memory_service.call<qi::AnyValue>("getListData", laserKeysVector);
    std::vector<float> floatReadings = readings.toList<float>();
    //Preparing XY pairs
    Vector2fVector points(floatReadings.size()/2);
    for (size_t i = 0; i < floatReadings.size()-1; ){
      Eigen::Vector2f p(floatReadings[i], floatReadings[i+1]);
      points[i/2]=p;
      i=i+2;
    }
    Vector2fVector endpoints = rawPointsToRobotFrame(points);
    bool updated = update(endpoints);
    computeStats();

    _force_redisplay|=updated;
    
    handleGUIDisplay();
    
    _restarted=false;
    
    handleGUIInput();
    
    Eigen::Isometry2f origin=v2t(_map_origin);
    Eigen::Isometry2f robot_transform=origin*v2t(_mean);
    Eigen::Vector3f robot_pose=t2v(robot_transform);

    std::cerr << "Robot pose: " << robot_pose.transpose() << std::endl;

    qi::SteadyClock::time_point time_end = qi::SteadyClock::now();
    qi::MilliSeconds ms = boost::chrono::duration_cast<qi::MilliSeconds>(time_end - time_start);
    std::cerr << "Cycle " << qi::to_string(ms) << std::endl;
    
    usleep(200000);
  }
  std::cout << "Monitor Thread finished." << std::endl;

}

void NAOqiLocalizer::onMouse( int event, int x, int y, int, void* v)
{
  NAOqiLocalizer* n=reinterpret_cast<NAOqiLocalizer*>(v);
  if (!n->_set_pose)
    return;
  if( event == cv::EVENT_LBUTTONDOWN ) {
    std::cerr << "Left Click!" << std::endl;
    Eigen::Vector2f p=n->grid2world(Eigen::Vector2i(y,x));
    Eigen::Vector3f mean=n->mean();
    mean.x()=p.x();
    mean.y()=p.y();
    n->setPose(mean);
    n->_force_redisplay=true;
  }
  if( event == cv::EVENT_RBUTTONDOWN ) {
    std::cerr << "Right Click!" << std::endl;
    Eigen::Vector2f p=n->grid2world(Eigen::Vector2i(y,x));
    Eigen::Vector3f mean=n->mean();
    Eigen::Vector2f dp=p-mean.head<2>();
    float angle=atan2(dp.y(), dp.x());
    mean.z()=angle;
    n->setPose(mean);
    n->_force_redisplay=true;
  }
    
}

void NAOqiLocalizer::handleGUIInput(){
  if (! _use_gui)
    return;

  char key=cv::waitKey(10);
  switch(key) {
  case 'g': 
    cerr << "starting global localization" << endl;
    _restarted = true;
    startGlobal();
    break;
  case 'd': 
    _show_distance_map = ! _show_distance_map;
    cerr << "toggle distance map: " << _show_distance_map << endl;
    _force_redisplay=true;
    break;
  case 'r': 
    setParticleResetting(! particleResetting());
    cerr << "particle resetting = " << particleResetting();
    break;
  case 's': 
    _set_pose=!_set_pose;
    cerr << "set pose is " << _set_pose << endl;
    break;
  default:;
  }
}

void NAOqiLocalizer::handleGUIDisplay() {
  if (_use_gui && (_restarted || _force_redisplay) ) {
    RGBImage img;
    paintState(img, _show_distance_map);
    char buf[1024];
    sprintf(buf, " SetPose: %d", _set_pose);
    cv::putText(img, buf, cv::Point(20, 30), cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(200,0,200), 1);
    sprintf(buf, " DynamicRestart: %d", particleResetting());
    cv::putText(img, buf, cv::Point(20, 60), cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(200,0,200), 1);
    sprintf(buf, " Latency/cycle: %f [ms]", cycleLatency());
    cv::putText(img, buf, cv::Point(20, 90), cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(200,0,200), 1);
  
    cv::imshow("pepper_localizer", img);
  }  
  _force_redisplay=false;
   
}

double NAOqiLocalizer::cycleLatency() const {
  double acc=0;
  for (size_t i=0; i<_timers.size(); i++)
    acc+=_timers[i];
  return acc/_timers.size();
}


void NAOqiLocalizer::setInitialPose(float x, float y,float theta) {
  Eigen::Vector3f new_pose(x,y,theta);
  printf("Setting pose (%s): %.3f %.3f %.3f",
	 qi::to_string(qi::SteadyClock::now()).c_str(),
	 new_pose.x(),
	 new_pose.y(),
	 new_pose.z());
  
  Eigen::Isometry2f inverse_origin=v2t(_map_origin).inverse();
  Eigen::Isometry2f global_pose=v2t(new_pose);
  Eigen::Vector3f map_pose=t2v(inverse_origin*global_pose);
  setPose(map_pose);
  _restarted=true;
}

void NAOqiLocalizer::readMap(const std::string mapname){
  std::cerr << "Reading map" << mapname << std::endl;
  
  // reading map info
  SimpleYAMLParser parser;
  parser.load(mapname);
  std::cerr << "Dirname: " << dirname(strdup(mapname.c_str())) << std::endl;
  
  std::string map_image_name = parser.getValue("image");
  float res = parser.getValueAsFloat("resolution");
  float occupied_thresh = parser.getValueAsFloat("occupied_thresh");
  float free_thresh = parser.getValueAsFloat("free_thresh");
  int negate = parser.getValueAsInt("negate");
  Eigen::Vector3f new_origin = parser.getValueAsVector3f("origin");
  //Parser testing
  std::cerr << "MAP NAME: " << map_image_name << std::endl;
  std::cerr << "RESOLUTION: " << res << std::endl;
  std::cerr << "ORIGIN: " << new_origin.transpose() << std::endl;
  std::cerr << "NEGATE: " << negate << std::endl;
  std::cerr << "OCC THRESHOLD: " << occupied_thresh << std::endl;
  std::cerr << "FREE THRESHOLD: " << free_thresh << std::endl;
  std::cerr << "NON EXISTING KEY: " << parser.getValue("non_exists") << std::endl;

  std::string full_path_map_image = std::string(dirname(strdup(mapname.c_str())))+"/"+map_image_name;
  std::cerr << "Opening image" << full_path_map_image << std::endl;
  
  UnsignedCharImage map_image = cv::imread(full_path_map_image, CV_LOAD_IMAGE_GRAYSCALE);

  std::cerr << "Image read: (" << map_image.rows << "x" << map_image.cols << ")" << std::endl;
  
  setMap(map_image, res, 10, 230);
  _map_origin=new_origin;

  _restarted=true;
}
