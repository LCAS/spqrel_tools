# msface_naoqi

This is a Pepper wrapper for the [Microsoft Cognitive Services FACE API](https://www.microsoft.com/cognitive-services/en-us/face-api) based on (https://github.com/LCAS/ros_web_apis)


## Running

During initialization it active the memory `Actions/FaceRecognition/Enabled` with `true` and it is subscribed to the `Actions/FaceRecognition/Command` event. 


### Commands 

 * `camera_start` subscribe to `ALVideoDevice` and start to recive images to avoid the camera image stabilization.

 * `camera_stop`  unsubscribe to `ALVideoDevice`.

 * `addface_<NAME>` to train the largest face in the provided image with a given name. Returns a JSON structure in `Actions/FaceRecognition/Recognition` with the face attributes.

 * `detect_<identify bool>` tries to identify all the detected faces and extract attributes like "gender", "smile", and "age". Returns a JSON structure in `Actions/FaceRecognition/Recognition`. if the `identify` flag is `true` in the request, the API tries to identify all the detected faces.


 * `initgroup_<namegroup>`

 * `deleteperson_<nameperson>`

 * `deleteallpersons_<namegroup>`


### Running

```
$ python init_naoqi_bridge.py --group_recognition robocup_test
```
### Usage

```
usage: init_naoqi_bridge.py [-h] [--pip PIP] [--pport PPORT] [--camera CAMERA]
                            [--outvideo OUTVIDEO]
                            [--group_recognition GROUP_RECOGNITION]
                            [--delete_group_first DELETE_GROUP_FIRST]

optional arguments:
  -h, --help            show this help message and exit
  --pip PIP             Robot IP address. On robot or Local Naoqi: use
                        '127.0.0.1'.
  --pport PPORT         Naoqi port number
  --camera CAMERA       Robot camera ID address. 0 by default
  --outvideo OUTVIDEO   Output video name output.avi
  --group_recognition GROUP_RECOGNITION
                        Name of group for recognition robocup_test
  --delete_group_first DELETE_GROUP_FIRST
                        Initialization of the group deleting all persons

```

### Result attributes

```
{
  "faces": [
    {
      "faceid": "35adb184-2c7f-4fa4-a93d-f631c3e7b966", 
      "faceinfo": {
        "gender": "male",
        "age": 38.0,
        "accessories": [], 
        "facialhair": {
          "sideburns": 0.2, 
          "moustache": 0.4, 
          "beard": 0.5
        }, 
        "hair": {
          "color": "red", 
          "confidence": 0.06
        }, 
        "smile": 0.01, 
        "glasses": "NoGlasses"
      }, 
      "name": ""
    }
  ]
}
```

