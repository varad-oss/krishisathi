export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
export const MAX_SOURCE_BYTES = 15 * 1024 * 1024;
const MAX_EDGE_PX = 1600;
const JPEG_QUALITY = 0.85;

export type ImageProblem = 'invalidType' | 'tooLarge' | 'unreadable';

export function checkImageFile(file: File): ImageProblem | null {
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) return 'invalidType';
  if (file.size > MAX_SOURCE_BYTES) return 'tooLarge';
  return null;
}

/**
 * Downscales a photo to at most 1600 px on the long edge and re-encodes as JPEG.
 * Phone photos (3–8 MB) typically shrink to 200–500 KB, which matters on slow networks.
 * Throws if the browser cannot decode the file.
 */
export async function prepareImage(file: File): Promise<Blob> {
  const bitmap = await createImageBitmap(file).catch(() => {
    throw new Error('unreadable');
  });
  const scale = Math.min(1, MAX_EDGE_PX / Math.max(bitmap.width, bitmap.height));
  if (scale === 1 && file.type === 'image/jpeg' && file.size < 1.5 * 1024 * 1024) {
    bitmap.close();
    return file;
  }
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('unreadable');
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY));
  if (!blob) throw new Error('unreadable');
  return blob;
}

export async function blobToBase64(blob: Blob): Promise<string> {
  const buf = new Uint8Array(await blob.arrayBuffer());
  let binary = '';
  for (let i = 0; i < buf.length; i += 0x8000) binary += String.fromCharCode(...buf.subarray(i, i + 0x8000));
  return btoa(binary);
}
