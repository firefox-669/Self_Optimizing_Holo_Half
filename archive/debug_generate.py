import sys
import traceback
from pathlib import Path

print("Step 1: Importing modules...")
try:
    from user_scoring.visualization_report import VisualizationReportGenerator
    print("✓ Import successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Creating generator...")
try:
    generator = VisualizationReportGenerator(db_path="data/holo_half.db")
    print(f"✓ Generator created, report_dir: {generator.report_dir}")
except Exception as e:
    print(f"✗ Generator creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Generating HTML report...")
try:
    html_report = generator.generate_comprehensive_report(output_format="html")
    if html_report:
        print(f"✓ HTML report generated: {html_report}")
        print(f"  File exists: {Path(html_report).exists()}")
        print(f"  File size: {Path(html_report).stat().st_size} bytes")
    else:
        print("✗ HTML report generation returned None")
except Exception as e:
    print(f"✗ HTML report generation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Listing reports directory...")
try:
    reports_dir = Path("reports")
    files = sorted(reports_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
    print(f"Found {len(files)} HTML reports:")
    for f in files[:3]:
        print(f"  - {f.name} ({f.stat().st_size} bytes, modified: {f.stat().st_mtime})")
except Exception as e:
    print(f"✗ Failed to list reports: {e}")

print("\n✓ All steps completed!")
