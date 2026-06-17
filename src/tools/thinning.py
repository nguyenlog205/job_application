def zhang_suen_thin(binary):
    img = [row[:] for row in binary]
    h, w = len(img), len(img[0])
    changed = True

    while changed:
        changed = False

        # Step 1
        markers = []
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if img[y][x] == 1:
                    p2 = img[y-1][x]
                    p3 = img[y-1][x+1]
                    p4 = img[y][x+1]
                    p5 = img[y+1][x+1]
                    p6 = img[y+1][x]
                    p7 = img[y+1][x-1]
                    p8 = img[y][x-1]
                    p9 = img[y-1][x-1]
                    neigh = [p2, p3, p4, p5, p6, p7, p8, p9]
                    A = sum(1 for i in range(8) if neigh[i] == 0 and neigh[(i+1)%8] == 1)
                    B = sum(neigh)
                    if 2 <= B <= 6 and A == 1:
                        if p2 * p4 * p6 == 0 and p4 * p6 * p8 == 0:
                            markers.append((x, y))
        for x, y in markers:
            img[y][x] = 0
            changed = True

        # Step 2
        markers = []
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if img[y][x] == 1:
                    p2 = img[y-1][x]
                    p3 = img[y-1][x+1]
                    p4 = img[y][x+1]
                    p5 = img[y+1][x+1]
                    p6 = img[y+1][x]
                    p7 = img[y+1][x-1]
                    p8 = img[y][x-1]
                    p9 = img[y-1][x-1]
                    neigh = [p2, p3, p4, p5, p6, p7, p8, p9]
                    A = sum(1 for i in range(8) if neigh[i] == 0 and neigh[(i+1)%8] == 1)
                    B = sum(neigh)
                    if 2 <= B <= 6 and A == 1:
                        if p2 * p4 * p8 == 0 and p2 * p6 * p8 == 0:
                            markers.append((x, y))
        for x, y in markers:
            img[y][x] = 0
            changed = True

    return img