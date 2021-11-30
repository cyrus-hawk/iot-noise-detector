import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import struct
import math
import numpy as np
import http.client
from scipy.fftpack import fftfreq, fft
import urllib.request
import scipy.io.wavfile
import json
import sys
import getopt

def print_usage(name):
    print("usage: python", name, "-l number.number.number.number:port")

def get_streaming_link(argv):
    if len(argv) == 1:
        print_usage(name = argv[0])
        sys.exit(2)

    try:
        opt_vals, args = getopt.getopt(argv[1:], 'l:', ['link='])
    except getopt.GetoptError:
        print_usage(argv[0])
        sys.exit(2)

    for opt, val in opt_vals:
        if opt in ('-l', '--link'):
            return 'http://' + val

    print_usage(argv[0])
    sys.exit(2)

streaming_time = 4 # in seconds
streaming_length = streaming_time * 4
frame_rate = 22500
number_of_frames = streaming_length * frame_rate // 4
file_location = "soundtemp.mp3"

IoT_platform_url = "uBeac's IoT platform address" #for example 'askini.hub.ubeac.io'
IoT_platform_gateway = "uBeac's gateway" # for example '/lanmic'

def get_audio(r):
    audio = r.read(frame_rate)
    for i in range(streaming_length - 1):
        audio += r.read(frame_rate)
    return audio


def get_rate_and_data(audio):
    format_float = '<' + str(number_of_frames) + 'i'
    result = struct.unpack(format_float, audio)
    abs_numbers = np.abs(np.array(result))
    max_number = np.max(abs_numbers)
    audio_data = (abs_numbers/max_number).astype(np.float32)
    scipy.io.wavfile.write(file_location, frame_rate, audio_data)
    rate, data = scipy.io.wavfile.read(file_location)        
    return rate, data

def get_amplitude(data):
    rms_amplitude = np.sqrt(np.mean(np.square(data)))
    log_of_rms_amp = 20 * math.log10(rms_amplitude)
    return -1 * log_of_rms_amp

def prep_sensor_data(id, data):
    sensor_data = {
        'id': id,
        'data': data
    }
    return sensor_data

def get_max_freq(data, rate):
    frequencies = fftfreq(data.shape[0], 1/rate)
    freqspos = frequencies[:frequencies.size // 2]
    fft_of_data = fft(data)
    fftabs = abs(fft_of_data)[:frequencies.size // 2]

    #peakfreq = np.max(fftabs) #NOTE: may produce bug
    max_idx = np.argmax(fftabs)  
    max_freq = freqspos[max_idx]     

    return max_freq, max_idx


def send_data_to_IoT_platform(sensors):
    device = [{
        'id': "Android Microphone",
        'sensors': sensors
    }]

    connection = http.client.HTTPSConnection(IoT_platform_url)
    connection.request('POST', IoT_platform_gateway, json.dumps(device))
    response = connection.getresponse()
    print(response.read().decode())

import time
time_previous = 0

def send_notification(amplitude):
    global time_previous

    time_now = time.time()

    if time_now - time_previous < 60:
        return
    elif float(amplitude['data']['Amplitude']) < 22:
        return

    time_previous = time_now

    mail_content = '''Hello,
     noise detected!!!!
     
     Cheers
    '''
    #The mail addresses and password
    sender_address = 'your@email.address'
    with open('pass.txt', 'r') as f:
        sender_pass = f.read()
    receiver_address = 'your@email.address'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Noise Detection Notification'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    #session = smtplib.SMTP_SSL('smtp.gmail.com') 
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('email notification sent')

link = get_streaming_link(sys.argv)

with urllib.request.urlopen(link) as r:
    print('the program is running')
    _ = r.read(44) # skip header
    while True:
        audio = get_audio(r)
        rate, data = get_rate_and_data(audio)        

        log_of_rms_amp = get_amplitude(data)
        
        amplitude = prep_sensor_data("Average Amplitude", {"Amplitude": str(log_of_rms_amp)})

        send_notification(amplitude) # sends an email when apmplitude is high
            
        max_freq, max_freq_idx = get_max_freq(data, rate)

        frequency = prep_sensor_data("Frequency", {"Max Frequency" : str(max_freq)})

        peak = prep_sensor_data("Max Peak", {"Amplitude" : str(max_freq_idx)})

        sensors = [amplitude, frequency, peak]  

        send_data_to_IoT_platform(sensors)
