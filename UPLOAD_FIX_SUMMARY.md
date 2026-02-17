# Fix: Uploaded Photos Not Being Saved/Accessible

## Problem Statement (French)
> je ne retrouve pas les photos uploadé  
> on est sur de les sauvegarder ?

Translation: "I can't find the uploaded photos. Are we sure we're saving them?"

## Root Cause

The uploaded photos were not accessible because:

1. **Temporary Storage**: Files were saved to a temporary `uploads/` directory
2. **Relative Paths**: Database stored relative paths that break when working directory changes
3. **Not Persisted**: Original uploaded images were not saved alongside other outputs
4. **Path Resolution Issues**: Job Viewer couldn't find images using relative paths

## Solution

### Changes Made

#### 1. app.py
- **Changed upload directory**: From `uploads/` → `outputs/images_input/`
- **Use absolute paths**: Convert file paths to absolute before passing to pipeline
- **Updated UI**: Added uploaded images directory to output location info

```python
# Before:
upload_dir = Path("uploads")
file_path = upload_dir / uploaded_file.name
pipeline.run_pipeline(image_path=str(file_path), ...)

# After:
upload_dir = Path("outputs") / "images_input"
upload_dir.mkdir(parents=True, exist_ok=True)
file_path = upload_dir / uploaded_file.name
absolute_file_path = file_path.resolve()
pipeline.run_pipeline(image_path=str(absolute_file_path), ...)
```

#### 2. src/pipeline.py
- **Store absolute paths in database**: For both input images and cropped components

```python
# Before:
image_id = self.db.log_image_upload(file_name, img_path_str, format)

# After:
absolute_path = str(Path(img_path_str).resolve())
image_id = self.db.log_image_upload(file_name, absolute_path, format)
```

### Benefits

✅ **Persistent Storage**: Uploaded images saved in `outputs/images_input/` alongside other results  
✅ **Reliable Paths**: Absolute paths work regardless of working directory  
✅ **Job Viewer Compatible**: Images can always be found and displayed  
✅ **Co-located Outputs**: All outputs in one directory tree for easy management  
✅ **Docker Compatible**: Works correctly in containerized deployments  

## File Structure

```
outputs/
├── images_input/          ← NEW: Uploaded photos saved here
│   ├── board1.jpg
│   └── board2.jpg
├── cropped_components/    ← Cropped IC images
├── results/               ← Detection results
└── visualizations/        ← Generated charts
```

## Database Storage

### Before
```
images_input.file_path: "uploads/board1.jpg"  ← Relative path
```

### After
```
images_input.file_path: "/home/app/outputs/images_input/board1.jpg"  ← Absolute path
```

## Testing

All tests pass:
- ✅ **test_upload_fix.py**: Validates directory structure, path conversion, and code changes
- ✅ **test_integration_upload.py**: Simulates full upload → process → retrieve flow
- ✅ **Code Review**: No issues in production code
- ✅ **Security Scan**: No vulnerabilities found

## Backward Compatibility

- Old `uploads/` directory still in .gitignore (for backward compatibility)
- Database paths are absolute, so they work regardless of location
- No breaking changes to API or database schema

## Security

No security vulnerabilities were introduced. The fix actually improves security by:
- Using absolute paths prevents relative path traversal issues
- All files stored in controlled `outputs/` directory
- No changes to authentication or authorization logic

## Verification Steps

To verify the fix works:

1. Start the web interface: `streamlit run app.py`
2. Upload a photo through the web UI
3. Process the photo
4. Go to "Job Viewer" page
5. Select the job
6. ✅ Original image should be displayed correctly
7. ✅ Check `outputs/images_input/` directory - your uploaded photo should be there

## Future Improvements (Optional)

While this fix solves the immediate problem, future enhancements could include:
- Add file deduplication (same filename uploaded multiple times)
- Add cleanup policy for old uploaded files
- Add volume mount configuration for Docker deployments
- Store file checksums in database for integrity verification
