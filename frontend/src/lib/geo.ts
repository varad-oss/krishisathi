// Field outline helpers. The same area formula and limits as backend/services/plots.py, so the area the farmer
// sees while drawing is the area the server stores. Positions are [lng, lat] (GeoJSON order).

export type Position = [number, number];

const EARTH_RADIUS_M = 6_371_008.8;
export const MIN_AREA_HA = 0.01;
export const MAX_AREA_HA = 200;
export const MAX_VERTICES = 200;

function project(ring: Position[]): [number, number][] {
  const lat0 = ((ring.reduce((s, p) => s + p[1], 0) / ring.length) * Math.PI) / 180;
  return ring.map(([lng, lat]) => [((lng * Math.PI) / 180) * EARTH_RADIUS_M * Math.cos(lat0), ((lat * Math.PI) / 180) * EARTH_RADIUS_M]);
}

export const closeRing = (points: Position[]): Position[] =>
  points.length && (points[0][0] !== points[points.length - 1][0] || points[0][1] !== points[points.length - 1][1]) ? [...points, points[0]] : points;

/** Area in hectares of the polygon through `points` (open or closed). */
export function areaHa(points: Position[]): number {
  if (points.length < 3) return 0;
  const xy = project(closeRing(points));
  let twice = 0;
  for (let i = 0; i < xy.length - 1; i++) twice += xy[i][0] * xy[i + 1][1] - xy[i + 1][0] * xy[i][1];
  return Math.abs(twice) / 2 / 10_000;
}

const cross = (o: number[], a: number[], b: number[]) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);

/** True when two non-adjacent edges of the outline cross (a "bow tie"). */
export function selfIntersects(points: Position[]): boolean {
  const xy = project(closeRing(points));
  const n = xy.length - 1;
  for (let i = 0; i < n; i++) {
    for (let j = i + 2; j < n; j++) {
      if (i === 0 && j === n - 1) continue;
      const [p1, p2, p3, p4] = [xy[i], xy[i + 1], xy[j], xy[j + 1]];
      const d1 = cross(p3, p4, p1), d2 = cross(p3, p4, p2), d3 = cross(p1, p2, p3), d4 = cross(p1, p2, p4);
      if (d1 * d2 < 0 && d3 * d4 < 0) return true;
    }
  }
  return false;
}

export type OutlineProblem = 'too_few_points' | 'crosses_itself' | 'too_small' | 'too_large' | 'too_many_points' | null;

/** Why the outline cannot be saved yet, or null when it can. The server validates again. */
export function outlineProblem(points: Position[]): OutlineProblem {
  if (points.length < 3) return 'too_few_points';
  if (points.length > MAX_VERTICES) return 'too_many_points';
  if (selfIntersects(points)) return 'crosses_itself';
  const area = areaHa(points);
  if (area < MIN_AREA_HA) return 'too_small';
  if (area > MAX_AREA_HA) return 'too_large';
  return null;
}

export const toPolygon = (points: Position[]) => ({ type: 'Polygon' as const, coordinates: [closeRing(points)] });

/** Open ring of a stored polygon (for editing). */
export const fromPolygon = (g: { coordinates: Position[][] } | undefined): Position[] => (g ? g.coordinates[0].slice(0, -1) : []);

/**
 * SVG path of the outline scaled into a `size`×`size` box with `pad` margin, north up and true to shape (east–west
 * distances are shrunk by cos(latitude) like the area formula). Used for a tile-free preview of the saved field.
 */
export function outlinePath(points: Position[], size = 64, pad = 4): string {
  if (points.length < 3) return '';
  const xy = project(points);
  const xs = xy.map((p) => p[0]);
  const ys = xy.map((p) => p[1]);
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const span = Math.max(maxX - minX, maxY - minY) || 1;
  const k = (size - 2 * pad) / span;
  const ox = pad + (size - 2 * pad - (maxX - minX) * k) / 2;
  const oy = pad + (size - 2 * pad - (maxY - minY) * k) / 2;
  const r = (v: number) => Math.round(v * 10) / 10;
  return `${xy.map(([x, y], i) => `${i ? 'L' : 'M'}${r(ox + (x - minX) * k)},${r(oy + (maxY - y) * k)}`).join(' ')} Z`;
}
