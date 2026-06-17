import math

class SkeletonGraph:
    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.graph = self._build_graph()
        self.segments = None

    def _build_graph(self):
        h, w = len(self.skeleton), len(self.skeleton[0])
        graph = {}
        for y in range(h):
            for x in range(w):
                if self.skeleton[y][x] == 1:
                    neighbors = []
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h and self.skeleton[ny][nx]:
                                neighbors.append((nx, ny))
                    graph[(x, y)] = neighbors
        return graph

    def find_segments(self):
        graph = self.graph
        if not graph:
            self.segments = []
            return

        endpoints = [p for p, nb in graph.items() if len(nb) == 1]
        branches = [p for p, nb in graph.items() if len(nb) > 2]
        special = set(endpoints + branches)

        visited_edges = set()
        segments = []

        if not special:
            start = next(iter(graph))
            path = [start]
            prev = None
            curr = start
            while True:
                nxt = None
                for nb in graph[curr]:
                    if nb != prev:
                        nxt = nb
                        break
                if nxt is None:
                    break
                if nxt == start:
                    path.append(start)
                    break
                path.append(nxt)
                prev, curr = curr, nxt
                if len(path) > len(graph):
                    break
            if path[0] == path[-1]:
                segments.append(path)
            else:
                segments.append(path + [path[0]])
            self.segments = segments
            return

        for p in list(special):
            for nb in graph[p]:
                edge = (p, nb)
                if edge in visited_edges:
                    continue
                path = [p, nb]
                visited_edges.add((p, nb))
                visited_edges.add((nb, p))
                prev, curr = p, nb
                while True:
                    neigh = graph[curr]
                    candidates = [n for n in neigh if n != prev]
                    if not candidates:
                        break
                    if len(candidates) > 1:
                        break
                    nxt = candidates[0]
                    path.append(nxt)
                    visited_edges.add((curr, nxt))
                    visited_edges.add((nxt, curr))
                    prev, curr = curr, nxt
                    if curr in special:
                        break
                segments.append(path)

        self.segments = segments

    def prune_branches(self, min_length=5):
        """
        Xóa các nhánh (branch) có độ dài (số pixel) < min_length.
        """
        if self.segments is None:
            self.find_segments()

        # Xác định các đầu mút là endpoint hoặc branch
        endpoints = [p for p, nb in self.graph.items() if len(nb) == 1]
        branches = [p for p, nb in self.graph.items() if len(nb) > 2]
        special = set(endpoints + branches)

        to_remove = set()
        for idx, seg in enumerate(self.segments):
            # Chỉ xử lý segment có đầu mút là endpoint (không phải branch)
            first, last = seg[0], seg[-1]
            if first in branches or last in branches:
                continue
            if len(seg) < min_length:
                to_remove.add(idx)

        self.segments = [seg for idx, seg in enumerate(self.segments) if idx not in to_remove]

    def merge_segments(self, angle_threshold_deg=30):
        if self.segments is None:
            self.find_segments()
        segments = self.segments
        if not segments:
            return

        angle_threshold = math.radians(angle_threshold_deg)

        while True:
            endpoint_map = {}
            for idx, seg in enumerate(segments):
                if len(seg) < 2:
                    continue
                first, last = seg[0], seg[-1]
                if first == last:
                    continue
                endpoint_map.setdefault(first, []).append((idx, True))
                endpoint_map.setdefault(last, []).append((idx, False))

            branches = [p for p, lst in endpoint_map.items() if len(lst) > 2]
            if not branches:
                break

            p = branches[0]
            entries = endpoint_map[p]

            dirs = []
            for seg_idx, is_start in entries:
                seg = segments[seg_idx]
                if is_start:
                    p2 = seg[1]
                else:
                    p2 = seg[-2]
                vec = (p2[0] - p[0], p2[1] - p[1])
                angle = math.atan2(vec[1], vec[0])
                dirs.append((angle, seg_idx, is_start))

            dirs.sort(key=lambda x: x[0])
            used = [False] * len(dirs)
            pairs = []

            for i in range(len(dirs)):
                if used[i]:
                    continue
                for j in range(i + 1, len(dirs)):
                    if used[j]:
                        continue
                    diff = dirs[j][0] - dirs[i][0]
                    diff = (diff + math.pi) % (2 * math.pi) - math.pi
                    if abs(abs(diff) - math.pi) < angle_threshold:
                        pairs.append((i, j))
                        used[i] = used[j] = True
                        break

            if not pairs:
                break

            to_remove = set()
            new_segments = []

            for i, j in pairs:
                seg_idx_i = dirs[i][1]
                seg_idx_j = dirs[j][1]
                is_start_i = dirs[i][2]
                is_start_j = dirs[j][2]

                seg_i = segments[seg_idx_i]
                seg_j = segments[seg_idx_j]

                if is_start_i:
                    part_i = list(reversed(seg_i))
                else:
                    part_i = seg_i[:]

                if is_start_j:
                    part_j = seg_j[1:]
                else:
                    part_j = list(reversed(seg_j[:-1]))

                merged = part_i + part_j
                new_segments.append(merged)
                to_remove.add(seg_idx_i)
                to_remove.add(seg_idx_j)

            segments = [seg for idx, seg in enumerate(segments) if idx not in to_remove]
            segments.extend(new_segments)

        self.segments = segments

    def get_segments(self, angle_threshold=30, min_branch_length=5):
        if self.segments is None:
            self.find_segments()
            self.prune_branches(min_branch_length)
            self.merge_segments(angle_threshold)
        return self.segments