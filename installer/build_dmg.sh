#!/usr/bin/env bash
# macOS uchun o'rnatuvchi (.dmg) yaratish.
# Talab: avval `pyinstaller hazorasp_sales.spec` orqali dist/HazoraspSalesManagement.app yaratilgan bo'lishi kerak.
#
# Ishlatish:
#   pyinstaller hazorasp_sales.spec
#   bash installer/build_dmg.sh
#
# Natija: installer/output/HazoraspSalesManagement-Setup-<versiya>.dmg

set -euo pipefail

APP_NAME="Hazorasp Sales Management"
APP_VERSION="0.1.0"
APP_BUNDLE="HazoraspSalesManagement.app"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
OUTPUT_DIR="$PROJECT_ROOT/installer/output"
DMG_NAME="HazoraspSalesManagement-Setup-${APP_VERSION}.dmg"

if [[ ! -d "$DIST_DIR/$APP_BUNDLE" ]]; then
    echo "Xato: $DIST_DIR/$APP_BUNDLE topilmadi. Avval quyidagini bajaring:" >&2
    echo "  pyinstaller hazorasp_sales.spec" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR/$DMG_NAME"

STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT

cp -R "$DIST_DIR/$APP_BUNDLE" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$OUTPUT_DIR/$DMG_NAME"

echo "Tayyor: $OUTPUT_DIR/$DMG_NAME"
