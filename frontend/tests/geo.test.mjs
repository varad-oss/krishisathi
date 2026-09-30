// Field outline geometry: the area shown while drawing matches the server's formula and limits.
import assert from 'node:assert/strict';
import { test } from 'node:test';

const { areaHa, closeRing, fromPolygon, outlineProblem, selfIntersects, toPolygon } = await import('../src/lib/geo.ts');

const LAT = 18.52, LNG = 73.857;
function square(sideM) {
  const dlat = sideM / 2 / 111_195;
  const dlng = dlat / Math.cos((LAT * Math.PI) / 180);
  return [[LNG - dlng, LAT - dlat], [LNG + dlng, LAT - dlat], [LNG + dlng, LAT + dlat], [LNG - dlng, LAT + dlat]];
}

test('a 100 m square is one hectare, open or closed', () => {
  assert.ok(Math.abs(areaHa(square(100)) - 1) < 0.01);
  assert.ok(Math.abs(areaHa(closeRing(square(100))) - 1) < 0.01);
  assert.equal(areaHa(square(100).slice(0, 2)), 0);
});

test('bow tie is detected', () => {
  const d = 0.001;
  assert.equal(selfIntersects([[LNG, LAT], [LNG + d, LAT + d], [LNG + d, LAT], [LNG, LAT + d]]), true);
  assert.equal(selfIntersects(square(100)), false);
});

test('problems before saving', () => {
  assert.equal(outlineProblem(square(100).slice(0, 2)), 'too_few_points');
  assert.equal(outlineProblem(square(5)), 'too_small');
  assert.equal(outlineProblem(square(1500)), 'too_large');
  assert.equal(outlineProblem(square(100)), null);
});

test('GeoJSON round trip keeps an open ring for editing', () => {
  const g = toPolygon(square(100));
  assert.equal(g.type, 'Polygon');
  assert.deepEqual(g.coordinates[0][0], g.coordinates[0][4]);
  assert.deepEqual(fromPolygon(g), square(100));
  assert.deepEqual(fromPolygon(undefined), []);
});

test('the field preview keeps the outline inside its box, north up', async () => {
  const { outlinePath } = await import('../src/lib/geo.ts');
  assert.equal(outlinePath([]), '');
  const d = outlinePath(square(100), 64, 4);
  const nums = [...d.matchAll(/-?\d+(\.\d+)?/g)].map((m) => Number(m[0]));
  assert.ok(nums.every((n) => n >= 4 - 0.01 && n <= 60 + 0.01), d);
  assert.match(d, /^M4,60 L60,60 L60,4 L4,4 Z$/); // square: SW corner bottom-left, NE corner top-right
});
