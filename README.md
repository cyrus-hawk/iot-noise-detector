# This is the implementation code for the IoT project for the 2nd period of the autumn semester 2021

## How to use this repo?
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