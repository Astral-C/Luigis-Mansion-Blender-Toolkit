import bpy
import struct
from bStream import *
from wwlib_texture_utils import *
import time

    
def cmpr_from_blender(image):
    img_data = [[image.pixels[(y * image.size[0] + x)*4 : ((y * image.size[0] + x) * 4) + 4] for x in range(image.size[0])] for y in reversed(range(image.size[1]))]
    img_out = bStream()

    #calculate block count to ensure that we dont get any garbage data
    #img_out.write(encode_image_to_cmpr_block(img_data, None, tx, ty, BLOCK_WIDTHS[ImageFormat.CMPR], BLOCK_HEIGHTS[ImageFormat.CMPR], image.size[0], image.size[1]))

    for ty in range(0, image.size[1], 8):
        for tx in range(0, image.size[0], 8):
            img_out.fhandle.write(encode_image_to_cmpr_block(img_data, [], tx, ty, BLOCK_WIDTHS[ImageFormat.CMPR], BLOCK_HEIGHTS[ImageFormat.CMPR], image.size[0], image.size[1]))
    
    img_out.seek(0)
    return (0x0E, image.size[0], image.size[1], img_out.fhandle.read())

def rgb565_from_blender(image):
    img_data = [[image.pixels[(y * image.size[0] + x)*4 : ((y * image.size[0] + x) * 4) + 4] for x in range(image.size[0])] for y in range(image.size[1])]
    img_out = bStream()

    for ty in range(0, image.size[1], 4):
        for tx in range(0, image.size[0], 4):
            for by in range(4):
                for bx in range(4):
                    pixel = img_data[(image.size[1] - 1) - (ty + by)][(tx + bx)]
                    pixel = [int(p*255) for p in pixel]

                    img_out.writeUInt16(((pixel[0] & 0xF8) << 8) | ((pixel[1] & 0xFC) << 3) | ((pixel[2] & 0xF8) >> 3))

    img_out.seek(0)
    return (0x04, image.size[0], image.size[1], img_out.fhandle.read())

def rgb5A3_from_blender(image):
    img_data = [[image.pixels[(y * image.size[0] + x)*4 : ((y * image.size[0] + x) * 4) + 4] for x in range(image.size[0])] for y in range(image.size[1])]
    img_out = bStream()

    for ty in range(0, image.size[1], 4):
        for tx in range(0, image.size[0], 4):
            for by in range(4):
                for bx in range(4):
                    pixel = img_data[(image.size[1] - 1) - (ty + by)][(tx + bx)]
                    pixel = [int(p*255) for p in pixel]

                    if(pixel[3] == 255): # use rgb555 mode
                        img_out.writeUInt16(0x8000 | ((pixel[0] & 0xF8) << 7) | ((pixel[1] & 0xF8) << 2) | ((pixel[2] & 0xF8) >> 3))
                    else:
                        img_out.writeUInt16(((pixel[3] & 0xE0) << 8) | ((pixel[0] & 0xF0) << 4) | (pixel[1] & 0xF0) | (pixel[2] >> 4))


    img_out.seek(0)
    return (0x05, image.size[0], image.size[1], img_out.fhandle.read())

class Material():
    wrap_modes = ['CLAMP','REPEAT','MIRROR']
    def __init__(self, texindex, material):
        self.texture_index = texindex
        self.u = self.wrap_modes.index(material.bin_wrap_mode_u)
        self.v = self.wrap_modes.index(material.bin_wrap_mode_v)
        self.mat = material

    def write(self, stream):
        stream.writeInt16(self.texture_index)
        stream.writeInt16(-1)
        stream.writeUInt8(self.u)
        stream.writeUInt8(self.v)
        flags = 0
        flags |= (self.mat.bin_shader_sampler_bitflag_1 << 1)
        flags |= (self.mat.bin_shader_sampler_bitflag_2 << 2)
        flags |= (self.mat.bin_shader_sampler_bitflag_3 << 3)
        flags |= (self.mat.bin_shader_sampler_bitflag_4 << 4)
        flags |= (self.mat.bin_shader_sampler_bitflag_5 << 5)
        flags |= (self.mat.bin_shader_sampler_bitflag_6 << 6)
        flags |= (self.mat.bin_shader_sampler_bitflag_7 << 7)
        flags |= (self.mat.bin_shader_sampler_bitflag_8 << 8)
        flags |= (self.mat.bin_shader_sampler_bitflag_9 << 9)
        flags |= (self.mat.bin_shader_sampler_bitflag_10 << 10)
        flags |= (self.mat.bin_shader_sampler_bitflag_11 << 11)
        flags |= (self.mat.bin_shader_sampler_bitflag_12 << 12)
        flags |= (self.mat.bin_shader_sampler_bitflag_13 << 13)
        flags |= (self.mat.bin_shader_sampler_bitflag_14 << 14)
        flags |= (self.mat.bin_shader_sampler_bitflag_15 << 15)
        flags |= (self.mat.bin_shader_sampler_bitflag_16 << 16)
        stream.writeUInt16(0)
        stream.pad(12)

