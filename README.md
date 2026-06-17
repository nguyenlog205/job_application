# Centerline Extraction from PNG Icons

## 1. Overview

> This program converts filled raster PNG icons (1024×1024, single solid-black shape on white/transparent background) into clean SVG paths representing the **medial axis** (centerline/skeleton) of the original shape. Instead of tracing the outline, it extracts the "pen stroke" skeleton a person would naturally draw.

**Example:** A thick `H` shape → three thin paths: two vertical strokes and one horizontal stroke, connected at intersections.

---

## 2. Approach

The pipeline follows these steps:

### Step 01: PNG Parsing (no external libraries)
- Custom PNG reader using only Python's built-in `struct` and `zlib` modules.
- Fully supports **filter methods 0–4** (Sub, Up, Average, Paeth) and **color types** (grayscale, RGB, RGBA).
- For RGBA images: extracts **RGB channels** (not alpha) to correctly handle solid shapes on transparent backgrounds.

### Step 02. Binarization
- Converts grayscale to binary mask: pixel value < threshold (configurable, default 128) → foreground (shape).
- Auto-inverts if no foreground pixels are detected.

### Step 03. Skeletonization (thinning)
- **Zhang-Suen iterative thinning algorithm** reduces the binary shape to a **1-pixel-thick skeleton** while preserving topology.
- Iteratively removes boundary pixels that satisfy connectivity and end-point conditions until no more pixels can be removed.

### Step 04. Graph Construction
- Builds an undirected graph where each skeleton pixel is a node connected to its 8-neighbors.
- Classifies nodes:
  - **Endpoints** (degree 1)
  - **Branch points** (degree > 2)
  - **Internal points** (degree 2)

### Step 05. Segment Extraction
- Traverses from endpoints and branch points to extract continuous paths.
- Handles closed loops (no endpoints) separately.

### Step 06. Segment Merging
- At branch points, merges segments that are **collinear** (opposite directions within a configurable angle threshold, default 30°).
- This transforms a cross/intersection into continuous straight lines (e.g., the vertical strokes of an `H` pass through the horizontal bar without breaking).

### Step 07. SVG Export
- Scales all coordinates to fit the target viewBox (default 1024×1024).
- Exports as `<path>` elements with:
  - `fill="none"`
  - Configurable `stroke-width` (default 45)
  - `stroke-linecap="round"` and `stroke-linejoin="round"`

---

## 3. How to Run

### 3.1. Prerequisites
- Python 3.6+ (no third-party libraries required)

### 3.2. Setup
```bash
cd <project-root>
git clone https://github.com/nguyenlog205/job_application
```

### 3.3. Configuration
Edit `config.json` to adjust parameters:
```json
{
  "input_dir": "data",
  "output_dir": "results",
  "stroke_width": 45,
  "threshold": 128,
  "merge_angle_threshold": 30,
  "target_width": 1024,
  "target_height": 1024
}
```

### 3.4. Run
```bash
python -m src.main
```
Or process a specific file/folder:
```bash
python -m src.main data/custom.png
python -m src.main data/
```

### 3.5. Output
- SVG files saved in `results/` (or custom output directory).
- Each `<name>.svg` has `viewBox="0 0 1024 1024"`.


## 4. Output Characteristics

The generated SVG contains:
- **Centerline paths** following the medial axis of the original shape.
- **Stroke width** matching the config (45 by default, matching the reference).
- **Rounded caps and joins** for a natural pen-stroke appearance.
- All paths scaled to fit the 1024×1024 viewBox.

## 5. Limitations & Future Improvements

### Limitations
- **No pruning**: Small spurs from the skeletonization process remain.
- **No curve fitting**: Paths are straight line segments; curves are not smoothed with Bezier or spline approximations.
- **No polygon simplification**: Redundant points along straight lines are not removed.
- **Performance**: Python loops over every pixel for thinning; 1024×1024 images take a few seconds.

### 5.1. What I'd Improve with More Time

1. **Pruning**  
   - Remove branches shorter than a configurable length threshold (e.g., < 10 pixels).

2. **Curve Smoothing**  
   - Apply Douglas-Peucker or Ramer-Douglas-Peucker to reduce points on straight segments.
   - Convert remaining sequences to cubic Bezier curves for smoother arcs.

3. **Post-processing**  
   - Detect and merge near-collinear segments across the entire path (not just at branch points).

4. **Performance Optimization**  
   - Use NumPy (if allowed) for vectorized operations.
   - Implement Guo-Hall thinning (faster than Zhang-Suen).

5. **Better Scaling**  
   - Maintain aspect ratio when scaling to 1024×1024 instead of stretching.

6. **Palette PNG Support**  
   - Extend the PNG reader to handle indexed color (color type 3).

<!--

## Algorithmic Understanding

### Why Zhang-Suen Thinning?
- **Simple & deterministic**: Easy to implement correctly.
- **Preserves connectivity**: The two-pass conditional removal ensures the skeleton remains a connected 1-pixel-thick representation.
- **Works for any binary shape**: No assumptions about stroke width or shape complexity.

### How the Graph Merging Works
1. At each branch point, compute the **direction vector** of each incident segment (2–3 pixels away from the branch).
2. Sort directions by angle.
3. Pair segments whose directions are nearly opposite (within 30° of 180°).
4. Merge each pair into a single continuous segment passing through the branch point.

This effectively "connects the dots" through intersections, producing the natural pen-stroke appearance.

### Why Manual Filter Handling?
- The PNG specification includes filtering to improve compression.
- Many PNG exporters use filter method 1 (Sub) by default.
- By implementing all filters (0–4), we ensure compatibility with any PNG without external libraries.


## Final Notes

This implementation demonstrates:
- **Deep understanding of image processing fundamentals** (filtering, binarization, thinning, graph traversal).
- **No external dependencies** – fully self-contained Python.
- **Correct topology preservation** – the centerline follows the shape's medial axis.
- **Configurable parameters** for fine-tuning stroke width, threshold, and merging.

With additional time for pruning and curve smoothing, this would match the reference quality closely. The core algorithm is solid and production-ready for straight-line or simple-curve shapes.

-->
