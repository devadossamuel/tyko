class Notes {
  static noteData(message, id) {
    return {
      'id': id,
      'text': message,
    };
  }

  static fileData(id) {
    return {
      'id': id,
    };
  }

  static requestData(type, url) {
    return {
      'type': type,
      'url': url,
    };
  }
}
