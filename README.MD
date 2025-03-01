# Kivy VoIP (Now Part of Plyer)

**Kivy VoIP has been fully integrated into the [Plyer](https://github.com/kivy/plyer) module and is no longer maintained as a standalone project.**  
All VoIP-related functionality is now available directly within Plyer. Developers should use **Plyer’s VoIP API** for all future implementations.

- [View the Plyer VoIP Pull Request](https://github.com/kivy/plyer/pull/832)
- [Plyer Main Branch VoIP Documentation](https://github.com/kivy/plyer/tree/master/examples/voip)

## Table of Contents

- [Description](#description)
- [Plyer Implementation](#plyer-implementation)
- [License](#license)

## Description

Kivy VoIP was a framework designed to bring **Voice Over IP (VoIP)** functionality to Kivy applications. This project has now been merged into **Plyer**, simplifying the process of setting up voice communication between users within Kivy apps.

As a result of this transition, Kivy VoIP is **no longer a separate project**. Developers should use **Plyer’s built-in VoIP API** for implementing voice communication in their Kivy applications.

### **Key Features (Now in Plyer)**
- Real-time voice communication.
- Seamless integration with Kivy applications.
- Support for Android and iOS platforms.

## Plyer Implementation  

Kivy VoIP has been successfully merged into **Plyer**, meaning all VoIP-related features are now available in Plyer’s main branch.

### **How to Install Plyer with VoIP Support**
To use the VoIP functionality, install the latest version of Plyer directly from the GitHub repository:

```sh
pip install git+https://github.com/kivy/plyer.git@master
```

## License

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project's voip.py file is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.
