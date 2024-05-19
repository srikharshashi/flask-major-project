import os 
def write_video_file(video_file, output_path):
    video_data = video_file.read()
    with open(output_path, 'wb') as f:
        f.write(video_data)
    file_size = os.path.getsize(output_path)
    if file_size != len(video_data):
        raise Exception('File was not written correctly')
    return output_path