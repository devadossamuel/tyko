/** Helper for formatting data correctly **/
class Notes {
  /**
   * Format notes Data correctly
   *
   * @param {string} message - Contents of note
   * @param {number} id - id of note
   * @return {{id: *, text: *}}
   */
  static noteData(message, id) {
    return {
      'id': id,
      'text': message,
    };
  }

  /**
   * Format file data correctly
   *
   * @param {number} id - id of file
   * @return {{id: *}}
   */
  static fileData(id) {
    return {
      'id': id,
    };
  }

  /**
   * Format request data correctly
   *
   * @param {string} type - type of request being made
   * @param {string} url - Url route to api making the request
   * @return {{type: *, url: *}}
   */
  static requestData(type, url) {
    return {
      'type': type,
      'url': url,
    };
  }
}
