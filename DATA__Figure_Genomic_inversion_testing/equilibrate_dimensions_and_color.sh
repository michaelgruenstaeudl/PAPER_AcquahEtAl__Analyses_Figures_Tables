#!/usr/bin/env bash

images=(
    GEL_Inv2.jpeg
)

# Find minimum height
min_h=$(identify -format "%h\n" "${images[@]}" | sort -n | head -1)
echo "Target height: $min_h px"

# Find minimum width after scaling to min height
min_w=$(
    for img in "${images[@]}"; do
        read -r w h <<<"$(identify -format "%w %h" "$img")"
        awk -v w="$w" -v h="$h" -v mh="$min_h" 'BEGIN { printf "%d\n", (w * mh) / h }'
    done | sort -n | head -1
)
echo "Target width: $min_w px"

# Scale all images to exact dimensions, convert to grayscale, equilibrate tones, and sharpen
for img in "${images[@]}"; do
    convert "$img" -resize x${min_h} -resize "${min_w}x${min_h}!" -colorspace Gray -auto-level -sharpen 0x1.0 "scaled_${img}"
    echo "Saved: scaled_${img}"
done
