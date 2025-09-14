# emp_planning_system/report_generator.py

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

def _register_vietnamese_fonts():
    base_path = os.path.dirname(__file__)
    font_regular_path = os.path.join(base_path, "DejaVuSans.ttf")
    font_bold_path = os.path.join(base_path, "DejaVuSans-Bold.ttf")
    if os.path.exists(font_regular_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_regular_path))
    if os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))

def generate_report(filename, report_data):
    try:
        _register_vietnamese_fonts()
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Title_vi', parent=styles['Title'], fontName='DejaVuSans-Bold'))
        styles.add(ParagraphStyle(name='Heading1_vi', parent=styles['h1'], fontName='DejaVuSans-Bold'))
        styles.add(ParagraphStyle(name='Normal_vi', parent=styles['Normal'], fontName='DejaVuSans'))
        styles.add(ParagraphStyle(name='TableContent_vi', parent=styles['Normal'], fontName='DejaVuSans', alignment=1))

        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        story.append(Paragraph("BÁO CÁO QUY HOẠCH VÀ CẢNH BÁO NGUY HIỂM DO EMP", styles['Title_vi']))
        timestamp = datetime.now().strftime("%H:%M:%S Ngày %d-%m-%Y")
        story.append(Paragraph(f"<i>Báo cáo được tạo lúc: {timestamp}</i>", styles['Normal_vi']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Độ cao mặt cắt xét ảnh hưởng: {report_data.get('altitude', 'N/A')} m", styles['Normal_vi']))
        story.append(Spacer(1, 0.2 * inch))

        common_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        story.append(Paragraph("Danh sách các nguồn phát EMP", styles['Heading1_vi']))
        emp_headers = ['Tên', 'Vĩ độ', 'Kinh độ', 'Công suất (W)', 'Độ cao (m)']
        emp_table_data = [emp_headers]
        for emp in report_data.get('emps', []):
            emp_table_data.append([emp.name, f"{emp.lat:.6f}", f"{emp.lon:.6f}", emp.power, emp.height])
        emp_table = Table(emp_table_data)
        emp_table.setStyle(common_table_style)
        story.append(emp_table)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Danh sách các vật cản", styles['Heading1_vi']))
        obs_headers = ['Tên', 'Vĩ độ', 'Kinh độ', 'Dài (m)', 'Rộng (m)', 'Cao (m)']
        obs_table_data = [obs_headers]
        for obs in report_data.get('obstacles', []):
            obs_table_data.append([obs.name, f"{obs.lat:.6f}", f"{obs.lon:.6f}", obs.length, obs.width, obs.height])
        obs_table = Table(obs_table_data)
        obs_table.setStyle(common_table_style)
        story.append(obs_table)
        story.append(Spacer(1, 0.4 * inch))
        
        story.append(Paragraph("Minh họa vùng ảnh hưởng", styles['Heading1_vi']))
        image_path = report_data.get('image_path')
        if image_path and os.path.exists(image_path):
            img = Image(image_path)
            page_width, _ = letter
            scale = (page_width - 1.5 * inch) / img.imageWidth
            img.drawWidth, img.drawHeight = img.imageWidth * scale, img.imageHeight * scale
            story.append(img)
        else:
            story.append(Paragraph("<i>Không có hình ảnh vùng ảnh hưởng.</i>", styles['Normal_vi']))
            
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("Kiến nghị", styles['Heading1_vi']))
        story.append(Paragraph("Dựa trên kết quả mô phỏng, cần xem xét các biện pháp che chắn hoặc di dời các thiết bị nhạy cảm ra khỏi vùng có màu ĐỎ (nguy hiểm cao) và VÀNG (cảnh báo). Đảm bảo nhân sự không tiếp xúc lâu dài trong các khu vực này.", styles['Normal_vi']))

        doc.build(story)
        return True, f"Báo cáo đã được lưu thành công tại: {filename}"
    except Exception as e:
        return False, f"Tạo báo cáo thất bại: {e}"