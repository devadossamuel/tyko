const sample_notes_data = `
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
export const requests = {
  'get': (apiPath) => {
    return new Promise(((resolve, reject) => {
      resolve(sample_notes_data);
    }));
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
