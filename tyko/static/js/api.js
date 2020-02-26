import {requests} from "./request.js"

function addNote(apiRoute, noteTypeId, text) {
  if(apiRoute === undefined){
    throw new TypeError("apiRoute is a required field")
  }
  if(noteTypeId === undefined){
    throw new TypeError("noteTypeId is a required field")
  }
  if(text === undefined){
    throw new TypeError("text is a required field")
  }

  const newNoteRoute = apiRoute + "/notes";

  const data = {
    "text": text,
    "note_type_id": noteTypeId
  };
  return requests.post(newNoteRoute, data);
}

const getNotes = () => {
  const apiPath = `/api/notes`;
  return requests.get(apiPath);
};

function editNote(apiRoute, noteTypeId, text){
  if(apiRoute === undefined){
    throw("apiRoute is a required field")
  }
  if(noteTypeId === undefined){
    throw("noteTypeId is a required field")
  }
  if(text === undefined){
    throw("text is a required field")
  }

  const data = {
    "text": text,
    "note_type_id": noteTypeId
  };

  return requests.put(apiRoute, data);
}

function removeNote(apiRoute) {
  if(apiRoute === undefined){
    throw("apiRoute is a required field")
  }
  return requests.delete(apiRoute)
}

export const notes = {
  "getNotes": getNotes,
  "addNote": addNote,
  "editNote": editNote,
  "removeNote": removeNote
};


function addObject(apiRoute, data) {
  if(apiRoute === undefined){
    throw("apiRoute is a required field")
  }
  return requests.post(apiRoute, data);
}

export const objects = {
  "addObject": addObject
};