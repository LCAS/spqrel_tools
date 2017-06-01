## set joint angle ##
This folder contains two example programs to understand how to manipulate the joints on Pepper.
#### **Warning!!!** Be careful when manipulating joints, Pepper could fall!!! 

### setjointangle ###
This is a C++ program that allows to set the angle of a specific joint on Pepper. The syntax is:
```bash
$ ./setjointangle <PEPPER_IP> <PEPPER_PORT> joint_name angle_value
```
where `joint_name` can be one of those listed in http://doc.aldebaran.com/2-5/family/pepper_technical/joints_pep.html

### setjointangleGUI ###
This is a Python program with a small interface where joint angles can be controlled using a slider bar. To run this Python program simply do:
```bash
$ python setjointangleGUI.py --pip <PEPPER_IP> --pport <PEPPER_PORT>
```
Program arguments can be ommited in the default case (PEPPER_IP = 127.0.0.1, PEPPER_PORT = 9559)