import bpy
import struct
import squish

class gx_texture():

    @staticmethod
    def cfrom_rgb565(color):
        r = ((color >> 8) & 0xF8) | ((color >> 11) & 0x7)
        g = ((color >> 3) & 0xFC) | ((color >> 5) & 0x3)
        b = ((color << 3) & 0xF8) | (color & 0x7)
        return (r, g, b, 0xFF)

    @staticmethod
    def bi_from_rgb565(stream, w, h, offset, tex_index):
        stream.seek(offset)
        img = bpy.data.images.new("IMG{}".format(tex_index), width=w, height=h, alpha=True, float_buffer=False)

        pixels = [None] * w * h
        for ty in range(0, h, 4):
            for tx in range(0, w, 4):
                for by in range(4):
                    for bx in range(4):
                        color = gx_texture.cfrom_rgb565(stream.readUInt16())
                        pixels[(ty + by) * w + (tx + bx)] = color
        
        img.pixels = [chan for px in pixels for chan in px]
        return img

    @staticmethod
    def bi_from_cmpr(stream, w, h, offset, tex_index):
        stream.seek(offset)
        img = bpy.data.images.new("IMG{}".format(tex_index), width=w, height=h, alpha=True, float_buffer=False)
        pixels = [None] * w * h

        for ty in range(0, h, 8):
            for tx in range(0, w, 8):
                for by in range(0, 8, 4):
                    for bx in range(0, 8, 4):
                        block = stream.fhandle.read(8)
                        rgba = struct.unpack('>IIIIIIIIIIIIIIII', squish.decompress(block, squish.DXT1))

                        for y in range(4):
                            for x in range(4):
                                if((ty + by + y) < h and (tx + bx + (3-x)) < w):
                                    r = ((rgba[(y * 4 + x)] >> 24) & 0xFF) / 255
                                    g = ((rgba[(y * 4 + x)] >> 16) & 0xFF) / 255
                                    b = ((rgba[(y * 4 + x)] >> 8) & 0xFF) / 255
                                    a = (rgba[(y * 4 + x)] & 0xFF) / 255
                                    pixels[(ty + by + y) * w + (tx + bx + (3-x))] = [r, g, b, a]
        
        img.pixels = [chan for px in pixels for chan in px]
        return img