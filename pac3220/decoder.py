"""Decode two Modbus 16-bit registers as IEEE-754 Float32."""

import struct


def decode_float32(registers, word_order="ABCD"):
    if len(registers) != 2:
        raise ValueError(
            f"Float32 needs exactly 2 registers; received {len(registers)}"
        )

    first, second = registers

    if word_order == "ABCD":
        ordered_words = (first, second)
    elif word_order == "CDAB":
        ordered_words = (second, first)
    else:
        raise ValueError(
            "Unsupported FLOAT_WORD_ORDER. Use 'ABCD' or 'CDAB'."
        )

    raw_bytes = struct.pack(">HH", *ordered_words)
    return struct.unpack(">f", raw_bytes)[0]
