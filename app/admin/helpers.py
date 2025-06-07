import os
import json
import uuid
from werkzeug.utils import secure_filename
import logging

CONTENT_FILE = os.path.join('app', 'admin', 'cmsContent.json')
IMAGE_UPLOAD_FOLDER = os.path.join('app', 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg', 'avif'}

def load_content():
    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_content(data):
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_nested_value(d, path):
    """Get a value from a nested dictionary using dot notation."""
    if not path:
        return d
        
    parts = path.split('.')
    current = d
    
    for i, part in enumerate(parts):
        is_last = i == len(parts) - 1
        
        if '[' in part:
            # Handle array access
            base, index = part.split('[')
            index = int(index.rstrip(']'))
            
            # If we're at a dictionary, ensure the base key exists
            if isinstance(current, dict):
                if base not in current:
                    current[base] = []
                current = current[base]
            
            # If we're at a list, ensure it's long enough
            if isinstance(current, list):
                while len(current) <= index:
                    current.append({} if not is_last else None)
                current = current[index]
        else:
            # Handle dictionary access
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {} if not is_last else None
                current = current[part]
            else:
                # If we're at a list or other type, we can't proceed
                return None
    
    return current

def set_nested_value(d, path, value):
    """Set a value in a nested dictionary using dot notation."""
    if not path:
        return
    
    parts = path.split('.')
    current = d
    
    # Navigate to the parent of the target
    for i, part in enumerate(parts[:-1]):
        if '[' in part:
            # Handle array access
            base, index = part.split('[')
            index = int(index.rstrip(']'))
            
            # If we're at a dictionary, ensure the base key exists
            if isinstance(current, dict):
                if base not in current:
                    current[base] = []
                current = current[base]
            
            # If we're at a list, ensure it's long enough
            if isinstance(current, list):
                while len(current) <= index:
                    current.append({})
                current = current[index]
        else:
            # Handle dictionary access
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
            else:
                # If we're at a list or other type, we can't proceed
                return
    
    # Handle the last part
    last_part = parts[-1]
    if '[' in last_part:
        # Handle array assignment
        base, index = last_part.split('[')
        index = int(index.rstrip(']'))
        
        # If we're at a dictionary, ensure the base key exists
        if isinstance(current, dict):
            if base not in current:
                current[base] = []
            current = current[base]
        
        # If we're at a list, ensure it's long enough
        if isinstance(current, list):
            while len(current) <= index:
                current.append(None)
            current[index] = value
    else:
        # Handle dictionary assignment
        if isinstance(current, dict):
            current[last_part] = value

def get_nested_dict(d, path_parts):
    """Helper function to get or create nested dictionary structure."""
    current = d
    for part in path_parts:
        if part not in current:
            current[part] = {}
        current = current[part]
    return current

def update_content_with_form_data(request, current_content):
    """Update content with form data, maintaining proper nested structure."""
    logger = logging.getLogger(__name__)

    # Get the section (e.g., 'home') from the first form field
    first_key = next(iter(request.form.keys()), None)
    if not first_key or '.' not in first_key:
        return current_content
    
    section = first_key.split('.')[0]
    if section not in current_content:
        current_content[section] = {}

    # Log all form data
    logger.debug("Form data received:")
    for key in request.form:
        logger.debug(f"{key}: {request.form[key]}")

    # First, collect all array paths and their indices, and track deleted items
    array_paths = {}
    deleted_indices = set()
    
    # Process form data to find deleted items and array updates
    for key in request.form:
        if key.startswith('__deleted__'):
            # This is a deleted item marker
            path = key[11:]  # Remove '__deleted__' prefix
            logger.debug(f"Processing deletion marker: {path}")
            if '[' in path:
                # Extract the base path and index
                base_path = path[:path.find('[')]
                index = int(path[path.find('[')+1:path.find(']')])
                logger.debug(f"Marking for deletion: {base_path}[{index}]")
                if base_path not in array_paths:
                    array_paths[base_path] = {}
                deleted_indices.add((base_path, index))
            continue
            
        if '[' in key:
            # Extract the base path (everything before the array index)
            base_path = key[:key.find('[')]
            if base_path not in array_paths:
                array_paths[base_path] = {}
            
            # Extract the index and field name
            # Example: "home.community.quotes[0].name" -> (0, "name")
            index_part = key[key.find('[')+1:key.find(']')]
            field_name = key[key.find(']')+2:] if ']' in key else None
            index = int(index_part)
            
            if index not in array_paths[base_path]:
                array_paths[base_path][index] = {}
            if field_name:
                array_paths[base_path][index][field_name] = request.form[key].strip()

    logger.debug(f"Deleted indices: {deleted_indices}")
    logger.debug(f"Array paths: {array_paths}")

    # Process each array path
    for base_path, indices in array_paths.items():
        logger.debug(f"Processing array path: {base_path}")
        # Get the parent dictionary and array name
        parts = base_path.split('.')
        parent_path = '.'.join(parts[:-1])
        array_name = parts[-1]
        
        # Get the parent dictionary
        parent = get_nested_value(current_content, parent_path)
        if not isinstance(parent, dict):
            logger.debug(f"Parent is not a dictionary: {parent_path}")
            continue
            
        # Get or create the array
        if array_name not in parent:
            parent[array_name] = []
        current_array = parent[array_name]
        
        if not isinstance(current_array, list):
            current_array = []
            parent[array_name] = current_array
        
        logger.debug(f"Current array before update: {current_array}")
        logger.debug(f"Indices to process: {indices}")
        logger.debug(f"Indices to delete: {[i for b, i in deleted_indices if b == base_path]}")
        
        # Create new array preserving existing items and updating with form data
        new_array = []
        max_index = max(indices.keys()) if indices else -1
        
        # First, copy existing items up to the max index, excluding deleted ones
        for i in range(max_index + 1):
            # Skip if this index is marked for deletion
            if (base_path, i) in deleted_indices:
                logger.debug(f"Skipping deleted index: {i}")
                continue
                
            if i < len(current_array):
                # If we have form data for this index, update the item
                if i in indices:
                    if isinstance(current_array[i], dict):
                        # Update existing dictionary
                        item = current_array[i].copy()
                        item.update(indices[i])
                        new_array.append(item)
                        logger.debug(f"Updated item at index {i}: {item}")
                    else:
                        # Convert to dictionary if it's not already
                        new_array.append(indices[i])
                        logger.debug(f"Converted item at index {i}: {indices[i]}")
                else:
                    # Keep existing item unchanged
                    new_array.append(current_array[i])
                    logger.debug(f"Kept existing item at index {i}: {current_array[i]}")
            elif i in indices:
                # Add new item
                new_array.append(indices[i])
                logger.debug(f"Added new item at index {i}: {indices[i]}")
        
        # Add any remaining items from the original array, excluding deleted ones
        for i in range(max_index + 1, len(current_array)):
            if (base_path, i) not in deleted_indices:
                new_array.append(current_array[i])
                logger.debug(f"Kept remaining item at index {i}: {current_array[i]}")
            else:
                logger.debug(f"Skipped deleted remaining item at index {i}")
            
        parent[array_name] = new_array
        logger.debug(f"Final array after update: {new_array}")

    # Process regular form fields
    for key in request.form:
        if not key.startswith('__deleted__') and '[' not in key:  # Skip deleted markers and array fields
            value = request.form[key].strip()
            set_nested_value(current_content, key, value)

    # Process file uploads
    for key in request.files:
        file = request.files[key]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(IMAGE_UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            set_nested_value(current_content, key, unique_filename)

    return current_content
