"""Package identical-format PNGs without delta-frame or alpha-blend optimization."""
import struct,zlib
from pathlib import Path

SIGNATURE=b'\x89PNG\r\n\x1a\n'


def chunks(path):
    data=path.read_bytes();assert data[:8]==SIGNATURE
    offset=8
    while offset<len(data):
        length=struct.unpack_from('>I',data,offset)[0]
        kind=data[offset+4:offset+8];payload=data[offset+8:offset+8+length]
        assert zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from('>I',data,offset+8+length)[0]
        yield kind,payload
        offset+=length+12


def pack(folder:Path,output:Path,count:int,fps:int,plays:int=0):
    first=list(chunks(folder/'frame_0001.png'))
    header=next(data for kind,data in first if kind==b'IHDR')
    width,height=struct.unpack_from('>II',header)
    shared=[(kind,data) for kind,data in first if kind in (b'PLTE',b'tRNS',b'sRGB',b'gAMA',b'cHRM')]
    temp=output.with_suffix('.tmp');sequence=0
    with temp.open('wb') as stream:
        stream.write(SIGNATURE)
        def emit(kind,data):
            stream.write(struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff))
        emit(b'IHDR',header)
        for kind,data in shared:emit(kind,data)
        emit(b'acTL',struct.pack('>II',count,plays))
        for number in range(1,count+1):
            source=list(chunks(folder/f'frame_{number:04d}.png'))
            assert next(data for kind,data in source if kind==b'IHDR')==header
            assert [(kind,data) for kind,data in source if kind in (b'PLTE',b'tRNS',b'sRGB',b'gAMA',b'cHRM')]==shared
            emit(b'fcTL',struct.pack('>IIIIIHHBB',sequence,width,height,0,0,1,fps,0,0));sequence+=1
            for kind,data in source:
                if kind!=b'IDAT':continue
                if number==1:emit(b'IDAT',data)
                else:emit(b'fdAT',struct.pack('>I',sequence)+data);sequence+=1
        emit(b'IEND',b'')
    temp.replace(output)
