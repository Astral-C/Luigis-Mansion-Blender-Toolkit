from enum import IntFlag

class GXAttribute(IntFlag):
    PositionMatrixIndex = 0
    Tex0MatrixIndex = 1
    Tex1MatrixIndex = 2
    Tex2MatrixIndex = 3
    Tex3MatrixIndex = 4
    Tex4MatrixIndex = 5
    Tex5MatrixIndex = 6
    Tex6MatrixIndex = 7
    Tex7MatrixIndex = 8
    Position = 9
    Normal = 10
    Color0 = 11
    Color1 = 12
    Tex0 = 13
    Tex1 = 14
    Tex2 = 15
    Tex3 = 16
    Tex4 = 17
    Tex5 = 18
    Tex6 = 19
    Tex7 = 20
    PositionMatrixArray = 21
    NormalMatrixArray = 22
    TextureMatrixArray = 23
    LitMatrixArray = 24
    NormalBinormalTangent = 25
    NullAttr = 0xFF

class GXPrimitiveTypes():
    @staticmethod
    def valid_opcode(opcode):
        return opcode in  [0xB8, 0xA8, 0xB0, 0x90, 0x98, 0xA0, 0x80]