import {requests} from './request.js';
import * as metadataWidgets from './metadataWidgets.mjs';
import {parseUpdateRequestData} from './utils.mjs';

export const urls = {
  tapeTypesUrl: null,
  cassetteTypesUrl: null,
  cassetteTapeTapeThicknessURL: null,

};

export const data = {};

/**
 * Parse data and convert name to text and id to value
 * @param {Object} row
 * @return {{text: *, value: *}}
 */
function parseOptionsNameId(row) {
  return {text: row['name'], value: row['id']};
}

/**
 * Fetch data for the page
 * @return {Promise<{}>}
 */
export async function load() {
  const missingVariables = getMissingVariables();
  if (missingVariables.length > 0) {
    const missing = missingVariables.join(', ');
    throw new Error(`url is missing required data attributes: ${missing}`);
  }
  return Promise.all([
    requests.get(urls['tapeTypesUrl']).
        then((res) => {
          return {'type': 'tapeTypes', 'data': res};
        }),
    requests.get(urls['cassetteTypesUrl']).
        then((res) => {
          return {'type': 'formatTypes', 'data': res};
        }),
    requests.get(urls['cassetteTapeTapeThicknessURL']).
        then((res) => {
          return {'type': 'tapeThickness', 'data': res};
        }),
  ]).then(
      ((values) => {
        for (const v in values) {
          if (values.hasOwnProperty(v)) {
            data[values[v].type] = JSON.parse(values[v].data);
          }
        }
        return data;
      })).
      then((inData) => {
        inData.formatTypes = inData.formatTypes.map(parseOptionsNameId);
        inData.tapeTypes = inData.tapeTypes.map(parseOptionsNameId);
        inData.tapeThickness = inData.tapeThickness.map(parseOptionsUnits);
        return inData;
      });
}

/**
 * Tester for loading modules to make sure required data is included
 * @return {[]}
 */
function getMissingVariables() {
  const missing = [];
  for (const i in urls) {
    if (urls[i] === null) {
      missing.push(i);
    }
  }
  return missing;
}

/**
 * Parse options data and join the value and the unit together if unit is not
 * null
 * @param {Object[]} row
 * @return {Object[]}
 */
function parseOptionsUnits(row) {
  const text = row['unit'] != null ?
      `${row['value']} ${row['unit']}` :
      row['value'];
  return {text: text, value: row['id']};
}

/**
 * Redraw data to page
 */
export function refresh() {
  $('#rowTapeTape').loadEnumData(data['tapeTypes']);
  $('#cassetteAudioType').loadEnumData(data['formatTypes']);
  $('#cassetteTapeThickness').loadEnumData(data['tapeThickness']);
}

$(metadataWidgets).ready(() => {
  refresh();

  $('#formatDetails').on('changesRequested', (event, data, url) => {
    const parsedData = parseUpdateRequestData(data);
    requests.put(url, parsedData).then((res) => {
      location.reload();
    }).catch((res) => {
      alert(res.responseText);
    });
  });
});
