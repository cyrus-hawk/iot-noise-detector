# IoT Noise Detector

This is the underlying code that processes the sound data that is being streamed by the sound detector, that is placed outside a room or house and connected to the local network. The result of the analysis is sent to an IoT cloud platform for visualization. SMTP protocol is used to notify the user about the detected sound via provided email credentials.

# Video Demonstration
The following is the presentation of the code in action:

[![Watch the presentation](https://img.youtube.com/vi/AyNAi1XYQ00/hqdefault.jpg)](https://youtu.be/AyNAi1XYQ00)

# How to use this repo?
After cloning the repo, open up the file sound_detector.py and fill the proper information for the following variables:

- IoT_platform_url
- IoT_platform_gateway
- sender_address
- receiver_address

After that, you need to install LANmic on your phone, and then turn it on. It will give an ip address that will be used with this application. Run the application like the following by the provided ip address by the LANmic.

`
python sound_detector.py -l 1.2.3.4:5678
`

After the program runs successfully, it should print a message on the terminal stating: "the program is running"

Then, if you make some loud noise, the program sends a notification to the provided email address. Simultaneously, the result of the analysis by the program is also sent to the IoT cloud platform.
