"""DNA Base4 Codec — バイナリデータとDNA塩基配列(ATCG)の相互変換"""

BASE4_TO_BASE = {0: "A", 1: "T", 2: "C", 3: "G"}
BASE_TO_BASE4 = {v: k for k, v in BASE4_TO_BASE.items()}


def dna_encode(data: bytes) -> str:
    """バイトデータをDNA塩基配列にエンコードする。

    1バイト(0-255)を4桁のbase4に変換し、各桁をATCGにマッピングする。
    """
    bases: list[str] = []
    for byte in data:
        for shift in (6, 4, 2, 0):
            bases.append(BASE4_TO_BASE[(byte >> shift) & 0b11])
    return "".join(bases)


def dna_decode(seq: str) -> bytes:
    """DNA塩基配列をバイトデータにデコードする。

    塩基配列の長さは4の倍数でなければならない。
    """
    seq = seq.upper()
    if len(seq) % 4 != 0:
        raise ValueError(f"塩基配列の長さは4の倍数である必要があります (got {len(seq)})")

    result = bytearray()
    for i in range(0, len(seq), 4):
        byte = 0
        for j, base in enumerate(seq[i : i + 4]):
            if base not in BASE_TO_BASE4:
                raise ValueError(f"無効な塩基: '{base}' (position {i + j})")
            byte = (byte << 2) | BASE_TO_BASE4[base]
        result.append(byte)
    return bytes(result)
