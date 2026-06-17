#!/usr/bin/env python3
import sys
import os

from .tools import read_png, zhang_suen_thin, SkeletonGraph, write_svg
from .tools.utils import load_config, ensure_dir


def process_file(input_path, output_dir, stroke_width, threshold, merge_angle,
                 target_width=1024, target_height=1024, min_branch_length=5,
                 smoothing_epsilon=2.0):
    ensure_dir(output_dir)
    base = os.path.basename(input_path)
    svg_out = os.path.join(output_dir, base.replace('.png', '.svg'))

    print(f"Processing: {input_path}")

    # 1. Đọc ảnh → grayscale
    w, h, gray = read_png(input_path)
    print(f"  Original size: {w}x{h}")

    # 2. Nhị phân hóa
    binary = [[1 if p < threshold else 0 for p in row] for row in gray]
    total_black = sum(sum(row) for row in binary)
    print(f"  Black pixels: {total_black} ({(total_black/(w*h)*100):.2f}%)")

    if total_black == 0:
        print("  WARNING: No black pixels. Trying inverted threshold...")
        binary = [[1-p for p in row] for row in binary]
        total_black = sum(sum(row) for row in binary)
        if total_black == 0:
            print("  ERROR: Still no black pixels. Check image.")
            return

    # 3. Thinning
    skeleton = zhang_suen_thin(binary)
    skel_count = sum(sum(row) for row in skeleton)
    print(f"  Skeleton pixels: {skel_count} ({(skel_count/(w*h)*100):.2f}%)")

    # 4. Graph và segments (có pruning + merge)
    graph = SkeletonGraph(skeleton)
    segments = graph.get_segments(angle_threshold=merge_angle,
                                   min_branch_length=min_branch_length)
    print(f"  Number of segments: {len(segments)}")

    # 5. Xuất SVG với smoothing
    write_svg(segments, svg_out, stroke_width,
              orig_width=w, orig_height=h,
              target_width=target_width, target_height=target_height,
              smoothing_epsilon=smoothing_epsilon)
    print(f"  SVG saved: {svg_out} (viewBox {target_width}x{target_height})")


def main():
    config = load_config()
    input_dir = config.get('input_dir', 'data')
    output_dir = config.get('output_dir', 'results')
    stroke_width = config.get('stroke_width', 45)
    threshold = config.get('threshold', 128)
    merge_angle = config.get('merge_angle_threshold', 30)
    target_width = config.get('target_width', 1024)
    target_height = config.get('target_height', 1024)
    min_branch_length = config.get('min_branch_length', 5)
    smoothing_epsilon = config.get('smoothing_epsilon', 2.0)

    if len(sys.argv) >= 2:
        path = sys.argv[1]
        if os.path.isdir(path):
            input_dir = path
        else:
            if not os.path.exists(path):
                print(f"File not found: {path}")
                sys.exit(1)
            process_file(path, output_dir, stroke_width, threshold, merge_angle,
                         target_width, target_height, min_branch_length, smoothing_epsilon)
            return

    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        sys.exit(1)

    for f in os.listdir(input_dir):
        if f.lower().endswith('.png'):
            full_path = os.path.join(input_dir, f)
            process_file(full_path, output_dir, stroke_width, threshold, merge_angle,
                         target_width, target_height, min_branch_length, smoothing_epsilon)


if __name__ == '__main__':
    main()