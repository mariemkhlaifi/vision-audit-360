

from fpdf import FPDF
from datetime import datetime
import unicodedata
import re

def normalize_text(text: str) -> str:
    """Supprime les accents et caractères spéciaux"""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ASCII', 'ignore').decode('ASCII')
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

class AuditPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Vision-Audit 360 - Rapport d'Audit Qualite", ln=True, align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_audit_report(result: dict, constat_text: str) -> str:
    """Génère un rapport PDF professionnel"""
    pdf = AuditPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Nettoyage des textes
    constat_text_clean = normalize_text(constat_text)
    diagnostic_clean = normalize_text(result.get("diagnostic", "Non disponible"))
    recommandations_clean = normalize_text(result.get("recommandations", "Aucune recommandation supplementaire"))
    
    # Priorité sans emoji
    priorite_brute = result.get("priorite_action", "Non defini")
    priorite_clean = re.sub(r'[🔴🟠🟢]', '', priorite_brute).strip()
    
    # Titre du constat
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Constat terrain", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, constat_text_clean)
    pdf.ln(8)

    # Diagnostic
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Diagnostic de conformite", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, diagnostic_clean)
    pdf.ln(8)

    # Clauses ISO
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Clauses ISO 9001 concernees", ln=True)
    pdf.set_font("Helvetica", "", 11)
    clauses = result.get("clauses_concernees", [])
    if clauses:
        clauses_clean = [normalize_text(c) for c in clauses]
        pdf.multi_cell(0, 6, " - " + "\n - ".join(clauses_clean))
    else:
        pdf.cell(0, 6, "Aucune clause identifiee", ln=True)
    pdf.ln(8)

    # Niveau de risque
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Niveau de risque", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"-> {normalize_text(result.get('niveau_risque', 'Non defini'))}", ln=True)
    pdf.ln(8)

    # Score de conformité
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Score de conformite", ln=True)
    pdf.set_font("Helvetica", "", 11)
    score = result.get("conformite_score", 0)
    pdf.cell(0, 6, f"-> {score}%", ln=True)
    pdf.ln(5)

    # Priorité d'action
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Priorite d'action", ln=True)
    pdf.set_font("Helvetica", "", 11)
    delai = normalize_text(result.get("delai_recommandation", "Non defini"))
    pdf.cell(0, 6, f"-> {priorite_clean} (delai recommande : {delai})", ln=True)
    pdf.ln(8)

    # Actions correctives
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Actions correctives proposees", ln=True)
    pdf.set_font("Helvetica", "", 11)
    actions = result.get("actions_correctives", [])
    if actions:
        for i, action in enumerate(actions, 1):
            action_clean = normalize_text(action)
            pdf.multi_cell(0, 6, f"{i}. {action_clean}")
    else:
        pdf.cell(0, 6, "Aucune action corrective proposee", ln=True)
    pdf.ln(8)

    # Recommandations
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Recommandations supplementaires", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, recommandations_clean)
    
    # Sauvegarde
    filename = f"rapport_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
