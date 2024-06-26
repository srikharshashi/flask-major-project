import os
import subprocess
from tennis_analysis.my_infer import model_infer
BASE_PATH="/home/shashi/python-firebase-flask-login"

def convert_video(input_path, output_path):
    command = ['ffmpeg', '-i', input_path, '-vcodec', 'libx264', output_path]
    try:
        subprocess.check_call(command)
        print(f'Successfully converted video from {input_path} to {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to convert video from {input_path} to {output_path}. Error: {e}')


def write_video_file(video_file, output_path):
    video_data = video_file.read()
    with open(output_path, 'wb') as f:
        f.write(video_data)
    file_size = os.path.getsize(output_path)
    if file_size != len(video_data):
        raise Exception('File was not written correctly')
    return output_path

def util_infer(in_path,storage,db,session,video_id):
    print("In Infer method")
     # Out path
    out_path=BASE_PATH+"/outputs/"+"conv-"+f"{video_id}.webm"
    # Run detect 
    model_infer(input_video_path=in_path,output_video_path=out_path)
    print("done inference")
    # Change Codec 
    new_out=BASE_PATH+"/outputs/"+f"conv-{video_id}.webm"
    # convert_video(BASE_PATH+out_path,BASE_PATH+"/outputs/"+f"conv-{video_id}.mp4")
    print("Video Converted")
    # # Chnage out path
    # out_path="./outputs/"+f"conv-{video_id}.mp4"
    # Upload the output video to Pyrebase
    storage.child(f"output_videos/{video_id}.webm").put(new_out)   
    print("Output video uploaded to Pyrebase")

    #  Get the download URL of the output video
    video_url= storage.child(f"output_videos/{video_id}.webm").get_url(None)
    print("Video URL:", video_url)

    #  Store the video URL in Firebase Realtime Database
    db.child("users").child(session["uid"]).child("videos").child(video_id).child("processed_url").set(video_url)
    print("Video URL stored in Firebase Realtime Database")
    return 
    


    
    
# infer("inputs/b9b6b239-f882-47be-be1b-ce54a9fbe432-ip.mp4",None,None,None,None,None)