import math

def douglas_peucker(points, epsilon):
    """
    Rút gọn danh sách điểm bằng thuật toán Douglas-Peucker.
    points: list of (x,y)
    epsilon: độ lệch tối đa
    """
    if len(points) <= 2:
        return points

    # Tìm điểm xa nhất
    dmax = 0
    index = 0
    for i in range(1, len(points) - 1):
        d = perpendicular_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        # Đệ quy hai bên
        left = douglas_peucker(points[:index+1], epsilon)
        right = douglas_peucker(points[index:], epsilon)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]


def perpendicular_distance(point, start, end):
    """Tính khoảng cách từ point đến đoạn thẳng start-end."""
    x0, y0 = point
    x1, y1 = start
    x2, y2 = end
    if x1 == x2 and y1 == y2:
        return math.hypot(x0 - x1, y0 - y1)
    # Công thức khoảng cách từ điểm đến đường thẳng
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.hypot(x2 - x1, y2 - y1)
    return num / den


def write_svg(segments, output_path, stroke_width=45, orig_width=None, orig_height=None,
              target_width=1024, target_height=1024, smoothing_epsilon=2.0):
    """
    Xuất SVG với viewBox target_width x target_height.
    Áp dụng Douglas-Peucker để làm mượt đường.
    """
    paths = []
    for seg in segments:
        if len(seg) < 2:
            continue

        # Scale tọa độ trước khi làm mịn
        if orig_width and orig_height:
            scale_x = target_width / orig_width
            scale_y = target_height / orig_height
            scaled_pts = [(p[0] * scale_x, p[1] * scale_y) for p in seg]
        else:
            scaled_pts = seg

        # Làm mịn bằng Douglas-Peucker
        if smoothing_epsilon > 0 and len(scaled_pts) > 2:
            simplified = douglas_peucker(scaled_pts, smoothing_epsilon)
        else:
            simplified = scaled_pts

        # Loại bỏ trùng lặp
        pts = []
        for p in simplified:
            if not pts or p != pts[-1]:
                pts.append(p)
        if len(pts) < 2:
            continue

        d = f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"
        for p in pts[1:]:
            d += f" L {p[0]:.2f} {p[1]:.2f}"
        if pts[0] == pts[-1]:
            d += " Z"
        paths.append(f'<path d="{d}"/>')

    paths_str = "\n    ".join(paths)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {target_width} {target_height}" width="{target_width}" height="{target_height}">
  <g fill="none" stroke="black" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">
    {paths_str}
  </g>
</svg>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)