#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------
# Usage
# ----------------------------------------
# Example:
# ./make_Figure1.sh /path/to/input_folder Figure1.jpg

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 INPUT_FOLDER OUTPUT_FILE"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_FILE="$2"

# ----------------------------------------
# Settings
# ----------------------------------------
FONT="DejaVu-Sans-Bold"
HEIGHT=1800
GAP=60
POINTSIZE=140
OFFSET="+50+50"
RIM=10

# ----------------------------------------
# Input files
# ----------------------------------------
IMG1A="${INPUT_DIR}/img1a.jpg"
IMG1B="${INPUT_DIR}/img1b.jpg"

# ----------------------------------------
# Check files
# ----------------------------------------
for f in "$IMG1A" "$IMG1B"
do
    if [ ! -f "$f" ]; then
        echo "Missing file: $f"
        exit 1
    fi
done

# ----------------------------------------
# Helper arguments
# ----------------------------------------
label_args=(
  -font "$FONT"
  -gravity northwest
  -pointsize "$POINTSIZE"
)

# ----------------------------------------
# Create figure
# ----------------------------------------
convert \
  \( "$IMG1A" -resize x${HEIGHT} \
     "${label_args[@]}" \
     -stroke white -strokewidth "$RIM" -fill black \
     -annotate "$OFFSET" "A" \) \
  \( "$IMG1B" -resize x${HEIGHT} \
     "${label_args[@]}" \
     -stroke white -strokewidth "$RIM" -fill black \
     -annotate "$OFFSET" "B" \) \
  -background white +smush "$GAP" \
  -units PixelsPerInch -density 600 \
  -quality 100 \
  "$OUTPUT_FILE"

echo "Created: $OUTPUT_FILE"