class Shader():
    def __init__(self, material, material_indices, cur_index, out_indices):
        tex = None

        if(material.use_nodes and len(material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].links) > 0):
            print(f"Setting up Material {material.name}, uses nodes {material.use_nodes}, input type {material.node_tree.nodes[0].inputs[0].links[0].from_node.type}")
            tex = material.node_tree.nodes.get("Principled BSDF").inputs[0].links[0].from_node.image
        
        self.bump_index = -1
        self.diffuse_index = -1
        #force for the moment
        self.tint = (int(material.bin_shader_tint[0]*255) << 24 | int(material.bin_shader_tint[1]*255) << 16 | int(material.bin_shader_tint[2]*255) << 8 | int(material.bin_shader_tint[3]*255))
        self.unk1 = material.bin_shader_unk1
        self.unk2 = material.bin_shader_unk2
        self.unk3 = material.bin_shader_unk3

        #TODO: bumpmaps?
        #if(material.bump_texname):
        #    self.bump_index = textures.material_indices[material.bump_texname]
        
        if(tex is not None):
            self.diffuse_index = material_indices[material.name]
        
        out_indices[material.name] = cur_index
        
        print("Bump Map {0}, Diffuse Map {1}, Tint {2}".format(self.bump_index, self.diffuse_index, hex(self.tint)))

    def write(self, stream):
        stream.writeUInt8(self.unk1)
        stream.writeUInt8(self.unk2)
        stream.writeUInt8(self.unk3)
        stream.writeUInt32(self.tint)
        stream.pad(1)
        stream.writeInt16(self.diffuse_index)
        stream.writeInt16(self.bump_index)

        #demolisher support
        for x in range(6):
            stream.writeInt16(-1)

        stream.writeInt16(0)
        stream.writeInt16(-1)
        for x in range(6):
            stream.writeInt16(0)

class ShaderManager():
    def __init__(self, material_indices, used_materials):
        self.shader_indices = {}
        self.shaders = [Shader(used_materials[x], material_indices, x, self.shader_indices) for x in range(len(used_materials))]

    def getShaderIndex(self, name):
        print(f"Looking for shader {name} out of shaders {self.shader_indices}")
        return (self.shader_indices[name] if name in self.shader_indices else -1)

    def writeShaders(self, stream):
        for shader in self.shaders:
            shader.write(stream)

class TextureManager():
    def __init__(self, materials_used):
        #TODO: Massive improvements need to be made here, this system works but it seems very inefficient.
        self.textures = []
        self.materials = []
        self.texture_indices = {}
        self.material_indices = {}
        matindex = 0
        texindex = 0

        for material in materials_used:
            if(material.use_nodes):
                tex = None
                if(len(material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].links) > 0):
                    tex = material.node_tree.nodes.get("Principled BSDF").inputs[0].links[0].from_node.image
                    texname = tex.name.split('.')[0]

                    if(texname in self.texture_indices):
                        self.material_indices[material.name] = matindex
                        self.materials.append(Material(self.texture_indices[texname] , material))
                        matindex += 1
                        continue

                    if(material.gx_img_type == 'CMPR'):
                        self.textures.append(cmpr_from_blender(tex))
                    elif(material.gx_img_type == 'RGB565'):
                        self.textures.append(rgb565_from_blender(tex))
                    elif(material.gx_img_type == 'RGB5A3'):
                        self.textures.append(rgb5A3_from_blender(tex))

                    self.texture_indices[texname] = texindex
                    self.material_indices[material.name] = matindex
                    self.materials.append(Material(texindex, material))
                    texindex += 1
                    matindex += 1

                else:
                    self.material_indices[material.name] = matindex
                    self.materials.append(Material(-1, material))
                    matindex += 1

            #else:
            #    self.materials.append(Material(texindex))
            #    texindex += 1   

            #if(material.bump_texname):
            #    self.textures.append(ConvertTexture(material.bump_texname))
            #    self.material_indices[material.bump_texname] = texindex
            #    self.materials.append(Material(texindex))
            #    texindex += 1


    def writeMaterials(self, stream):
        for material in self.materials:
            material.write(stream)
            
    def writeTextures(self, stream):
        header_section = bStream()
        data_section = bStream()
        header_size = bStream.padTo32Delta(0xC*len(self.textures)) + (0xC*len(self.textures))
        
        texture_offsets = []
        for texture in self.textures:
            texture_offsets.append(data_section.tell())
            data_section.write(texture[3])

        for x in range(0, len(texture_offsets)):
            header_section.write(struct.pack(">HHBBHI", self.textures[x][1], self.textures[x][2], self.textures[x][0], 0, 0, texture_offsets[x] + header_size))
        
        header_section.padTo32(header_section.tell())
        header_section.seek(0)
        data_section.seek(0)
        stream.write(header_section.fhandle.read())
        stream.write(data_section.fhandle.read())
        header_section.close()
        data_section.close()
