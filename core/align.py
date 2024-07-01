# v2 automation

# import os
# from moviepy.editor import VideoFileClip, AudioFileClip
#
# import audalign as ad  # https://github.com/benfmiller/audalign
# from pydub import AudioSegment
#
# # TODO: create wav sound file from ffmpeg in assets/sounds of the video file
# # call(["ffmpeg", "-i", "../assets/videos/" + ___, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
# #       "../assets/sounds/" + ___])
#
# video_dir = "../assets/videos/"
# sounds_dir = "../assets/sounds/"
# aligned_dir = "../assets/sounds/aligned/"
# audio_file_name = "Both.wav"
#
# # cor_spec_rec = ad.CorrelationSpectrogramRecognizer()
# # cor_spec_rec.config.num_processors = 4
# # results = ad.align(sounds_dir,
# #                    destination_path=aligned_dir,
# #                    recognizer=cor_spec_rec)
#
# correlation_rec = ad.CorrelationRecognizer()
# correlation_rec.config.num_processors = 4
# results = ad.align(sounds_dir,
#                    destination_path=aligned_dir,
#                    recognizer=correlation_rec)
# fine_results = ad.fine_align(
#     results,
#     recognizer=correlation_rec,
# )
#
# fine_results_map = {}
# for k, v in fine_results.items():
#     # Iterate through all files in the directory
#     for index, filename in enumerate(os.listdir(aligned_dir)):
#         if filename == k:
#             fine_results_map[k] = v
#
# for index, filename in enumerate(os.listdir(aligned_dir)):
#     # Define the full file path
#     file_path = os.path.join(aligned_dir, filename)
#     os.remove(file_path)  # Delete the file
#
# offset_map = {}
# for k, v in fine_results_map.items():
#     if audio_file_name not in k:
#         offset_map[k] = v - fine_results_map[audio_file_name]
#
# print("offset map", offset_map)
#
# for k, v in offset_map.items():
#     video_name = k.split(".")[0]
#
#     for index, filename in enumerate(os.listdir(video_dir)):
#         if video_name in filename:
#             video_path = os.path.join(video_dir, filename)
#             video = VideoFileClip(video_path)
#
#             if v < 0:
#                 # attach audio_file to -v timestamp
#                 start_time = -v
#                 trimmed_video = video.subclip(start_time)
#
#                 # Load the audio file
#                 audio_path = os.path.join(sounds_dir, audio_file_name)
#                 adjusted_audio_clip = AudioFileClip(audio_path)
#
#                 # Set the audio of the trimmed video to the adjusted audio
#                 video_with_new_audio = trimmed_video.set_audio(adjusted_audio_clip)
#
#                 # Save the final video
#                 output_path = os.path.join(video_dir, f"final_{filename}")
#                 video_with_new_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')
#             elif v > 0:
#                 # add empty frames +v timestamp. attach audio_file
#                 pass
#             else:
#                 pass
