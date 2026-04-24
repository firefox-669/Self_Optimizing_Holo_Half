import sys
print("Python version:", sys.version)
print("Current dir:", __file__)

try:
    print("\nTrying to import...")
    from user_scoring.visualization_report import VisualizationReportGenerator
    print("Import OK!")
    
    print("\nCreating generator...")
    g = VisualizationReportGenerator()
    print("Generator created!")
    print("DB path:", g.db_path)
    print("Report dir:", g.report_dir)
    
    print("\nGenerating report...")
    r = g.generate_comprehensive_report('html')
    print("Result:", r)
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
