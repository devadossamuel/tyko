/**
 *
 * @param {string} key
 * @param {Object<string, string>} dest
 * @param {Object<string, string>} source
 */
function updateEntry(key, dest, source) {
  const parts = key.split('.');
  const newKey = parts.pop();

  while (parts.length) {
    const part = parts.shift();
    dest = dest[part] = dest[part] || {};
  }
  dest[newKey] = source[key];
}

/**
 * Covert an array of objects key value where the key uses a dot delimiter
 * to indicate hierarchy in o nest object
 *
 * @param {Array.Object<string, string>} data
 * @return {Object} - Converted to a nested object
 */
export function parseUpdateRequestData(data) {
  const mergedObject = {};

  data.forEach((row) => {
    mergedObject[row['key']] = row['value'];
  });

  const newObject = {};
  for (const key in mergedObject) {
    if (! mergedObject.hasOwnProperty(key)) {
      continue;
    }
    updateEntry(key, newObject, mergedObject);
  }
  return newObject;
}
