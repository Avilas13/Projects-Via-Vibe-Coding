# Advanced Scientific Calculator

Two implementations of an advanced scientific calculator:

| Version | Technology | How to open |
|---------|------------|-------------|
| **Web-based** | HTML + CSS + JavaScript (zero dependencies) | Open `web/index.html` in any browser |
| **GUI-based** | Python 3 + tkinter (standard library only) | `python gui/calculator.py` |

---

## Features

Both calculators share the same feature set.

### Basic Arithmetic
| Operation | Button |
|-----------|--------|
| Addition | `+` |
| Subtraction | `−` |
| Multiplication | `×` |
| Division | `÷` |
| Modulo | `mod` |
| Percentage | `%` |

### Scientific Functions
| Category | Functions |
|----------|-----------|
| Trigonometry | sin, cos, tan |
| Inverse trig | sin⁻¹, cos⁻¹, tan⁻¹ |
| Logarithms | log (base 10), ln (natural log), log₂ |
| Exponential | eˣ |
| Powers | x², x³, xʸ (arbitrary power) |
| Roots | √x (square root), ∛x (cube root) |
| Other | 1/x, \|x\| (absolute value), x! (factorial) |

### Constants
- **π** ≈ 3.14159265358979…
- **e** ≈ 2.71828182845905…

### Angle Modes
Switch between **DEG** (degrees), **RAD** (radians), and **GRAD** (gradians) for all trigonometric operations.

### Memory Functions
| Button | Action |
|--------|--------|
| MC | Memory Clear |
| MR | Memory Recall |
| M+ | Add display value to memory |
| M− | Subtract display value from memory |
| MS | Memory Store (overwrite) |

### Other
- **ANS** – recall the last calculated result
- **+/−** – toggle positive/negative sign
- **History** – view the last 50 calculations; click any entry to reuse its result
- Full **keyboard support** (see table below)

---

## Running the Web Calculator

Open `web/index.html` directly in any modern browser — no server or build step required.

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `0`–`9`, `.` | Digit / decimal point |
| `+`, `-`, `*` | Arithmetic operators |
| `/` | Division |
| `%` | Percentage |
| `Enter` / `=` | Calculate (=) |
| `Backspace` | Delete last character |
| `Escape` | All Clear (AC) |
| `Delete` | Clear Entry (CE) |

---

## Running the GUI Calculator

Requires **Python 3.8+** with `tkinter` (bundled with Python on Windows and macOS).

```bash
cd scientific-calculator/gui
python calculator.py
```

On some Linux distributions tkinter must be installed separately:

```bash
# Debian / Ubuntu
sudo apt-get install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter
```

The GUI calculator supports the same keyboard shortcuts as the web version.
