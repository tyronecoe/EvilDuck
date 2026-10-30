#!/usr/bin/env python3
"""Inspect an explicitly supplied synthetic-only DS3 capture receipt; no device I/O."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

MARKERS = (0x1234, 0x00ff, 0x0100)
GROUPS = ('lower', 'upper', 'number', 'special')
PROPERTIES = ('$_RANDOM_LOWER_LETTER_KEYCODE', '$_RANDOM_UPPER_LETTER_KEYCODE',
              '$_RANDOM_NUMBER_KEYCODE', '$_RANDOM_SPECIAL_KEYCODE')
REQUIRED = ('device_model', 'device_firmware', 'compiler_id', 'language_map_sha256',
            'source_sha256', 'compiled_sha256', 'host_os', 'host_layout',
            'caps_lock', 'authenticity_limitations', 'run_id')


class InvalidReceipt(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise InvalidReceipt(code)


def calibration(raw):
    require(len(raw) == 6, 'UNSUPPORTED_CALIBRATION_LENGTH')
    matches = [order for order in ('little', 'big')
               if raw == b''.join(v.to_bytes(2, order) for v in MARKERS)]
    require(len(matches) == 1, 'AMBIGUOUS_OR_UNSUPPORTED_CALIBRATION')
    return matches[0]


def us_report(character):
    """Independent US keyboard-page printable table, not imported from the prototype."""
    if 'a' <= character <= 'z':
        return (0, ord(character) - ord('a') + 4)
    if 'A' <= character <= 'Z':
        return (2, ord(character) - ord('A') + 4)
    if character in '1234567890':
        return (0, '1234567890'.index(character) + 0x1e)
    if character in '!@#$%^&*()':
        return (2, '!@#$%^&*()'.index(character) + 0x1e)
    if character == ' ':
        return (0, 0x2c)
    plain, shifted = '-=[]\\;\'`,./', '_+{}|:"~<>?'
    usages = (0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38)
    if character in plain:
        return (0, usages[plain.index(character)])
    if character in shifted:
        return (2, usages[shifted.index(character)])
    raise InvalidReceipt('UNSUPPORTED_VISIBLE_CHARACTER')


def inspect(receipt):
    require(isinstance(receipt, dict), 'RECEIPT_NOT_OBJECT')
    require(receipt.get('format') == 'synthetic-ds3-reference-capture-v1', 'UNSUPPORTED_FORMAT')
    metadata = receipt.get('metadata')
    require(isinstance(metadata, dict), 'MISSING_METADATA')
    for key in REQUIRED:
        require(key in metadata, 'MISSING_METADATA_' + key)
        if key != 'caps_lock':
            require(isinstance(metadata[key], str) and 0 < len(metadata[key]) <= 256,
                    'INVALID_METADATA_' + key)
    for key in ('language_map_sha256', 'source_sha256', 'compiled_sha256'):
        require(re.fullmatch('[0-9a-f]{64}', metadata[key]) is not None, 'INVALID_HASH_' + key)
    require(metadata['host_layout'] == 'US' and metadata['caps_lock'] is False,
            'UNSUPPORTED_HOST_CONTEXT')
    require(receipt.get('synthetic_data_only') is True, 'SYNTHETIC_ONLY_CONFIRMATION_REQUIRED')
    offset = receipt.get('append_offset')
    require(type(offset) is int and 0 <= offset <= 0x7fffffff, 'INVALID_APPEND_OFFSET')
    encoded = receipt.get('capture_hex')
    require(isinstance(encoded, str) and re.fullmatch('[0-9a-fA-F]*', encoded) is not None,
            'INVALID_CAPTURE_HEX')
    require(len(encoded) <= 4096 and len(encoded) % 2 == 0, 'CAPTURE_SIZE_LIMIT')
    raw = bytes.fromhex(encoded)
    require(type(receipt.get('capture_length')) is int and receipt['capture_length'] == len(raw),
            'CAPTURE_LENGTH_MISMATCH')
    require(receipt.get('capture_sha256') == hashlib.sha256(raw).hexdigest(), 'CAPTURE_HASH_MISMATCH')
    mode = receipt.get('mode')
    if mode == 'calibration':
        order = calibration(raw)
        return dict(status='CALIBRATED_SELECTED_BYTES_ONLY', byte_order=order,
                    width_bytes=2, official_runtime_executed_by_tool=False,
                    device_authenticity_verified=False, canonical_contract_established=False)
    require(mode == 'four-groups', 'UNSUPPORTED_MODE')
    # 6-byte prefix + four groups of six uint16 observations + 6-byte suffix.
    require(len(raw) == 60, 'UNSUPPORTED_CAPTURE_LENGTH')
    order = calibration(raw[:6])
    require(raw[-6:] == raw[:6], 'TRAILING_CALIBRATION_MISMATCH')
    observations = receipt.get('observations')
    require(isinstance(observations, list) and len(observations) == 4, 'MISSING_GROUP_OBSERVATIONS')
    results = []
    for i, group in enumerate(GROUPS):
        observation = observations[i]
        require(isinstance(observation, dict) and observation.get('group') == group and
                observation.get('property') == PROPERTIES[i], 'WRONG_GROUP_ORDER_OR_PROPERTY')
        pair = observation.get('visible_pair')
        require(isinstance(pair, str) and len(pair) == 2 and all(32 <= ord(c) <= 126 for c in pair),
                'MISSING_OR_UNSUPPORTED_VISIBLE_PAIR')
        require(isinstance(observation.get('visible_evidence_id'), str) and
                0 < len(observation['visible_evidence_id']) <= 256, 'MISSING_VISIBLE_EVIDENCE_ID')
        values = [int.from_bytes(raw[6 + i * 12 + j:8 + i * 12 + j], order)
                  for j in range(0, 12, 2)]
        original = values[0::2]
        copied = values[1::2]
        expected = [us_report(c) for c in pair]
        h1 = [(value >> 8, value & 255) for value in copied[:2]]
        h2 = [(value & 255, value >> 8) for value in copied[:2]]
        results.append(dict(group=group, property=PROPERTIES[i],
                            values=dict(before_original=values[0], before_copy=values[1],
                                        after_first_original=values[2], after_first_copy=values[3],
                                        after_second_original=values[4], after_second_copy=values[5]),
                            copy_matches_before=original[0] == copied[0],
                            original_unchanged=len(set(original)) == 1,
                            copy_unchanged=len(set(copied)) == 1,
                            repeated_visible_character=pair[0] == pair[1],
                            h1_matches_text_derived_us_reports=h1 == expected,
                            h2_matches_text_derived_us_reports=h2 == expected,
                            ascii_values_match=[copied[j] == ord(pair[j]) for j in range(2)],
                            table_index_or_tagged='UNRESOLVED; requires a specified runtime mapping',
                            official_runtime_value=None))
    return dict(status='CAPTURE_PARSED_NOT_AUTHENTICATED', byte_order=order,
                selected_capture_bytes=len(raw), groups=results,
                official_runtime_executed_by_tool=False, device_authenticity_verified=False,
                canonical_contract_established=False,
                limitation='Text-derived US reports are conditional expectations, not captured HID reports; '
                           'owner metadata does not attest a genuine device or universal runtime behavior.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=pathlib.Path, required=True,
                        help='Explicit synthetic-only JSON receipt, never an original loot file')
    args = parser.parse_args()
    try:
        require(args.receipt.is_file() and not args.receipt.is_symlink() and
                args.receipt.stat().st_size <= 32768, 'INVALID_RECEIPT_FILE')
        with args.receipt.open('rb') as handle:
            encoded = handle.read(32769)
        require(len(encoded) <= 32768, 'RECEIPT_SIZE_LIMIT')
        result = inspect(json.loads(encoded.decode('utf-8')))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(json.dumps(dict(status='REJECTED', reason='INVALID_OR_UNSUPPORTED_SYNTHETIC_RECEIPT')))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
