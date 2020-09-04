import bpy
import struct
import squish
from bStream import *

def compress_block(image, imageData, tile_x, tile_y, block_x, block_y):
    rgba = [0 for x in range(64)]
    mask = 0

    for y in range(4):
        if(tile_y + block_y + y < len(imageData)):    
            for x in range(4):
                if(tile_x + block_x + x < len(imageData[0])):
                    #print(f"Writing pixel in tile [{tile_x}, {tile_y}] block [{bx}, {by}] at data at {x} {y}")
                    index = (y * 4) + x
                    mask |= (1 << index)
                    localIndex = 4 * index
                    pixel = imageData[(image.size[1] - 1) - (tile_y + block_y + y)][(tile_x + block_x + x)]

                    if(type(pixel) != int):
                        rgba[localIndex + 0] = int(pixel[0] * 255)
                        rgba[localIndex + 1] = int(pixel[1] * 255)
                        rgba[localIndex + 2] = int(pixel[2] * 255)
                        rgba[localIndex + 3] = int(pixel[3] * 255 if len(pixel) == 4 else 0xFF) #just in case alpha is not enabled
    
    return squish.compressMasked(bytes(rgba), mask, squish.DXT1)

def cmpr_from_blender(image):
    img_data = [[image.pixels[(y * image.size[0] + x)*4 : ((y * image.size[0] + x) * 4) + 4] for x in range(image.size[0])] for y in range(image.size[1])]
    

    img_out = bStream()

    for ty in range(0, image.size[1], 8):
        for tx in range(0, image.size[0], 8):
            for by in range(0, 8, 4):
                for bx in range(0, 8, 4):
                    img_out.write(compress_block(image, img_data, tx, ty, bx, by))

    img_out.seek(0)
    return (image.size[0], image.size[1], img_out.fhandle.read())

class Material():
    wrap_modes = {'CLAMP':0,'REPEAT':1,'MIRROR':2}
    def __init__(self, texindex, material):
        self.texture_index = texindex
        # These should be something user can set
        # for now, though, no.
        self.u = self.wrap_modes[material.bin_wrap_mode_u]
        self.v = self.wrap_modes[material.bin_wrap_mode_v]

    def write(self, stream):
        stream.writeInt16(self.texture_index)
        stream.writeInt16(-1)
        stream.writeUInt8(self.u)
        stream.writeUInt8(self.v)
        stream.writeUInt16(0)
        stream.pad(12)

class Shader():
    def __init__(self, material, material_indices, cur_index, out_indices):
        # Generate tint color from the diffuse color if it exists

        tex = None

        print(f"Setting up Material {material.name}, uses nodes {material.use_nodes}, input type {material.node_tree.nodes[0].inputs[0].links[0].from_node.type}")
        if(material.use_nodes and not (material.node_tree.nodes[0].inputs[0].links[0].from_node.type == "BSDF_PRINCIPLED")):
            tex = material.node_tree.nodes[0].inputs[0].links[0].from_node.image
        
        self.bump_index = -1
        self.diffuse_index = -1
        self.tint =  (int(material.bin_shader_tint[0]*255) << 24 | int(material.bin_shader_tint[1]*255) << 16 | int(material.bin_shader_tint[2]*255) << 8 | 0xFF)
        
        #TODO: bumpmaps?
        #if(material.bump_texname):
        #    self.bump_index = textures.material_indices[material.bump_texname]
        
        if(tex is not None):
            self.diffuse_index = material_indices[tex.name]
            out_indices[material.name] = cur_index
        
        print("Bump Map {0}, Diffuse Map {1}, Tint {2}".format(self.bump_index, self.diffuse_index, hex(self.tint)))

    def write(self, stream):
        stream.writeUInt8(1)
        stream.writeUInt8(1)
        stream.writeUInt8(1)
        stream.writeUInt32(self.tint)
        stream.pad(1)
        stream.writeInt16(self.diffuse_index)
        stream.writeInt16(self.bump_index)

        #demolisher support
        for x in range(6):
            stream.writeInt16(-1)

        stream.writeInt16(0)
        for x in range(7):
            stream.writeInt16(-1)

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
        self.textures = []
        self.materials = []
        self.material_indices = {}
        texindex = 0

        for material in materials_used:
            if(material.use_nodes and not (material.node_tree.nodes[0].inputs[0].links[0].from_node.type == "BSDF_PRINCIPLED")):
                #print(f"Converting Material wth From Node {material.node_tree.nodes[0].inputs[0].links[0].from_node.type}")
                tex = material.node_tree.nodes[0].inputs[0].links[0].from_node.image
                if(tex == None):
                    continue # What the fuck?
                self.textures.append(cmpr_from_blender(tex))
                self.material_indices[tex.name] = texindex
                self.materials.append(Material(texindex, material))
                texindex += 1

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
            data_section.write(texture[2])

        for x in range(0, len(texture_offsets)):
            header_section.write(struct.pack(">HHBBHI", self.textures[x][0], self.textures[x][1], 0x0E, 0, 0, texture_offsets[x] + header_size))
        
        header_section.padTo32(header_section.tell())
        header_section.seek(0)
        data_section.seek(0)
        stream.write(header_section.fhandle.read())
        stream.write(data_section.fhandle.read())
        header_section.close()
        data_section.close()
