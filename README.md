# KQIcon Engine

Phosphor icons for PySide6 applications.

## Installation

1. **From Source:**

   Use this command to install directly from the GitHub repository:

   ```bash
   pip install git+https://github.com/krosseye/kq_icon_engine.git
   ```

2. **From Release:**

   To install the latest prebuilt release, you can use the appropriate command for your operating system's shell:

   - **Bash/Linux/MacOS:**

     ```bash
     pip install $(curl -s https://api.github.com/repos/krosseye/kq_icon_engine/releases/latest | grep 'browser_download_url.*\.whl' | cut -d\" -f4)
     ```

   - **PowerShell/Windows:**

     ```powershell
     pip install ( (Invoke-RestMethod -Uri 'https://api.github.com/repos/krosseye/kq_icon_engine/releases/latest').assets | Where-Object { $_.name -like '*.whl' } ).browser_download_url
     ```

## Usage

### Basic Library Icons

The `KQIcon` class allows you to access the bundled icon library by name.

```python
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QColor
from kq_icon_engine import KQIcon, IconStyle

# Simple usage by name
btn = QPushButton()
btn.setIcon(KQIcon("house"))

# Specific style and color
btn_bold = QPushButton()
btn_bold.setIcon(KQIcon("gear", color=QColor("blue"), style=IconStyle.BOLD))
```

### Custom SVG Files

If you have your own SVG assets, `KQCustomIcon` provides the same rendering benefits.

```python
from pathlib import Path
from kq_icon_engine import KQCustomIcon

path = Path("assets/my-custom-icon.svg")
icon = KQCustomIcon(path, color=QColor("red"))
```

### Fill Modes

You can choose between flat colours and vertical gradients.

```python
from kq_icon_engine import KQIcon, FillMode

icon = KQIcon("star", fill=FillMode.GRADIENT)
```

## License

Distributed under the [MIT License](LICENSE).
Bundled [Phosphor Icons](https://phosphoricons.com) are also licensed under the MIT License.

*Copyright © 2026 [Killian W (krosseye)](https://github.com/krosseye).*
