#!/usr/bin/env bash

set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
fi

repo_root="$1"

if [ ! -d "$repo_root" ]; then
  echo "Repository path not found: $repo_root" >&2
  exit 1
fi

if [ "${repo_root#/}" = "$repo_root" ]; then
  echo "Pass an absolute repo path." >&2
  exit 1
fi

find_first() {
  local maxdepth="$1"
  shift
  find "$repo_root" \
    \( -path '*/.git' -o \
       -path '*/node_modules' -o \
       -path '*/dist' -o \
       -path '*/build' -o \
       -path '*/.build' -o \
       -path '*/target' -o \
       -path '*/coverage' -o \
       -path '*/.next' -o \
       -path '*/.turbo' -o \
       -path '*/.cache' -o \
       -path '*/.parcel-cache' -o \
       -path '*/.vite' -o \
       -path '*/.pytest_cache' -o \
       -path '*/__pycache__' -o \
       -path '*/venv' -o \
       -path '*/.venv' \) -prune -o \
    -maxdepth "$maxdepth" "$@" -print 2>/dev/null | sort | head -n 1
}

rel_path() {
  local path="${1:-}"
  if [ -z "$path" ]; then
    echo "none detected"
  elif [ "$path" = "$repo_root" ]; then
    echo "."
  else
    echo "${path#"$repo_root"/}"
  fi
}

extract_package_script() {
  local file="$1"
  local key="$2"
  awk -v key="\"$key\"" '
    /"scripts"[[:space:]]*:/ { in_scripts=1 }
    in_scripts && index($0, key) {
      line=$0
      sub(/^[^:]*:[[:space:]]*"/, "", line)
      sub(/".*$/, "", line)
      print line
      exit
    }
    in_scripts && /^[[:space:]]*}[[:space:]]*,?[[:space:]]*$/ { exit }
  ' "$file"
}

choose_package_command() {
  local file="$1"
  shift
  local runner="npm run"

  if [ -z "$file" ] || [ ! -f "$file" ]; then
    return 0
  fi

  if [ -f "$(dirname "$file")/pnpm-lock.yaml" ]; then
    runner="pnpm"
  elif [ -f "$(dirname "$file")/yarn.lock" ]; then
    runner="yarn"
  fi

  local key
  for key in "$@"; do
    if [ -n "$(extract_package_script "$file" "$key")" ]; then
      if [ "$runner" = "npm run" ]; then
        echo "$runner $key"
      else
        echo "$runner $key"
      fi
      return
    fi
  done
}

first_grep_match() {
  local pattern="$1"
  local path
  path="$(find "$repo_root" \
    \( -path '*/.git' -o \
       -path '*/node_modules' -o \
       -path '*/dist' -o \
       -path '*/build' -o \
       -path '*/.build' -o \
       -path '*/target' -o \
       -path '*/coverage' -o \
       -path '*/.next' -o \
       -path '*/.turbo' -o \
       -path '*/.cache' -o \
       -path '*/.parcel-cache' -o \
       -path '*/.vite' -o \
       -path '*/.pytest_cache' -o \
       -path '*/__pycache__' -o \
       -path '*/venv' -o \
       -path '*/.venv' \) -prune -o \
    -maxdepth 5 -type f \
    \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o \
       -name '*.py' -o -name '*.swift' -o -name '*.rs' -o -name '*.css' -o \
       -name '*.scss' -o -name '*.json' -o -name '*.toml' \) \
    -print0 2>/dev/null | xargs -0 grep -Eil "$pattern" 2>/dev/null | sort | head -n 1 || true)"
  echo "$path"
}

extract_port_from_file() {
  local file="$1"
  if [ -f "$file" ]; then
    grep -Eo 'localhost:[0-9]{3,5}|[Pp][Oo][Rr][Tt][^0-9]{0,20}[0-9]{3,5}|--port[ =][0-9]{3,5}' "$file" 2>/dev/null \
      | grep -Eo '[0-9]{3,5}' | head -n 1 || true
  fi
}

package_json="$(find_first 3 -type f -name 'package.json')"
pyproject_toml="$(find_first 3 -type f -name 'pyproject.toml')"
requirements_txt="$(find_first 3 -type f -name 'requirements.txt')"
requirements_dev_txt="$(find_first 3 -type f -name 'requirements-dev.txt')"
cargo_toml="$(find_first 3 -type f -name 'Cargo.toml')"
package_swift="$(find_first 3 -type f -name 'Package.swift')"
angular_json="$(find_first 3 -type f -name 'angular.json')"
next_config="$(find_first 3 -type f -name 'next.config.*')"
vite_config="$(find_first 3 -type f -name 'vite.config.*')"
nuxt_config="$(find_first 3 -type f -name 'nuxt.config.*')"
astro_config="$(find_first 3 -type f -name 'astro.config.*')"
xcodeproj="$(find_first 4 -name '*.xcodeproj')"
xcworkspace="$(find_first 4 -name '*.xcworkspace')"
manage_py="$(find_first 4 -type f -name 'manage.py')"

start_file="$(find_first 4 -type f -name 'main.tsx')"
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'main.jsx')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'main.ts')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'main.js')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'App.tsx')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'App.jsx')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'app.py')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'main.py')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name '__main__.py')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'manage.py')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'main.rs')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name '*App.swift')"; fi
if [ -z "$start_file" ]; then start_file="$(find_first 4 -type f -name 'ContentView.swift')"; fi

