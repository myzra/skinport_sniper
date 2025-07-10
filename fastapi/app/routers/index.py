from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import os
import json
import subprocess
import sys
import signal
import psutil
from datetime import datetime
from .models import FilterForm, SaveFilterForm, FilterFormData, SaveFilterFormData, EXTERIOR_CHOICES

router = APIRouter()

# Get the absolute path to templates directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# PID file path (adjust according to your project structure)
PID_FILE = os.path.join(BASE_DIR, 'script_pids.json')
FILTERS_FILE = os.path.join(BASE_DIR, 'saved_filters.json')

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main index page with forms and saved filters"""
    # Create empty form instances
    filter_form = FilterForm()
    save_filter_form = SaveFilterForm()
    
    # Get saved filters from JSON file
    saved_filters = load_saved_filters()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "filter_form": filter_form,
        "save_filter_form": save_filter_form,
        "exterior_choices": EXTERIOR_CHOICES,
        "saved_filters": saved_filters,
        "script_running": is_script_running()
    })

@router.post("/start-script")
async def start_script(request: Request):
    """Start the Node.js and Python scripts"""
    try:
        # Get JSON data from request body
        data = await request.json()
        query_params = {}
        
        # Build query_params dictionary from form data
        if data.get('names'):
            query_params['names'] = data.get('names')
        if data.get('min_price'):
            query_params['minPrice'] = data.get('min_price')
        if data.get('max_price'):
            query_params['maxPrice'] = data.get('max_price')
        if data.get('patterns'):
            query_params['patterns'] = data.get('patterns')
        if data.get('min_wear'):
            query_params['minWear'] = data.get('min_wear')
        if data.get('max_wear'):
            query_params['maxWear'] = data.get('max_wear')
        if data.get('exterior'):
            query_params['exterior'] = data.get('exterior')
        
        # Write query_params to a file that the script can read
        with open(os.path.join(BASE_DIR, 'script_params.json'), 'w') as f:
            json.dump(query_params, f)
        
        # Start api_client.js without parameters
        node_path = os.path.join(BASE_DIR, '..', '..', 'core', 'api_client.js')
        node_proc = subprocess.Popen(['node', node_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Start data_parser.py with path to JSON file as argument
        python_executable = sys.executable
        python_path = os.path.join(BASE_DIR, '..', '..', 'core', 'data_parser.py')
        py_proc = subprocess.Popen([python_executable, python_path], stdout=None, stderr=None)

        # Save PIDs to file
        with open(PID_FILE, 'w') as f:
            json.dump({'node_pid': node_proc.pid, 'python_pid': py_proc.pid}, f)

        return JSONResponse({'status': 'success', 'message': 'Script started successfully'})
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})

@router.post("/stop-script")
async def stop_script():
    """Stop the running scripts"""
    try:
        if not os.path.exists(PID_FILE):
            return JSONResponse({'status': 'error', 'message': 'No PID file found'})
        
        with open(PID_FILE, 'r') as f:
            pids = json.load(f)

        stopped = []
        for key in ['node_pid', 'python_pid']:
            pid = pids.get(key)
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    stopped.append(f'{key} (PID {pid})')
                except ProcessLookupError:
                    continue

        os.remove(PID_FILE)
        return JSONResponse({'status': 'success', 'message': f'Stopped: {", ".join(stopped)}'})
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})

@router.get("/get-script-output")
async def get_script_output():
    """Get the output from the script logs"""
    file_path = os.path.join(BASE_DIR, '..', '..', 'logs', 'listings.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if not content:
                content = 'Waiting for logs...'
    else:
        content = "No listings found"
    return JSONResponse({'output': content})

def is_script_running():
    """Check if the target scripts are running"""
    target_scripts = ['api_client.js', 'data_parser.py']
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
            for target in target_scripts:
                if any(target in part for part in cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def generate_filter_id():
    """Generate a unique ID for a filter"""
    saved_filters = load_saved_filters()
    if not saved_filters:
        return 1
    
    max_id = max([f.get('id', 0) for f in saved_filters])
    return max_id + 1

def load_saved_filters():
    """Load saved filters from JSON file and parse datetime strings"""
    if not os.path.exists(FILTERS_FILE):
        return []
    
    try:
        with open(FILTERS_FILE, 'r') as f:
            filters = json.load(f)
            
            # Parse datetime strings back to datetime objects for template rendering
            for filter_data in filters:
                if 'created_at' in filter_data:
                    if isinstance(filter_data['created_at'], str):
                        try:
                            filter_data['created_at'] = datetime.fromisoformat(filter_data['created_at'])
                        except ValueError:
                            # If parsing fails, use current datetime
                            filter_data['created_at'] = datetime.now()
                    # If created_at is missing or None, set to current datetime
                    elif filter_data['created_at'] is None:
                        filter_data['created_at'] = datetime.now()
                else:
                    # Add created_at if it doesn't exist
                    filter_data['created_at'] = datetime.now()
            
            return filters
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_filter_to_file(filter_data):
    """Save a filter to the JSON file"""
    if not os.path.exists(FILTERS_FILE):
        saved_filters = []
    else:
        try:
            with open(FILTERS_FILE, 'r') as f:
                saved_filters = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            saved_filters = []
    
    saved_filters.append(filter_data)
    
    with open(FILTERS_FILE, 'w') as f:
        json.dump(saved_filters, f, indent=2)

def delete_filter_from_file(filter_id):
    """Delete a saved filter from JSON file"""
    if not os.path.exists(FILTERS_FILE):
        return False
    
    try:
        with open(FILTERS_FILE, 'r') as f:
            saved_filters = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return False
    
    # Remove the filter
    updated_filters = [f for f in saved_filters if f['id'] != filter_id]
    
    if len(updated_filters) == len(saved_filters):
        return False  # Filter not found
    
    # Save updated filters back to file
    with open(FILTERS_FILE, 'w') as f:
        json.dump(updated_filters, f, indent=2)
    
    return True

@router.post("/save-filter")
async def save_filter(request: Request):
    """Save a filter configuration via JSON"""
    try:
        data = await request.json()
        
        # Debug: Print received data
        print("Received data:", data)
        
        filter_name = data.get('filter_name')
        
        if not filter_name:
            return JSONResponse({'status': 'error', 'message': 'Filter name is required'})
        
        # Create filter setting object - make sure we're getting the right keys
        filter_data = {
            'id': generate_filter_id(),
            'name': filter_name,
            'names': data.get('names', ''),
            'min_price': data.get('min_price', ''),
            'max_price': data.get('max_price', ''),
            'patterns': data.get('patterns', ''),
            'min_wear': data.get('min_wear', ''),
            'max_wear': data.get('max_wear', ''),
            'exterior': data.get('exterior', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # Debug: Print filter data being saved
        print("Filter data being saved:", filter_data)
        
        save_filter_to_file(filter_data)
        
        return JSONResponse({
            'status': 'success', 
            'message': 'Filter saved successfully',
            'filter_id': filter_data['id'],
            'filter_name': filter_name
        })
    except Exception as e:
        print("Error in save_filter:", str(e))
        return JSONResponse({'status': 'error', 'message': str(e)})

@router.get("/load-filter/{filter_id}")
async def load_filter(filter_id: int):
    """Load a saved filter by ID"""
    try:
        saved_filters = load_saved_filters()
        
        # Find the filter with the matching ID
        filter_data = None
        for f in saved_filters:
            if f.get('id') == filter_id:
                filter_data = f
                break
        
        if not filter_data:
            return JSONResponse({'status': 'error', 'message': 'Filter not found'})
        
        # Convert datetime to string if it exists
        created_at = filter_data.get('created_at')
        if created_at:
            # If it's a datetime object, convert to string
            if hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
            # If it's already a string, keep it as is
        
        # Return the filter data
        return JSONResponse({
            'status': 'success',
            'filter': {
                'id': filter_data.get('id'),
                'name': filter_data.get('name'),
                'names': filter_data.get('names', ''),
                'min_price': filter_data.get('min_price', ''),
                'max_price': filter_data.get('max_price', ''),
                'patterns': filter_data.get('patterns', ''),
                'min_wear': filter_data.get('min_wear', ''),
                'max_wear': filter_data.get('max_wear', ''),
                'exterior': filter_data.get('exterior', ''),
                'created_at': created_at
            }
        })
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})

@router.post("/delete-filter/{filter_id}")
async def delete_filter(filter_id: int):
    """Delete a saved filter by ID"""
    try:
        success = delete_filter_from_file(filter_id)
        
        if success:
            return JSONResponse({
                'status': 'success',
                'message': 'Filter deleted successfully'
            })
        else:
            return JSONResponse({
                'status': 'error',
                'message': 'Filter not found'
            })
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})

# === OPTIONAL: Keep only if you need form-based operations ===

@router.post("/filter", response_class=HTMLResponse)
async def filter_items(
    request: Request,
    names: Optional[str] = Form(None),
    min_price: Optional[str] = Form(None),
    max_price: Optional[str] = Form(None),
    patterns: Optional[str] = Form(None),
    min_wear: Optional[str] = Form(None),
    max_wear: Optional[str] = Form(None),
    exterior: Optional[str] = Form(None),
):
    """Process filter form submission"""
    # Create form data
    form_data = {
        'names': names,
        'min_price': min_price,
        'max_price': max_price,
        'patterns': patterns,
        'min_wear': min_wear,
        'max_wear': max_wear,
        'exterior': exterior,
    }
    
    # Create form instance with data
    filter_form = FilterForm(form_data)
    save_filter_form = SaveFilterForm()
    
    # Validate form
    if filter_form.is_valid():
        messages = [{"tags": "success", "text": "Filter applied successfully!"}]
    else:
        messages = [{"tags": "error", "text": "Please correct the errors below."}]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "filter_form": filter_form,
        "save_filter_form": save_filter_form,
        "exterior_choices": EXTERIOR_CHOICES,
        "messages": messages,
        "saved_filters": load_saved_filters(),
        "script_running": is_script_running()
    })