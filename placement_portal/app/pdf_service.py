from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

def generate_offer_letter_pdf(application):
    student=application.student; company=application.drive.company; drive=application.drive
    output=BytesIO(); styles=getSampleStyleSheet()
    title=ParagraphStyle("OfferTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=20,leading=24,textColor=colors.HexColor("#174ea6"),alignment=TA_CENTER,spaceAfter=10)
    portal=ParagraphStyle("Portal",parent=styles["Heading2"],fontSize=11,textColor=colors.HexColor("#4b5563"),alignment=TA_CENTER,spaceAfter=4)
    heading=ParagraphStyle("Section",parent=styles["Heading2"],fontSize=11,leading=14,textColor=colors.white,backColor=colors.HexColor("#174ea6"),borderPadding=5,spaceBefore=10,spaceAfter=7)
    body=ParagraphStyle("Body",parent=styles["BodyText"],fontSize=9.5,leading=14,alignment=TA_JUSTIFY,spaceAfter=7)
    doc=SimpleDocTemplate(output,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=16*mm,bottomMargin=18*mm,title=f"Offer Letter - {student.full_name}",author=company.company_name,pageCompression=0)

    def safe(value): return escape(str(value))
    def text(value): return safe(value) if value not in (None,"") else "To be communicated by the company"
    def date(value): return value.strftime("%d %B %Y") if value else "To be communicated by the company"
    def footer(canvas,document):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#d1d5db")); canvas.line(18*mm,14*mm,192*mm,14*mm); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#6b7280")); canvas.drawString(18*mm,9*mm,"PLACEMENT PORTAL · Academic Demonstration"); canvas.drawRightString(192*mm,9*mm,f"Page {document.page}"); canvas.restoreState()

    details=[["Company Name",company.company_name],["Position",drive.job_title],["Department / Role",drive.job_title],["Candidate Name",student.full_name],["Register Number",student.register_number],["Expected Joining Date","To be communicated by the company"],["Work Location","To be communicated by the company"],["Employment Type","To be communicated by the company"]]
    detail_table=Table(details,colWidths=[48*mm,118*mm],hAlign="LEFT")
    detail_table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#eef3fb")),("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#174ea6")),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#cbd5e1")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))

    candidate=f"<b>Date:</b> {date(__import__('datetime').datetime.now())}<br/><br/><b>To,</b><br/>{safe(student.full_name)}<br/>{safe(student.register_number)}<br/>{safe(student.user.email)}<br/>{text(student.phone)}"
    story=[Paragraph("PLACEMENT PORTAL",portal),Paragraph("OFFER LETTER",title),Paragraph(candidate,body),Spacer(1,3*mm),Paragraph(f"<b>Subject: Offer of Employment – {safe(drive.job_title)}</b>",body),Paragraph(f"Dear {safe(student.full_name)},",body),Paragraph(f"{safe(company.company_name)} is pleased to offer you the position of <b>{safe(drive.job_title)}</b>. Based on your participation in the placement process and successful completion of the recruitment process, we are pleased to offer you the opportunity to join {safe(company.company_name)}.",body),Paragraph("POSITION DETAILS",heading),detail_table]
    sections=[
        ("OFFER DETAILS",f"You successfully completed the placement selection process for this position. Your selection is subject to the terms and conditions communicated by {safe(company.company_name)}. Final compensation, joining date, and employment conditions are governed by the company's official policies and appointment documentation."),
        ("DRIVE INFORMATION",f"Placement drive date: {date(drive.drive_date)}<br/>Application date: {date(application.application_date)}<br/>Interview date: {date(application.interview_date)}<br/>Department eligibility: {text(drive.eligible_department)} · Minimum CGPA: {drive.minimum_cgpa} · Eligible year: {drive.eligible_year}"),
        ("RESPONSIBILITIES","Your responsibilities will include activities associated with the offered position and other reasonable duties assigned by the company according to organizational requirements."),
        ("JOINING INFORMATION","The company will communicate the final joining date, reporting location, onboarding instructions, and required documents separately."),
        ("DOCUMENTATION","You may be required to provide valid educational, identity, and other employment-related documents during onboarding."),
        ("TERMS AND CONDITIONS","This offer is generated through the Placement Portal Application for academic and demonstration purposes unless the company explicitly confirms it as an official employment offer. The company reserves the right to verify candidate information and apply its employment policies."),
    ]
    for section,content in sections: story.extend([Paragraph(section,heading),Paragraph(content,body)])
    story.extend([Spacer(1,3*mm),Paragraph("We congratulate you on your successful selection and wish you success in your professional career.",body),KeepTogether([Paragraph("Regards,",body),Paragraph(f"<b>{safe(company.hr_name)}</b><br/>{safe(company.hr_email)}<br/>{text(company.hr_phone)}<br/>{safe(company.company_name)}<br/>{text(company.website)}",body)])])
    doc.build(story,onFirstPage=footer,onLaterPages=footer); output.seek(0); return output
