"""
SOHH 邮件告警系统

当检测到高风险安全问题时自动发送邮件通知
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class EmailAlertSystem:
    """邮件告警系统"""
    
    def __init__(self, config_file: str = None):
        """
        初始化邮件告警系统
        
        Args:
            config_file: 配置文件路径（JSON格式）
        """
        self.config_file = config_file or Path(__file__).parent / "email_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载邮件配置"""
        if not self.config_file.exists():
            # 创建默认配置模板
            default_config = {
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "your_email@example.com",
                "password": "your_password",
                "use_tls": True,
                "recipients": [
                    "admin@example.com",
                    "security-team@example.com"
                ],
                "alert_thresholds": {
                    "critical_score": 30,  # 低于此分数发送紧急告警
                    "high_risk_count": 3   # 高风险项超过此数量发送告警
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            print(f"⚠️ 已创建默认邮件配置文件: {self.config_file}")
            print("请编辑该文件填入您的邮件服务器信息")
            return default_config
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def send_alert(self, assessment_report: Dict[str, Any]) -> bool:
        """
        发送安全告警邮件
        
        Args:
            assessment_report: 安全评估报告
            
        Returns:
            是否发送成功
        """
        # 检查是否需要发送告警
        if not self._should_send_alert(assessment_report):
            return False
        
        # 构建邮件内容
        subject, body = self._build_email_content(assessment_report)
        
        # 发送邮件
        try:
            self._send_email(subject, body)
            print(f"✅ 告警邮件已发送至: {', '.join(self.config['recipients'])}")
            return True
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def _should_send_alert(self, report: Dict[str, Any]) -> bool:
        """判断是否应该发送告警"""
        thresholds = self.config.get('alert_thresholds', {})
        
        # 检查安全评分
        safety_score = report.get('safety_score', 100)
        critical_score = thresholds.get('critical_score', 30)
        
        if safety_score < critical_score:
            return True
        
        # 检查高风险项数量
        high_risk_count = report.get('risky_commands', 0)
        max_high_risk = thresholds.get('high_risk_count', 3)
        
        if high_risk_count > max_high_risk:
            return True
        
        # 检查是否有严重风险
        top_risks = report.get('top_risks', [])
        has_critical = any(r.get('severity', 0) >= 9 for r in top_risks)
        
        if has_critical:
            return True
        
        return False
    
    def _build_email_content(self, report: Dict[str, Any]) -> tuple:
        """构建邮件内容"""
        safety_score = report.get('safety_score', 0)
        
        # 确定告警级别
        if safety_score < 30:
            alert_level = "🚨 紧急"
        elif safety_score < 50:
            alert_level = "⚠️  高危"
        else:
            alert_level = "💡 警告"
        
        # 邮件主题
        subject = f"[SOHH安全告警] {alert_level} - 安全评分: {safety_score}/100"
        
        # 邮件正文
        body = f"""
<html>
<body>
<h2>{alert_level} SOHH安全评估告警</h2>

<h3>📊 评估摘要</h3>
<ul>
    <li><strong>安全评分</strong>: {safety_score}/100</li>
    <li><strong>安全等级</strong>: {report.get('level_description', 'N/A')}</li>
    <li><strong>总命令数</strong>: {report.get('total_commands', 0)}</li>
    <li><strong>风险命令数</strong>: {report.get('risky_commands', 0)}</li>
    <li><strong>检测到的风险</strong>: {report.get('total_risks_detected', 0)}</li>
</ul>

<h3>⚠️ 最严重的风险</h3>
<ul>
"""
        
        top_risks = report.get('top_risks', [])[:5]
        for risk in top_risks:
            body += f"<li>{risk.get('name', 'Unknown')} (严重程度: {risk.get('severity', 0)})</li>\n"
        
        body += """
</ul>

<h3>💡 改进建议</h3>
<p>{recommendation}</p>

<h3>🔍 历史事故对比</h3>
""".format(recommendation=report.get('recommendation', 'N/A'))
        
        incidents = report.get('incident_comparison', {}).get('matched_incidents', [])
        if incidents:
            body += "<ul>\n"
            for incident in incidents:
                body += f"<li>{incident.get('description', 'N/A')}<br>"
                body += f"  <small>教训: {incident.get('lesson', 'N/A')}</small></li>\n"
            body += "</ul>\n"
        else:
            body += "<p>未检测到与历史事故相似的操作</p>\n"
        
        body += f"""
<hr>
<p style="color: gray; font-size: 12px;">
    生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    SOHH Security Assessment System v2.2.0
</p>
</body>
</html>
"""
        
        return subject, body
    
    def _send_email(self, subject: str, body: str):
        """发送邮件"""
        smtp_server = self.config['smtp_server']
        smtp_port = self.config['smtp_port']
        username = self.config['username']
        password = self.config['password']
        use_tls = self.config.get('use_tls', True)
        recipients = self.config['recipients']
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['From'] = username
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器并发送
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        server.login(username, password)
        server.sendmail(username, recipients, msg.as_string())
        server.quit()


def test_email_alert():
    """测试邮件告警"""
    alert_system = EmailAlertSystem()
    
    # 模拟一个高风险评估报告
    mock_report = {
        'safety_score': 25.5,
        'level_description': '较差 - 存在严重安全隐患',
        'total_commands': 10,
        'risky_commands': 5,
        'total_risks_detected': 8,
        'top_risks': [
            {'name': '数据库破坏', 'severity': 10},
            {'name': '文件删除', 'severity': 8},
            {'name': '网络风险', 'severity': 8}
        ],
        'recommendation': '🛑 发现严重安全隐患！禁止部署，需要重新设计Agent行为',
        'incident_comparison': {
            'matched_incidents': [
                {
                    'description': 'Claude AI 9秒删除公司数据库事件',
                    'lesson': '数据库删除操作必须有二次确认和备份验证'
                }
            ]
        }
    }
    
    print("="*70)
    print("📧 SOHH 邮件告警系统测试")
    print("="*70)
    print("\n正在发送测试邮件...")
    
    success = alert_system.send_alert(mock_report)
    
    if success:
        print("\n✅ 测试邮件发送成功！")
    else:
        print("\n⚠️ 未达到告警阈值或发送失败")
    
    print("="*70)


if __name__ == "__main__":
    test_email_alert()
