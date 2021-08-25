# Change Log

This file includes a list of notable changes to this project.

## [0.5.0](https://github.com/neuralet/smart-social-distancing/releases/tag/0.5.0)
Released on 2021-02-10.

#### Added:

* Camera IDs created with the API are now generated by the controller ([#127](https://github.com/neuralet/smart-social-distancing/pull/127))
* Unitary tests for the API Router ([#105](https://github.com/neuralet/smart-social-distancing/pull/105))
* Unitary tests for the Camera Router ([#130](https://github.com/neuralet/smart-social-distancing/pull/130))
* Endpoints to define a Region of Interest in a given camera ([#131](https://github.com/neuralet/smart-social-distancing/pull/131))

#### Updated:

* Readme: Supported video formats ([#126](https://github.com/neuralet/smart-social-distancing/pull/126))
* Readme: DockerHub information ([#129](https://github.com/neuralet/smart-social-distancing/pull/129))
* Moved references from beta.lanthorn.ai to app.lanthorn.ai ([#132](https://github.com/neuralet/smart-social-distancing/pull/132))
* Readme: Added documentation on how to quickly get the processor running for a PoC ([#133](https://github.com/neuralet/smart-social-distancing/pull/133))
* Polished configs making all default IDs `0` (instead of `default` or `area0`) ([#133](https://github.com/neuralet/smart-social-distancing/pull/133))

#### Fixed:

* Broken Posenet reference on Coral ([#128](https://github.com/neuralet/smart-social-distancing/pull/128))

## [0.4.0](https://github.com/neuralet/smart-social-distancing/releases/tag/0.4.0)
Released on 2021-01-14.

#### Added:

* Backup files into S3 ([#106](https://github.com/neuralet/smart-social-distancing/pull/106))
* Yolov3 detector for x86 devices ([#103](https://github.com/neuralet/smart-social-distancing/pull/103))
* Openpifpaf and OFM face-mask classifier TensorRT support for Jetson TX2 ([#101](https://github.com/neuralet/smart-social-distancing/pull/101))
* OAuth in endpoints ([#112](https://github.com/neuralet/smart-social-distancing/pull/112))
* Measure performance ([#123](https://github.com/neuralet/smart-social-distancing/pull/123))

#### Updated:

* Screenshot logger ([#111](https://github.com/neuralet/smart-social-distancing/pull/111))
* Video live feed ([#110](https://github.com/neuralet/smart-social-distancing/pull/110))
* Readme ([#118](https://github.com/neuralet/smart-social-distancing/pull/118))
* Export endpoints ([#114](https://github.com/neuralet/smart-social-distancing/pull/114))
* Small refactor in API responses ([#120](https://github.com/neuralet/smart-social-distancing/pull/120))
* Split `config-jetson.ini` into  `config-jetson-nano.ini` and `config-jetson-tx2.ini` ([#117](https://github.com/neuralet/smart-social-distancing/pull/117))

#### Fixed:

* Fixed minor issues in classifier ([#102](https://github.com/neuralet/smart-social-distancing/pull/102))
* Fixed minor issues in occupancy metrics ([#115](https://github.com/neuralet/smart-social-distancing/pull/115))


## [0.3.0](https://github.com/neuralet/smart-social-distancing/releases/tag/0.3.0)
Released on 2020-12-22.

#### Added:

* Tracker parameters to GPU config ([#89](https://github.com/neuralet/smart-social-distancing/pull/89))
* Parameter `reboot_processor` on all endpoints that update config ([#87](https://github.com/neuralet/smart-social-distancing/pull/87))
* Enable slack notifications per entity ([#86](https://github.com/neuralet/smart-social-distancing/pull/86))
* Openpifpaf TensorRT support ([#91](https://github.com/neuralet/smart-social-distancing/pull/91))
* Global reporting ([#92](https://github.com/neuralet/smart-social-distancing/pull/92))
* Add export_all endpoint ([#94](https://github.com/neuralet/smart-social-distancing/pull/94))
* Occupancy metrics ([#97](https://github.com/neuralet/smart-social-distancing/pull/97), ([#104](https://github.com/neuralet/smart-social-distancing/pull/104))
* Allow retrieving and updating all the sections in the configuration file using the API ([#98](https://github.com/neuralet/smart-social-distancing/pull/98))

#### Updated:

* Refactor video processing pipeline ([#95](https://github.com/neuralet/smart-social-distancing/pull/95))
* Extend config api ([#98](https://github.com/neuralet/smart-social-distancing/pull/98))
* Use tracking information to calculate social distancing metrics ([#97](https://github.com/neuralet/smart-social-distancing/pull/97))
* Reports are now generated by hour ([#97](https://github.com/neuralet/smart-social-distancing/pull/97))

#### Fixed:

* Improved tracking ([#91](https://github.com/neuralet/smart-social-distancing/pull/91))
* Fixed minor issues at classifier inference ([#96](https://github.com/neuralet/smart-social-distancing/pull/96))
* Camera image endpoints capture default image ([#100](https://github.com/neuralet/smart-social-distancing/pull/100))


## [0.2.0](https://github.com/neuralet/smart-social-distancing/releases/tag/0.2.0)
Released on 2020-11-20.

#### Added:

* Support for running on x86 with GPU ([#72](https://github.com/neuralet/smart-social-distancing/pull/72))
* Endpoint to get version, device and whether the processor has been set up ([#84](https://github.com/neuralet/smart-social-distancing/pull/84))
* Endpoints to export raw data ([#74](https://github.com/neuralet/smart-social-distancing/pull/74))
* Improve fault tolerance ([#82](https://github.com/neuralet/smart-social-distancing/pull/82))

#### Updated:

* Documentation in Readme (several, mainly ([#73](https://github.com/neuralet/smart-social-distancing/pull/73))
* Refactored Endpoints to not end with / ([#76](https://github.com/neuralet/smart-social-distancing/pull/76))
* Some improvements in face mask detection like adding a label on top of bounding boxes ([#77](https://github.com/neuralet/smart-social-distancing/pull/77))
* Improved Object tracker (IOU tracker added) ([#79](https://github.com/neuralet/smart-social-distancing/pull/79))

#### Fixed:

* An error in face anonymizer when using PoseNet ([#80](https://github.com/neuralet/smart-social-distancing/pull/80), [#81](https://github.com/neuralet/smart-social-distancing/pull/81))

#### Removed:

* Deprecated frontend and ui backend ([#73](https://github.com/neuralet/smart-social-distancing/pull/73))

---

## [0.1.0](https://github.com/neuralet/smart-social-distancing/releases/tag/0.1.0)

This is the first release of the Smart Social Distancing app.
The app is dockerized and can run on Coral Dev Board, Coral USB Accelerator, Jetson Nano, x86 or Openvino.
It supports close contact detection, occupancy alerts and facemask detection on multiple video sources.

It also includes a frontend React App and a separate backend that manages some endpoints which both have been **deprecated** and will be removed in future versions.