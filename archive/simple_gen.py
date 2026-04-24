from user_scoring.visualization_report import VisualizationReportGenerator
g = VisualizationReportGenerator(db_path='data/holo_half.db')
r = g.generate_comprehensive_report('html')
print('DONE:', r)
