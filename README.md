Purpose: to codify a workflow of converting a source video-file to a preservation-format video-file.

One of the important flags to give the `ffmpeg` conversion-command is `-pix_fmt`. That's depending on the source file.

This code runs `ffprobe` to get the information about the source file and then suggests the best `-pix_fmt` flag to use.