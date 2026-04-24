import sys
from pathlib import Path

log_file = Path("report_generation_log.txt")

try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("Starting report generation...\n")
        
        from user_scoring.visualization_report import VisualizationReportGenerator
        f.write("✓ Module imported\n")
        
        g = VisualizationReportGenerator()
        f.write(f"✓ Generator created\n")
        f.write(f"  DB: {g.db_path}\n")
        f.write(f"  Report dir: {g.report_dir}\n")
        
        r = g.generate_comprehensive_report('html')
        f.write(f"✓ Report generated: {r}\n")
        
        if r and Path(r).exists():
            size = Path(r).stat().st_size
            f.write(f"  File size: {size} bytes\n")
            f.write(f"  SUCCESS!\n")
        else:
            f.write(f"  WARNING: File may not exist\n")
            
except Exception as e:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc(file=f)
