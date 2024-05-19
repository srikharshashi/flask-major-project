import moviepy.editor as mp
import tempfile
import os
from PIL import Image


def upload_video_and_thumbnail(video_file, filename, storage, database, video_id,user):
    # Create a temporary file for the video
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(video_file.read())
        video_path = tmp.name

    # Generate the thumbnail
    video = mp.VideoFileClip(video_path)
    thumbnail_path = os.path.join(os.path.dirname(video_path), f'{filename}_thumbnail.jpg')
    thumbnail = Image.fromarray(video.get_frame(1))  # Get the frame at second 1
    print(thumbnail_path)
    thumbnail.save(thumbnail_path)

    # Upload the video to Firebase Storage  
    with open(video_path, "rb") as f:
        storage.child(f"videos/{video_id}/{filename}").put(f)

    # Upload the thumbnail to Firebase Storage
    with open(thumbnail_path, "rb") as f:
        storage.child(f"thumbnails/{video_id}.jpg").put(f)
    
    video.close()
    thumbnail.close()

    # Remove the temporary files
    os.remove(video_path)
    os.remove(thumbnail_path)

    # Get the video's URL
    video_url = storage.child(f"videos/{video_id}/{filename}").get_url(None)

    # Get the thumbnail's URL
    thumbnail_url = storage.child(f"thumbnails/{video_id}.jpg").get_url(None)

    # Store the video's URL and thumbnail's URL in the database
    database.child("users").child(user["uid"]).child("videos").child(video_id).child("video_url").set(video_url)
    database.child("users").child(user["uid"]).child("videos").child(video_id).child("thumbnail_url").set(thumbnail_url)
