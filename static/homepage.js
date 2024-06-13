  document.addEventListener('DOMContentLoaded', function() {
    var imageFieldsContainer = document.getElementById('image-fields');
    var addImageFieldButton = document.getElementById('add-image-field');
    var imageFieldIndex = 2; // Start index for additional image fields

    addImageFieldButton.addEventListener('click', function() {
      var imageField = document.createElement('div');
      imageField.className = 'image-field mb-3';
      imageField.innerHTML = `
        <label for="image-file-${imageFieldIndex}">Image ${imageFieldIndex}:</label>
        <input type="file" id="image-file-${imageFieldIndex}" name="image_files[]" accept="image/*" required>
        <input type="text" class="form-control" name="image_titles[]" placeholder="Image Title" required>
        <input type="text" class="form-control" name="image_descriptions[]" placeholder="Image Description" required>
      `;
      imageFieldsContainer.appendChild(imageField);
      imageFieldIndex++;
    });
  });
