import {parseUpdateRequestData} from '../tyko/static/js/utils.mjs';

describe('Testing parseUpdateRequestData on flat data', () => {
  const data = [
    {key: 'format', value: 'video'},
  ];

  test('parseUpdateRequestData returns an object', () => {
    const result = parseUpdateRequestData(data);
    expect(result).toBeInstanceOf(Object);
  });

  test('parseUpdateRequestData includes the data', () => {
    const result = parseUpdateRequestData(data);
    expect(result).toMatchObject({
      'format': 'video',
    });
  });
});

describe('Testing parseUpdateRequestData on data with a dot', () => {
  const data = [
    {key: 'format_id', value: '7'},
    {key: 'format_details.inspection_date', value: '05-05-2020'},
    {key: 'format_details.recorded_date', value: '02-01-1995'},
  ];

  test('parseUpdateRequestData returns an object', () => {
    const result = parseUpdateRequestData(data);
    expect(result).toBeInstanceOf(Object);
  });

  test('parseUpdateRequestData includes the data', () => {
    const result = parseUpdateRequestData(data);
    expect(result).toMatchObject({
      'format_id': '7',
      'format_details': {
        'inspection_date': '05-05-2020',
        'recorded_date': '02-01-1995'
      },
    });
  });
});