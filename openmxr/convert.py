import subprocess as sp

def convert_opus_to_wav(input_data):
    ffmpeg = 'ffmpeg'
    
    # Define the ffmpeg command
    cmd = [ffmpeg,
           '-i', 'pipe:',
           '-f', 'wav',
           'pipe:']
    
    # Create a subprocess and communicate with input from input_data
    proc = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE)
    out = proc.communicate(input=input_data)[0]
    
    # Wait for the subprocess to finish
    proc.wait()
    
    return out