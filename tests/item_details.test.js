'use strict';

jest.mock('../tyko/static/js/request.js');
import * as module from '../tyko/static/js/item_details.mjs';

describe('module', () => {
  beforeEach(() => {
    document.body.innerHTML = ``;
  });

  test('check missing data', async () => {
    return await expect(module.load()).rejects.toThrow(Error);
  });

  test('returns the data', async () => {
        module.urls['tapeTypesUrl'] = '/api/formats/cassette_tape/cassette_tape_tape_types';
        module.urls['cassetteTypesUrl'] = '/api/formats/cassette_tape/cassette_tape_format_types';
        module.urls['cassetteTapeTapeThicknessURL'] = '/api/formats/cassette_tape/cassette_tape_tape_thickness';
        return await expect(module.load()).resolves.toEqual(
            {
              'formatTypes': [
                  {'value': 1, 'text': 'compact cassette'},
                  {'value': 2, 'text': 'DAT'},
                  {'value': 3, 'text': 'ADAT'},
                  {'value': 4, 'text': 'Other'},
              ],
              'tapeTypes': [
                {'value': 1, 'text': 'I'},
                {'value': 2, 'text': 'II'},
                {'value': 3, 'text': 'IV'},
              ],
              "tapeThickness": [
                {'value': 1, 'text': '0.5 mm' },
                {'value': 2, 'text': '1.0 mm' },
                {'value': 3, 'text': '1.5 mm' },
                {'value': 4, 'text': "unknown"},
              ],
            },
        );
      },
  );
});