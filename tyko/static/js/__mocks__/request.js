const sampleNotesData = `
{
  "notes": [
    {
      "note_id": 1, 
      "note_type": "Inspection", 
      "note_type_id": 1, 
      "text": "inspection note"
    }, 
    {
      "note_id": 2, 
      "note_type": "Project", 
      "note_type_id": 3, 
      "text": "One 16mm film"
    }
  ]
}`;

const sampleFormatData = `[
  {
    "format_types_id": 1,
    "name": "audio video"
  },
  {
    "format_types_id": 2,
    "name": "audio"
  },
  {
    "format_types_id": 3,
    "name": "video"
  },
  {
    "format_types_id": 4,
    "name": "open reel"
  },
  {
    "format_types_id": 5,
    "name": "grooved disc"
  },
  {
    "format_types_id": 6,
    "name": "film"
  },
  {
    "format_types_id": 7,
    "name": "cassette tape"
  }
]`;

const cassetteTapeTapeTypes = `[
  {
    "id": 1,
    "name": "I"
  },
  {
    "id": 2,
    "name": "II"
  },
  {
    "id": 3,
    "name": "IV"
  }
]
`;

const cassetteTapeTypes = `[
  {
    "id": 1, 
    "name": "compact cassette"
  }, 
  {
    "id": 2, 
    "name": "DAT"
  }, 
  {
    "id": 3, 
    "name": "ADAT"
  }, 
  {
    "id": 4, 
    "name": "Other"
  }
]`;

const cassetteTapeTapeThickness = `[
  {
    "id": 1,
    "unit": "mm",
    "value": "0.5"
  },
  {
    "id": 2,
    "unit": "mm",
    "value": "1.0"
  },
  {
    "id": 3,
    "unit": "mm",
    "value": "1.5"
  },
  {
    "id": 4,
    "unit": null,
    "value": "unknown"
  }
]`;

export const requests = {
  'get': (apiPath) => {
    return new Promise((resolve, reject) => {
      switch (apiPath) {
        case '/api/formats':
          resolve(sampleFormatData);
          break;
        case '/api/formats/cassette_tape/cassette_tape_tape_types':
          resolve(cassetteTapeTapeTypes);
          break;
        case '/api/formats/cassette_tape/cassette_tape_format_types':
          resolve(cassetteTapeTypes);
          break;
        case '/api/formats/cassette_tape/cassette_tape_tape_thickness':
          resolve(cassetteTapeTapeThickness);
          break;
        default:
          resolve(sampleNotesData);
      }
      if (apiPath === '/api/formats') {
        resolve(sampleFormatData);
      } else {
        resolve(sampleNotesData);
      }
    });
  },
  'post': (apiPath, data) => {
    return new Promise(((resolve, reject) => {
      resolve();
    }));
  },
  'put': (apiPath, data) => {
    return new Promise(((resolve, reject) => {
      resolve();
    }));
  },
  'delete': (apiPath) => {
    return new Promise(((resolve, reject) => {
      resolve();
    }));
  },

};
