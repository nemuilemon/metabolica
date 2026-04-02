import pytest
from lib.dna_codec import dna_encode, dna_decode


class TestDnaEncode:
    def test_single_byte_zero(self):
        assert dna_encode(b"\x00") == "AAAA"

    def test_single_byte_max(self):
        assert dna_encode(b"\xff") == "GGGG"

    def test_ascii_text(self):
        encoded = dna_encode(b"Hi")
        decoded = dna_decode(encoded)
        assert decoded == b"Hi"

    def test_empty(self):
        assert dna_encode(b"") == ""

    def test_all_base4_digits(self):
        # 0b00_01_10_11 = 0x1B = 27
        assert dna_encode(b"\x1b") == "ATCG"


class TestDnaDecode:
    def test_roundtrip(self):
        original = b"Metabolica 2026!"
        assert dna_decode(dna_encode(original)) == original

    def test_roundtrip_binary(self):
        original = bytes(range(256))
        assert dna_decode(dna_encode(original)) == original

    def test_case_insensitive(self):
        assert dna_decode("atcg") == dna_decode("ATCG")

    def test_empty(self):
        assert dna_decode("") == b""

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="4の倍数"):
            dna_decode("ATC")

    def test_invalid_base(self):
        with pytest.raises(ValueError, match="無効な塩基"):
            dna_decode("AXCG")
