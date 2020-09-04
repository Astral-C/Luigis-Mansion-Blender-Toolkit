def to_triangles(indices, type):
    new_indices = []
    if(type == 0x90):
        new_indices = [indices]
    if(type == 0x98):
        for x in range(2, len(indices)):
            even = x % 2 != 0
            tri = [indices[x-2], indices[x] if even else indices[x-1], indices[x-1] if even else indices[x]]
            if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
                new_indices.append(tri)
    #0xA0
    if(type == 0xA0):
        for x in range(1, len(indices)):
            tri[indices[x], indices[x + 1], 0]
            if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
                new_indices.append(tri)

    if(type == 0x80):
        for x in range(0, (len(indices) // 4) // 2):
            tri[indices[x], indices[x + 1], [x + 2]]
            if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
                new_indices.append(tri)

    return new_indices

def to_triangles_uv(indices, type):
    new_indices = []
    if(type == 0x90):
        new_indices = [indices]
    if(type == 0x98):
        for x in range(2, len(indices)):
            even = x % 2 != 0
            tri = [indices[x-2], indices[x] if even else indices[x-1], indices[x-1] if even else indices[x]]
            #if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
            new_indices.append(tri)
    #0xA0
    if(type == 0xA0):
        for x in range(1, len(indices)):
            tri[indices[x], indices[x + 1], 0]
            #if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
            new_indices.append(tri)

    if(type == 0x80):
        for x in range(0, (len(indices) // 4) // 2):
            tri[indices[x], indices[x + 1], [x + 2]]
            #if(tri[0] != tri[1] and tri[1] != tri[2] and tri[2] != tri[0]):
            new_indices.append(tri)

    return new_indices