#!/bin/bash
# uso: STORY=dormir ./fazer.sh  (voz em voices/$STORY.mp3) -> final/$STORY.mp4
set -e
BASE=${BIBLIA_BASE:-$(cd "$(dirname "$0")" && pwd)}; export BIBLIA_BASE=$BASE
cd "$BASE"
O=out_$STORY
python3 davi.py render
python3 audio.py
cd $O
STYLE=$(cd "$BASE" && python3 -c "import davi;print(getattr(davi,'MUSIC',{}).get('style',''))" 2>/dev/null | tail -1)
if [ "$STYLE" = piano ]; then MV=0.62; RATIO=2.5; else MV=0.32; RATIO=6; fi
ffmpeg -y -v error -i ../voices/$STORY.mp3 -i music.wav -i sfx.wav -filter_complex "[0:a]aresample=44100,aformat=channel_layouts=stereo,adelay=150:all=1,apad[v];[v]asplit=2[v1][vsc];[1:a]volume=$MV[m];[m][vsc]sidechaincompress=threshold=0.05:ratio=$RATIO:attack=60:release=600[md];[2:a]volume=0.75[s];[v1][md][s]amix=inputs=3:normalize=0:duration=shortest,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map "[a]" -ar 48000 mix.wav
ls s??.mp4 | sort | sed "s/.*/file '&'/" > v.txt
ffmpeg -y -v error -f concat -i v.txt -c copy video.mp4
mkdir -p ../final && ffmpeg -y -v error -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ../final/$STORY.mp4
echo "done $STORY"
