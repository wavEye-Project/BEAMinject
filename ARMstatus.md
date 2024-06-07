# :test_tube: ARM support for BEAMinject
Since version 0.3.0, BEAMinject has added support for ARMv7 and ARM64 platforms!

### :hammer_and_wrench: ARMv7 support
:warning: **WARNING:** ARMv7 support is pretty much experimental, due to lack of Python runtimes and testing platforms. Use at your own risk.

## :zap: Usage
- Install a Python runtime
    - ARM64 is officially supported by Python
    - ARMv7 support is tricky however
- Download BEAMinject's source code
- Exact the source code zipball into a folder
- Install dependencies
    - Open a terminal in the folder
    - Run the following command: `pip install -r requirements.txt`
- Run BEAMinject
    - Silent version: `py BEAMinjector.py`
    - GUI version: `py app.py`
