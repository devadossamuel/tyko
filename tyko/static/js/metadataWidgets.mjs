$(document).ready(
    function() {
      applyStyles();
    },
);

/**
 * Apply all the styles to the elements with special classes
 */
export function applyStyles() {
  $.each($('.tyko-metadata-entity'), (i, row) => {
    metadataEntry(row);
  });
}

/**
 * Replace any existing content in a row with the rendered version
 * @param {jQuery} row
 */
function metadataEntry(row) {
  $(row).empty();
  const builder = new MetadataWidgetBuilder();
  builder.setMetadataDisplay($(row).data('name'));
  builder.setDisplayText($(row).data('displaydata'));
  builder.setEdit($(row).is('.tyko-metadata-entity-editable'));

  const newRowData = builder.build().join('');
  $(row).append(newRowData);
}

/**
 * Builder for generating a row of metadata in a table
 */
export class MetadataWidgetBuilder {
  #editable = true;
  #metadataDisplayText = '';
  #displayText = '';

  /**
   * How the header for the metadata should be displayed
   * @param {string} text
   */
  setMetadataDisplay(text) {
    this.#metadataDisplayText = text;
  }

  /**
   * How the content of the metadata should be displayed
   * @param {string} text
   */
  setDisplayText(text) {
    this.#displayText = text;
  }

  /**
   * Set if the field can be edited
   * @param {boolean} isEditble - a button should be added
   */
  setEdit(isEditble) {
    this.#editable = isEditble;
  }

  /**
   * Render the heading for the metadata
   * @param {string} text - Display the type of metadata
   * @return {string} - Rendered Html
    */
  static buildMetadataTitle(text) {
    return `<th style="width: 16.66%">${text}</th>`;
  }

  /**
   * Build the value of the metadata
   * @param {string} text - How the value metadata should render
   * @return {string} Rendered HTML string
   */
  static buildMetadataDisplay(text) {
    return `<td>${text}</td>`;
  }

  /**
   * Build the row
   * @return {string[]}
   */
  build() {
    return [
      MetadataWidgetBuilder.buildMetadataTitle(this.#metadataDisplayText),
      MetadataWidgetBuilder.buildMetadataDisplay(this.#displayText),
      MetadataWidgetBuilder.buildEditRow(this.#editable),
    ];
  }

  /**
   * Build the edit options column, if it can be edited, an edit button will be
   * drawn
   * @param {boolean} editable
   * @return {string} string html of the edit column
   */
  static buildEditRow(editable) {
    const items = [];
    items.push('<td style=\'text-align:right\'>');
    if (editable === true) {
      items.push(`<button class="btn btn-sm btn-secondary">Edit</button>`);
    }
    items.push('</td>');
    return items.join('');
  }
}
