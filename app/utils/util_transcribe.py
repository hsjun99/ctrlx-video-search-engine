import whisperx

from app.model import SegmentType, WordType
from typing import List

import torch
from pydantic import parse_obj_as


def transcribe_audio(file_path: str) -> List[SegmentType]:
    try:
        device = "cuda"
        batch_size = 32  # reduce if low on GPU mem
        # change to "int8" if low on GPU mem (may reduce accuracy)
        compute_type = "float16"
        print(1)
        # 1. Transcribe with original whisper (batched)
        model = whisperx.load_model("large-v2", device, compute_type=compute_type)
        print(2)
        audio = whisperx.load_audio(file_path)
        result = model.transcribe(audio, batch_size=batch_size)

        # delete model if low on GPU resources
        # import gc

        # gc.collect()
        # torch.cuda.empty_cache()
        # del model

        # 2. Align whisper output
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"],
            device=device,
        )
        print(3)
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False,
        )
        print(4)
        # delete model if low on GPU resources
        # import gc

        # gc.collect()
        # torch.cuda.empty_cache()
        # del model_a

        # 3. Assign speaker labels
        # diarize_model = whisperx.DiarizationPipeline(use_auth_token="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", device=device)

        # add min/max number of speakers if known
        # diarize_segments = diarize_model(audio_file)
        # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)

        # result = whisperx.assign_word_speakers(diarize_segments, result)
        # print(diarize_segments)
        # print(result["segments"]) # segments are now assigned speaker IDs

        # Extract the list of words
        # transcript = []
        segments = parse_obj_as(List[SegmentType], result["segments"])
        print(5)
        wordList: List[WordType] = []
        for segment in segments:
            for word in segment.words:
                wordList.append(word)

        for index, word in enumerate(wordList):
            if word.start is None or word.end is None:
                if index == 0:
                    wordList[index].start = 0
                    if wordList[index + 1].start is not None:
                        wordList[index].end = wordList[index + 1].start
                    else:
                        wordList[index].end = word.start + 0.05  # as fallback
                else:
                    wordList[index].start = wordList[index - 1].end
                    if index == len(wordList) - 1:
                        wordList[index].end = word.start + 0.05
                    else:
                        if wordList[index + 1].start is None:
                            wordList[index].end = wordList[index].start + 0.05
                        else:
                            wordList[index].end = wordList[index + 1].start
        print(6)
        for index, segment in enumerate(segments):
            for word in segment.words:
                if word.start is None or word.end is None:
                    word.start = wordList[index].start
                    word.end = wordList[index].end
        print(7)
        return segments
    except Exception as e:
        print(e)
