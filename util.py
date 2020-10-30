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

def rgb_to_hsv(r, g, b, a):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return [h, s, v, a]