router_file="$(find_first 5 -type f \( \
  -iname '*router*.ts' -o \
  -iname '*router*.tsx' -o \
  -iname '*router*.js' -o \
  -iname '*router*.jsx' -o \
  -iname '*router*.swift' -o \
  -iname '*routes*.ts' -o \
  -iname '*routes*.tsx' -o \
  -iname '*routes*.js' -o \
  -iname '*routes*.jsx' -o \
  -iname '*routes*.swift' -o \
  -path '*/app/page.tsx' -o \
  -path '*/app/page.ts' -o \
  -path '*/app/page.jsx' -o \
  -path '*/app/page.js' -o \
  -path '*/src/app/page.tsx' -o \
  -path '*/src/app/page.ts' -o \
  -path '*/src/app/page.jsx' -o \
  -path '*/src/app/page.js' -o \
  -path '*/pages/*.tsx' -o \
  -path '*/pages/*.ts' -o \
  -path '*/pages/*.jsx' -o \
  -path '*/pages/*.js' \
  \))"

dark_mode_match="$(first_grep_match 'prefers-color-scheme|ThemeProvider|dark mode|dark:|[Tt]heme')"

python_web_framework=""
for dep_file in "$pyproject_toml" "$requirements_txt" "$requirements_dev_txt"; do
  if [ -z "$dep_file" ] || [ ! -f "$dep_file" ]; then
    continue
  fi

  if grep -Eiq 'streamlit' "$dep_file" 2>/dev/null; then
    python_web_framework="streamlit"
    break
  elif grep -Eiq 'flask' "$dep_file" 2>/dev/null; then
    python_web_framework="flask"
    break
  elif grep -Eiq 'django' "$dep_file" 2>/dev/null; then
    python_web_framework="django"
    break
  elif grep -Eiq 'fastapi|uvicorn' "$dep_file" 2>/dev/null; then
    python_web_framework="fastapi"
    break
  fi
done

python_gui_file="$(first_grep_match '^[[:space:]]*(from|import)[[:space:]]+(tkinter|PyQt5|PyQt6|PySide|PySide2|PySide6|kivy)')"

app_type="cli"
framework="unknown"
dev_command="none detected"
dev_port="n/a"

if [ -n "$package_json" ] && grep -Eiq '"electron"|electron[[:space:]]*:' "$package_json"; then
  app_type="electron"
  framework="electron"
  framework_detail="$(first_grep_match 'next|vite|react|vue|svelte')"
  if [ -n "$framework_detail" ]; then
    framework="electron + web shell"
  fi
  dev_command="$(choose_package_command "$package_json" dev start electron desktop app || true)"
  if [ -z "$dev_command" ]; then
    dev_command="npm run dev"
  fi
elif [ -n "$next_config" ]; then
  app_type="web-next"
  framework="next.js"
  dev_command="$(choose_package_command "$package_json" dev start || true)"
  if [ -z "$dev_command" ]; then
    dev_command="npm run dev"
  fi
  dev_port="$(extract_port_from_file "$next_config")"
  if [ -z "$dev_port" ] && [ -n "$package_json" ]; then
    dev_port="$(extract_port_from_file "$package_json")"
  fi
  if [ -z "$dev_port" ]; then
    dev_port="3000"
  fi
elif [ -n "$vite_config" ]; then
  app_type="web-vite"
  framework="vite"
  if [ -n "$package_json" ] && grep -Eiq '"react"|react-dom' "$package_json"; then
    framework="vite + react"
  elif [ -n "$package_json" ] && grep -Eiq '"vue"' "$package_json"; then
    framework="vite + vue"
  elif [ -n "$package_json" ] && grep -Eiq '"svelte"' "$package_json"; then
    framework="vite + svelte"
  fi
  dev_command="$(choose_package_command "$package_json" dev start || true)"
  if [ -z "$dev_command" ]; then
    dev_command="npm run dev"
  fi
  dev_port="$(extract_port_from_file "$vite_config")"
  if [ -z "$dev_port" ] && [ -n "$package_json" ]; then
    dev_port="$(extract_port_from_file "$package_json")"
  fi
  if [ -z "$dev_port" ]; then
    dev_port="5173"
  fi
