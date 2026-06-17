import struct
import zlib

def read_png(filename):
    """
    Đọc file PNG, trả về (width, height, binary_mask)
    1 = đen (hình), 0 = trắng (nền).
    Hỗ trợ filter 0-4, ảnh RGBA/RGB/grayscale.
    """
    with open(filename, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError('Not a PNG file')

        width = height = None
        bit_depth = color_type = None
        raw_data = bytearray()

        while True:
            len_data = f.read(4)
            if not len_data:
                break
            length = struct.unpack('>I', len_data)[0]
            chunk_type = f.read(4)
            data = f.read(length)
            f.read(4)  # CRC

            if chunk_type == b'IHDR':
                width, height, bit_depth, color_type, compress, filter_, interlace = struct.unpack('>IIBBBBB', data)
                if compress != 0 or interlace != 0:
                    raise ValueError('Only compress=0 and interlace=0 supported')
                if bit_depth != 8:
                    raise ValueError(f'Only 8-bit depth supported, got {bit_depth}')
            elif chunk_type == b'IDAT':
                raw_data.extend(data)
            elif chunk_type == b'IEND':
                break

    try:
        img_data = zlib.decompress(raw_data)
    except zlib.error as e:
        raise ValueError(f'Decompress failed: {e}')

    # Số kênh
    if color_type == 0:      # Grayscale
        channels = 1
    elif color_type == 2:    # RGB
        channels = 3
    elif color_type == 3:    # Palette
        raise ValueError('Palette images not supported')
    elif color_type == 4:    # Grayscale + alpha
        channels = 2
    elif color_type == 6:    # RGBA
        channels = 4
    else:
        raise ValueError(f'Unsupported color type {color_type}')

    bpp = channels
    row_len = width * bpp
    offset = 0
    rows = []

    def unfilter(filter_type, row, prev_row):
        if filter_type == 0:
            return row
        elif filter_type == 1:  # Sub
            for i in range(bpp, len(row)):
                row[i] = (row[i] + row[i - bpp]) & 0xFF
            return row
        elif filter_type == 2:  # Up
            if prev_row:
                for i in range(len(row)):
                    row[i] = (row[i] + prev_row[i]) & 0xFF
            return row
        elif filter_type == 3:  # Average
            for i in range(len(row)):
                left = row[i - bpp] if i >= bpp else 0
                above = prev_row[i] if prev_row else 0
                row[i] = (row[i] + (left + above) // 2) & 0xFF
            return row
        elif filter_type == 4:  # Paeth
            for i in range(len(row)):
                left = row[i - bpp] if i >= bpp else 0
                above = prev_row[i] if prev_row else 0
                upper_left = prev_row[i - bpp] if (prev_row and i >= bpp) else 0
                p = left + above - upper_left
                pa = abs(p - left)
                pb = abs(p - above)
                pc = abs(p - upper_left)
                if pa <= pb and pa <= pc:
                    row[i] = (row[i] + left) & 0xFF
                elif pb <= pc:
                    row[i] = (row[i] + above) & 0xFF
                else:
                    row[i] = (row[i] + upper_left) & 0xFF
            return row
        else:
            raise ValueError(f'Unknown filter {filter_type}')

    prev_row = None
    for y in range(height):
        filter_byte = img_data[offset]
        offset += 1
        row = list(img_data[offset:offset + row_len])
        offset += row_len
        row = unfilter(filter_byte, row, prev_row)
        prev_row = row
        rows.append(row)

    # Chuyển sang grayscale
    gray_rows = []
    for row in rows:
        if channels == 1:
            gray = row
        elif channels == 2:
            gray = row[0::2]
        elif channels == 3:
            gray = [int(0.299*row[i] + 0.587*row[i+1] + 0.114*row[i+2])
                    for i in range(0, len(row), 3)]
        elif channels == 4:
            # Bỏ alpha, lấy từ RGB
            gray = [int(0.299*row[i] + 0.587*row[i+1] + 0.114*row[i+2])
                    for i in range(0, len(row), 4)]
        else:
            gray = row
        gray_rows.append(gray)

    return width, height, gray_rows