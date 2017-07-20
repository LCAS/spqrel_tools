# msface_naoqi

This is a Pepper wrapper for the [Microsoft Cognitive Services FACE API](https://www.microsoft.com/cognitive-services/en-us/face-api) based on (https://github.com/LCAS/ros_web_apis)


## Running

During initialization it active the memory `Actions/FaceRecognition/Enabled` with `true` and it is subscribed to the `Actions/FaceRecognition/Command` event. 


### Commands 

 * `camera_start` subscribe to `ALVideoDevice` and start to recive images to avoid the camera image stabilization.

 * `camera_stop`  unsubscribe to `ALVideoDevice`.

 * `addface_<NAME>` to train the largest face in the provided image with a given name. Returns a JSON structure in `Actions/FaceRecognition/Recognition` with the face attributes.

 * `detect_<identify bool>` tries to identify all the detected faces and extract attributes like "gender", "smile", and "age". Returns a JSON structure in `Actions/FaceRecognition/Recognition`. if the `identify` flag is `true` in the request, the API tries to identify all the detected faces.



