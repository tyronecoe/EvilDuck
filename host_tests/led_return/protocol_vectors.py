"""Fixed fake-data reference vectors only; no host APIs, network or device access."""
import binascii,json
MESSAGE=b'EVILDUCK TEST 123'
def frame():
 body=bytes([len(MESSAGE)])+MESSAGE
 return b'\0EDR1'+body+binascii.crc_hqx(body,0xffff).to_bytes(2,'big')
if __name__=='__main__':print(json.dumps(dict(message=MESSAGE.decode(),payload_bytes=len(MESSAGE),frame_hex=frame().hex(),bit_order='MSB first',crc='CRC16-CCITT-FALSE over length+payload'),indent=2))
