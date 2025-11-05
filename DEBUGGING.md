# Python Debugging Guide

This guide covers multiple ways to debug your Python application.

## 🎯 Quick Start - VS Code Debugging

### Method 1: Use VS Code Debug Panel (Recommended)

1. **Set breakpoints**: Click in the gutter (left of line numbers) in any Python file
2. **Open Debug Panel**: Press `F5` or click the Debug icon in the sidebar
3. **Select configuration**: Choose one of these:
   - **Python: Flask (Main App)** - Debug the Flask web server
   - **Python: Detector Script** - Debug the YOLO detector script
   - **Python: Current File** - Debug the currently open file
4. **Start debugging**: Press `F5` or click the green play button

### Debugging Controls:
- **F5** - Continue/Start
- **F10** - Step Over
- **F11** - Step Into
- **Shift+F11** - Step Out
- **Shift+F5** - Stop
- **Ctrl+Shift+F5** - Restart

### View Variables:
- Hover over variables to see their values
- Check the "Variables" panel in the Debug sidebar
- Use the "Debug Console" to evaluate expressions

---

## 🔧 Method 2: Command-Line Debugging with `pdb`

### Quick Breakpoint Insertion

Add this line where you want to break:
```python
import pdb; pdb.set_trace()
```

Or use `breakpoint()` (Python 3.7+):
```python
breakpoint()  # Automatically uses the configured debugger
```

### Example in Flask Route:
```python
@detector_bp.route("/detector/detect", methods=["POST"])
def detect_image():
    breakpoint()  # Execution will pause here
    # Your code...
```

### pdb Commands:
- `n` (next) - Execute next line
- `s` (step) - Step into function
- `c` (continue) - Continue execution
- `l` (list) - Show current code
- `p <variable>` - Print variable value
- `pp <variable>` - Pretty print variable
- `q` (quit) - Quit debugger
- `h` (help) - Show all commands

### Run with pdb from terminal:
```bash
python -m pdb -m server.app
# or
python -m pdb server/detector/main.py
```

---

## 📝 Method 3: Logging for Debugging

### Setup Logging in Your Code:

Add to the top of your Python files:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Use in Your Code:
```python
logger.debug("Debug message - detailed info")
logger.info("Info message - general info")
logger.warning("Warning message - potential issues")
logger.error("Error message - errors occurred")
logger.critical("Critical message - serious problems")
```

### View Logs:
Logs will appear in the VS Code terminal or wherever you run the app.

---

## 🚀 Method 4: Attach to Running Process

### Start your app with debugpy:

1. Add this to your code (temporarily):
```python
import debugpy

# Start debug server on port 5678
debugpy.listen(5678)
print("Waiting for debugger to attach...")
debugpy.wait_for_client()  # Optional: wait for debugger
```

2. Run your app normally:
```bash
python -m server.app
```

3. In VS Code:
   - Select "Python: Attach to Process" configuration
   - Press F5
   - The debugger will connect to your running process

---

## 🎨 Method 5: Flask Debug Mode

Your Flask app already has debug mode enabled in `server/app.py`:
```python
app.run(host="0.0.0.0", port=8080, debug=True)
```

This provides:
- **Auto-reload**: Code changes restart the server
- **Better error pages**: Detailed tracebacks in browser
- **Debug toolbar**: Interactive debugger in browser (if enabled)

### To disable for production:
Change `debug=True` to `debug=False` in `server/app.py`

---

## 🐛 Common Debugging Scenarios

### Debugging Flask Routes:

1. Set a breakpoint in any route function
2. Use "Python: Flask (Main App)" configuration
3. Make a request to that endpoint
4. Execution will pause at your breakpoint

### Debugging Detector Script:

1. Open `server/detector/main.py`
2. Set breakpoints where needed
3. Use "Python: Detector Script" configuration
4. Press F5

### Debugging Import Errors:

```python
try:
    from utils.detector_utils import detect_objects
except ImportError as e:
    print(f"Import error: {e}")
    import sys
    print(f"Python path: {sys.path}")
    breakpoint()  # Inspect sys.path
```

### Debugging Environment Variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()
breakpoint()  # Check loaded env vars
print(os.environ.get('YOUR_VAR'))
```

---

## 🔍 VS Code Debugging Tips

### Conditional Breakpoints:
- Right-click on a breakpoint
- Choose "Edit Breakpoint"
- Add a condition (e.g., `x > 5`)

### Logpoints:
- Right-click in gutter
- Choose "Add Logpoint"
- Enter message (e.g., `Variable x is {x}`)
- Execution logs without stopping

### Watch Expressions:
- Add variables to "Watch" panel
- Monitor expressions like `len(detections) > 0`

### Call Stack:
- View "Call Stack" panel to see function call hierarchy
- Click any frame to jump to that code location

---

## 📚 Additional Resources

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Python pdb Documentation](https://docs.python.org/3/library/pdb.html)
- [Flask Debugging](https://flask.palletsprojects.com/en/latest/debugging/)

---

## ✅ Quick Debugging Checklist

- [ ] Set breakpoints in problematic code
- [ ] Check variables panel for unexpected values
- [ ] Review call stack for execution flow
- [ ] Check terminal for error messages
- [ ] Verify environment variables are loaded
- [ ] Ensure virtual environment is activated
- [ ] Check Python path includes your modules
- [ ] Review logs for clues

---

## 🆘 Troubleshooting

### Debugger not attaching?
- Ensure `.venv/bin/python3` exists
- Check Python extension is installed in VS Code
- Verify `debugpy` is installed: `pip install debugpy`

### Breakpoints not hit?
- Ensure code is actually executing (check with print statements)
- Verify you're using the correct debug configuration
- Check that `justMyCode` setting allows debugging into libraries if needed

### Import errors while debugging?
- Verify `cwd` in launch.json is correct
- Check `sys.path` in debug console
- Ensure virtual environment is activated
