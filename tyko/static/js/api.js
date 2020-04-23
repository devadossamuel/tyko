import {requests} from './request.js';

function addNote(apiRoute, noteTypeId, text) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  if (noteTypeId === undefined) {
    throw new TypeError('noteTypeId is a required field');
  }
  if (text === undefined) {
    throw new TypeError('text is a required field');
  }

  const newNoteRoute = apiRoute + '/notes';

  const data = {
    'text': text,
    'note_type_id': noteTypeId,
  };
  return requests.post(newNoteRoute, data);
}

const getNotes = () => {
  const apiPath = `/api/notes`;
  return requests.get(apiPath);
};

function editNote(apiRoute, noteTypeId, text) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  if (noteTypeId === undefined) {
    throw new TypeError('noteTypeId is a required field');
  }
  if (text === undefined) {
    throw new TypeError('text is a required field');
  }

  const data = {
    'text': text,
    'note_type_id': noteTypeId,
  };

  return requests.put(apiRoute, data);
}

function removeNote(apiRoute) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  return requests.delete(apiRoute);
}

export const notes = {
  'getNotes': getNotes,
  'addNote': addNote,
  'editNote': editNote,
  'removeNote': removeNote,
};

function addObject(apiRoute, data) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  return requests.post(apiRoute, data);
}

function removeObject(apiRoute) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  return requests.delete(apiRoute);
}

export const objects = {
  'addObject': addObject,
  'removeObject': removeObject,
};

/**
 * Add an item to a given object
 * @param {string} apiRoute - url to the project_object_add_item route
 * @param {Object} data - data to be sent to the server
 * @return {Promise | Promise<Object>} result of request made to server
 */
function addItem(apiRoute, data) {
  if (apiRoute === undefined) {
    throw new TypeError('apiRoute is a required field');
  }
  return requests.post(apiRoute, data);
}
/**
 * Update a note for a given file
 * @param {string} apiRoute - url to the file_notes route
 * @param {Object} data - data to be sent to the server
 * @return {Promise | Promise<Object>} result of request made to server
 */
function editFileNote(apiRoute, data) {
  return requests.put(apiRoute, data);
}

/**
 * Add a note to a given file
 * @param {string} apiRoute - url to the file_notes route
 * @param {Object} data - data to be sent to the server
 * @return {Promise | Promise<Object>} result of request made to server
 */
function addFileNote(apiRoute, data) {
  return requests.post(apiRoute, data);
}

/**
 * Add a file to a given item
 * @param {string} apiRoute - url to the item_files route
 * @param {Object} data - data to be sent to the server
 * @return {Promise | Promise<Object>} result of request made to server
 */
function addFile(apiRoute, data) {
  return requests.post(apiRoute, data);
}

export const items = {
  'addItem': addItem,
  'addFile': addFile,
};

export const collections = {
  'new': requests.post,
};

export const files = {
  'addFile': addFile,
  'removeFile': (apiRoute) => {
    return requests.delete(apiRoute);
  },
  'removeNote': (apiRoute) => {
    return requests.delete(apiRoute);
  },
  'addNote': addFileNote,
  'editNote': editFileNote,
};
export const routes = {
  'all_routes': (baseURL) => {
    return requests.get(baseURL).then(function(result) {
      const d = JSON.parse(result);
      const dataRoutes = {};
      for (let i = 0; i < d.length; i++) {
        dataRoutes[d[i].endpoint.toString()] = d[i];
      }
      return dataRoutes;
    });
  },
};