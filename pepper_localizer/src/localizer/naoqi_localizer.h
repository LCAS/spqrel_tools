#pragma once

#include "localization_filter.h"
#include "simple_yaml_parser.h"

#include <libgen.h> 

#include <qi/session.hpp>
#include <qi/clock.hpp>

#include <thread>

using namespace std;

static const char* laserMemoryKeys[] = {
  // RIGHT LASER
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg01/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg01/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg02/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg02/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg03/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg03/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg04/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg04/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg05/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg05/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg06/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg06/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg07/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg07/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg08/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg08/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg09/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg09/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg10/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg10/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg11/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg11/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg12/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg12/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg13/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg13/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg14/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg14/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg15/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Right/Horizontal/Seg15/Y/Sensor/Value",
  // FRONT LASER
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg01/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg01/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg02/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg02/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg03/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg03/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg04/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg04/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg05/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg05/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg06/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg06/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg07/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg07/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg08/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg08/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg09/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg09/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg10/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg10/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg11/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg11/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg12/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg12/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg13/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg13/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg14/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg14/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg15/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg15/Y/Sensor/Value",
  // LEFT LASER
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg01/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg01/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg02/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg02/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg03/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg03/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg04/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg04/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg05/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg05/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg06/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg06/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg07/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg07/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg08/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg08/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg09/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg09/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg10/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg10/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg11/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg11/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg12/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg12/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg13/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg13/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg14/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg14/Y/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg15/X/Sensor/Value",
  "Device/SubDeviceList/Platform/LaserSensor/Left/Horizontal/Seg15/Y/Sensor/Value",
};





/*!
  class that implements a ROS localization node.
  It uses a particle filter with likelihood function based on a distance map
*/
class NAOqiLocalizer : public LocalizationFilter{
 public:
  EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    //! initializes the localizer 
    NAOqiLocalizer(qi::SessionPtr session);
  
  //! call this after construction if you want to have a gui
  void initGUI();
  
  //! sets/gets the maximum range of a laser, ranges further than this are ignored
  inline float forcedMaxRange() const {return _forced_max_range;}
  inline void setForcedMaxRange( float mr) {_forced_max_range=mr;}
  
  //! endpoints that are closer between each other than this threshold are suppressed
  inline float squaredEndpointDistance() const {return _squared_endpoint_distance;}
  inline void setSquaredEndpointDistance(float sd) { _squared_endpoint_distance=sd;}
  
  //! call this when all is in place, AND the map is loaded (either via direct setMap function or
  //! by calling the requestMap service)
  void subscribeServices();
  void unsubscribeServices();

  //! reads a map in yaml format
  void readMap(const std::string mapname);
  
  void setInitialPose(float x, float y,float theta);
 protected:

  qi::SessionPtr _session;

  Eigen::Vector3f _old_odom_pose; //< stores the previous odom pose, used to compute the control 
  Eigen::Vector3f _laser_pose; //< stores the laser pose from the system
  /* bool _has_laser_pose;*/
  bool _restarted;
    
  std::vector<double> _timers; //< holds the update time of the last n cycles
  size_t _last_timer_slot; // the current update cycle

  float _forced_max_range; //< max range to use in localization
  float _squared_endpoint_distance; //< max distance betweem endpoints in the laser. The ones that are closer are suppressed

  Eigen::Vector3f _map_origin;    //< world coordinates of the upper left pixel 
  
  //! converts a range scan into a vector of regularized endpoints
  //! @param endpoints: a vector2fvector containing the cartesian 
  //!                   written by the method coordinares of the regularized endpoints
  //! @paeam laser_pose: pose of the laser on the robot
  //! @param msg: the laser message to be processed
  Vector2fVector rawPointsToRobotFrame(Vector2fVector& rawPoints);

  /*
  //! publishes the particles
  void publishParticles();

  //! publishes the statistics (amcl_pose) and the transform (tf)
  void publishPose();

  //! publishes the distance between each laser endpoint and the closest point in the map
  void publishRanges();
  */
  //! handles a laser scan and updates the filter
  std::thread _servicesMonitorThread;
  void servicesMonitorThread(qi::AnyObject memory_service, qi::AnyObject motion_service);
  std::atomic<bool> _stop_thread;
  /*
  //! handles the set-pose-estimate message from outside
  //! puts all partcles in the neighborhood of the pose in msg
  void setPoseCallback(const geometry_msgs::PoseWithCovarianceStampedConstPtr& msg);

  //! triggers global localization
  bool globalLocalizationCallback(std_srvs::Empty::Request& req,
  std_srvs::Empty::Response& res);
  
  // called when the map is updated. causes some overhead
  void mapMessageCallback(const nav_msgs::OccupancyGrid& msg);
  */
  // GUI stuff
  //! callback fot the mouse, used to set the robot pose
  //! when in set_pose mode, left click sets the pose
  //! right click sets the orientation
  static void onMouse( int event, int x, int y, int, void* );
    
  //! handles the keyboard
  //!  "s": toggles setPose mode
  //!  "d": toggles map mode (distance/occupancy)
  //!  "r": toggles particle resetting (spread the particles when enterning in unknown)
  //!  "g": triggers global localization
  void handleGUIInput();

  //! computes the average computation time of the last n updates
  double cycleLatency() const;

  //! shows the gui stuff
  void handleGUIDisplay();
  bool _use_gui;           //! handled internally
  bool _show_distance_map; //! if 1 in the gui shows the distance map. (to be toggled with "d")
  bool _force_redisplay;   //! if toggled to one forces the display and sends out all messages 
  bool _set_pose;          //! set_pose mode (to be toggled with "s")
};

