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
    "name": "casette tape"
  }
]`;
export const requests = {
  'get': (apiPath) => {
    return new Promise((resolve, reject) => {
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