elif [ -n "$package_json" ] || [ -n "$angular_json" ] || [ -n "$nuxt_config" ] || [ -n "$astro_config" ]; then
  if [ -n "$angular_json" ] || ([ -n "$package_json" ] && grep -Eiq 'react-scripts|next|nuxt|astro|gatsby|vite|angular' "$package_json"); then
    app_type="web-other"
    framework="web app"
    if [ -n "$angular_json" ]; then
      framework="angular"
      dev_port="4200"
    elif [ -n "$nuxt_config" ] || ([ -n "$package_json" ] && grep -Eiq '"nuxt"' "$package_json"); then
      framework="nuxt"
      dev_port="3000"
    elif [ -n "$astro_config" ] || ([ -n "$package_json" ] && grep -Eiq '"astro"' "$package_json"); then
      framework="astro"
      dev_port="4321"
    elif [ -n "$package_json" ] && grep -Eiq 'react-scripts' "$package_json"; then
      framework="react-scripts"
      dev_port="3000"
    fi
    dev_command="$(choose_package_command "$package_json" dev start serve || true)"
    if [ -z "$dev_command" ]; then
      dev_command="npm run dev"
    fi
    if [ "$dev_port" = "n/a" ] || [ -z "$dev_port" ]; then
      if [ -n "$package_json" ]; then
        dev_port="$(extract_port_from_file "$package_json")"
      fi
      if [ -z "$dev_port" ]; then
        dev_port="3000"
      fi
    fi
  fi
fi

if [ "$app_type" = "cli" ] && [ -n "$python_web_framework" ]; then
  app_type="python-web"
  framework="$python_web_framework"
  if [ "$python_web_framework" = "streamlit" ]; then
    if [ -z "$start_file" ] || [ "$start_file" = "none detected" ]; then
      start_file="$(find_first 4 -type f -name '*.py')"
    fi
    dev_command="streamlit run $(rel_path "$start_file")"
    dev_port="8501"
  elif [ "$python_web_framework" = "flask" ]; then
    if [ -n "$manage_py" ]; then
      dev_command="python $(rel_path "$manage_py") runserver"
      dev_port="5000"
    else
      dev_command="flask run"
      dev_port="5000"
    fi
  elif [ "$python_web_framework" = "django" ]; then
    dev_command="python $(rel_path "$manage_py") runserver"
    dev_port="8000"
  else
    dev_command="uvicorn app:app --reload"
    dev_port="8000"
  fi
fi

if [ "$app_type" = "cli" ] && [ -n "$python_gui_file" ]; then
  app_type="python-gui"
  framework="python gui"
  if grep -Eiq 'tkinter' "$python_gui_file"; then
    framework="tkinter"
  elif grep -Eiq 'PyQt5' "$python_gui_file"; then
    framework="PyQt5"
  elif grep -Eiq 'PyQt6' "$python_gui_file"; then
    framework="PyQt6"
  elif grep -Eiq 'PySide' "$python_gui_file"; then
    framework="PySide"
  elif grep -Eiq 'kivy' "$python_gui_file"; then
    framework="kivy"
  fi
  start_file="$python_gui_file"
  dev_command="python $(rel_path "$start_file")"
fi

if [ "$app_type" = "cli" ] && { [ -n "$xcodeproj" ] || [ -n "$xcworkspace" ] || [ -n "$package_swift" ] || { [ -n "$cargo_toml" ] && grep -Eiq 'tauri' "$cargo_toml"; }; }; then
  app_type="macos-native"
  framework="macOS native"
  if [ -n "$cargo_toml" ] && grep -Eiq 'tauri' "$cargo_toml"; then
    framework="tauri"
    if [ -n "$package_json" ]; then
      dev_command="$(choose_package_command "$package_json" tauri dev || true)"
    fi
    if [ -z "$dev_command" ]; then
      dev_command="cargo tauri dev"
    fi
  elif [ -n "$package_swift" ]; then
    framework="swift package"
    dev_command="swift run"
  elif [ -n "$xcworkspace" ]; then
    dev_command="open $(rel_path "$xcworkspace")"
  elif [ -n "$xcodeproj" ]; then
    dev_command="open $(rel_path "$xcodeproj")"
  fi
fi

if [ -z "$dark_mode_match" ]; then
  has_dark_mode="no"
else
  has_dark_mode="yes"
fi

echo "App Type: $app_type"
echo "Framework: $framework"
echo "Dev Command: $dev_command"
echo "Dev Port: $dev_port"
echo "Start File: $(rel_path "$start_file")"
echo "Has Dark Mode: $has_dark_mode"
echo "Router File: $(rel_path "$router_file")"
