def timecode_to_float(timecode: str) -> float:
    h, m, s = timecode.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)
