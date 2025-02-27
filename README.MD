# Kivy VOIP

## Table of Contents

- [Description](#description)
- [Plyer Implmentation](#Plyer Implmentation)
- [Server](#server)
- [Android](#android)
- [iOS](#iOS)
- [Contributing](#contributing)
- [License](#license)

## Description

Kivy VOIP is a simple, yet powerful framework designed for Kivy app developers to implement Voice Over IP (VOIP) functionality in their applications.
It simplifies the process of setting up voice communication between users, allowing developers to integrate it easily into their Kivy apps.
The main goal of this project is to provide a seamless VOIP experience, enabling direct communication between clients through an easily configurable server.
Caution must be exercised by the developer to prevent sending data to the wrong IP address or root domain.

Key features:
- Real-time voice communication.
- Easy integration with Kivy applications.
- Supports Android and iOS platforms.

## Plyer Implementation  

This project was successfully integrated into the Plyer module!  
[View Pull Request Merge](https://github.com/kivy/plyer/pull/832).  

Plyer main branch documentation for VoIP:  
[VoIP Example Documentation](https://github.com/kivy/plyer/tree/master/examples/voip)  

```sh
pip install git+https://github.com/kivy/plyer.git@master

## Server

• To use the Kivy VOIP functionality, you will need to create a server application and configure it to route data sent by clients.
For testing purposes, the node VOIP server in the repository is configured to echo data back to a connected client.
Note that any programming language could be used to create the server. Node.js was chosen due to its popularity and performance.
Here is an outline of steps to run the generic server application from the repository:
1. Download "node VOIP server.js" from the main repository.
2. If not already installed, install node.js on your operating system.
3. If not already known, discover your server's local IP address by running "ipconfig" (Windows) or "ifconfig" (Linux) in your Command Line Interface (CLI).
4. Run the following command in your CLI to run the VOIP server when desired: node "node VOIP server.js". It is also possible to run the "node VOIP server.js"
   through VS Code.

## Android

1. Download main.py and voip.py and place them in a folder that is solely used for this project.
2. Within the start_call() function, update the dst_address and dst_port arguments in main.py to match your server's local IP address and port.
   All other arguments within the function are not required but may be assigned values as desired.
3. Create a buildozer.spec file.
4. Within your buildozer.spec file, include the following permissions before compiling with Buildozer:
   INTERNET, RECORD_AUDIO, ACCESS_NETWORK_STATE, and WAKE_LOCK.
5. Compile main.py with Buildozer to incorporate pyjnius into the mobile application by default.
6. Ensure microphone permission is enabled for the compiled mobile application on your phone.
7. Ensure the node VoIP server is running.
8. Run the compiled mobile application on your Android device
9. Press the call button to hear your voice echoing back from the server.

## iOS

• The VoIP iOS framework only supports arm_64 (actual iPhone) devices by default. To use the simulator, you must load the simulator
framework in the SimulatorFramework folder instead of the one provided in the main directory of this repository.
1. Download main.py, voip.py, and Voip.framework(or SimulatorFramework/Voip.framework for iOS simulator)
   and place them in a folder that is solely used for this project.
2. Within the start_call() function, update the dst_address and dst_port arguments in main.py to match your server's local IP address and port.
   All other arguments within the function are not required but may be assigned values as desired.
3. Through kivy-ios, utilize toolchain to create a new Xcode project that references the main.py folder.
4. Open the project in Xcode and navigate to the project's directory explorer if not already selected.
5. Under resources, click yourprojectname-info to load the info.plist file of your project.
6. Hover over any description already set and press the add button to select "Privacy - Microphone Usage Description" to add microphone permission.
7. To the right of the microphone permission added, enter a brief message to explain why microphone access is needed.
   This will appear during the permission request.
8. Ensure the node VoIP server is running.
9. Run the mobile application on your iOS device through Xcode.
10. Press the call button to hear your voice echoing back from the server.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push your branch.
4. Submit a pull request.

## License

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project's voip.py file is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.
