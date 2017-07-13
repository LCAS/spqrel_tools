
import qi
import math

robotPoseKey = "NAOqiLocalizer/RobotPose"

def point2world(memory_service, point):
    
    point_world = []
    try:
        robot_pose = memory_service.getData(robotPoseKey)
        print robot_pose
        s = math.sin(robot_pose[2])
        c = math.cos(robot_pose[2])
        point_world = [robot_pose[0] + c*point[0]-s*point[1],
                       robot_pose[1] + s*point[0]+c*point[1]];
    except:
        print "Cannot read Robot Pose. Is NAOqiLocalizer running?"

    return point_world


