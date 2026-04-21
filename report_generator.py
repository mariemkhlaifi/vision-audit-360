

import re
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)
from reportlab.platypus.flowables import KeepTogether


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_emojis(text: str) -> str:
    """Supprime les emojis et caractères non imprimables."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U00002500-\U00002BEF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\u2600-\u26FF"
        "\u2B50-\u2B55"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text).strip()


def _safe(text) -> str:
    """Garantit une chaîne propre (pas None, pas d'emojis)."""
    return _strip_emojis(str(text)) if text else ""


# ---------------------------------------------------------------------------
# Style sheet
# ---------------------------------------------------------------------------

def _build_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1a3c6e"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=base["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12,
        alignment=1,  # centre
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=base["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#1a3c6e"),
        borderPad=4,
        spaceBefore=14,
        spaceAfter=4,
        leading=16,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )

    item_style = ParagraphStyle(
        "ReportItem",
        parent=body_style,
        leftIndent=12,
        spaceAfter=3,
    )

    highlight_style = ParagraphStyle(
        "Highlight",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=11,
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_style,
        "body": body_style,
        "item": item_style,
        "highlight": highlight_style,
    }


# ---------------------------------------------------------------------------
# Score badge (table colorée)
# ---------------------------------------------------------------------------

def _score_badge(score: int, styles: dict):
    """Retourne un petit tableau coloré affichant le score de conformité."""
    if score >= 75:
        bg = colors.HexColor("#d4edda")
        fg = colors.HexColor("#155724")
        label = "Conforme"
    elif score >= 50:
        bg = colors.HexColor("#fff3cd")
        fg = colors.HexColor("#856404")
        label = "Partiellement conforme"
    else:
        bg = colors.HexColor("#f8d7da")
        fg = colors.HexColor("#721c24")
        label = "Non conforme"

    data = [[f"Score de conformité : {score}%", label]]
    tbl = Table(data, colWidths=[10 * cm, 6 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TEXTCOLOR", (0, 0), (-1, -1), fg),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def generate_audit_report(result: dict, constat_text: str, output_dir: str = ".") -> str:
    """
    Génère un rapport PDF professionnel Vision-Audit 360.

    Paramètres
    ----------
    result       : dict issu de l'analyse IA (diagnostic, score, actions…)
    constat_text : description textuelle du constat terrain
    output_dir   : dossier de sortie (défaut : répertoire courant)

    Retour
    ------
    Chemin absolu du fichier PDF généré.
    """
    # -- Préparation du chemin de sortie ------------------------------------
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filename = output_path / f"rapport_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # -- Initialisation du document -----------------------------------------
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="Vision-Audit 360 – Rapport d'Audit Qualité",
        author="Vision-Audit 360",
    )

    styles = _build_styles()
    story = []

    # -- En-tête du rapport -------------------------------------------------
    story.append(Paragraph("Vision-Audit 360", styles["title"]))
    story.append(Paragraph("Rapport d'Audit Qualité – ISO 9001", styles["title"]))
    story.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles["subtitle"],
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3c6e")))
    story.append(Spacer(1, 0.4 * cm))

    # -- Section 1 : Constat terrain ----------------------------------------
    story.append(Paragraph("1. Constat terrain", styles["section"]))
    story.append(Paragraph(_safe(constat_text) or "Aucun constat fourni.", styles["body"]))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 2 : Diagnostic ---------------------------------------------
    story.append(Paragraph("2. Diagnostic de conformité", styles["section"]))
    diagnostic = _safe(result.get("diagnostic", "Non disponible."))
    story.append(Paragraph(diagnostic, styles["body"]))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 3 : Clauses ISO 9001 ---------------------------------------
    story.append(Paragraph("3. Clauses ISO 9001 concernées", styles["section"]))
    clauses = result.get("clauses_concernees", [])
    if clauses:
        for clause in clauses:
            story.append(Paragraph(f"• {_safe(clause)}", styles["item"]))
    else:
        story.append(Paragraph("Aucune clause identifiée.", styles["body"]))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 4 : Niveau de risque ---------------------------------------
    story.append(Paragraph("4. Niveau de risque", styles["section"]))
    risque = _safe(result.get("niveau_risque", "Non défini"))
    story.append(Paragraph(f"→ {risque}", styles["highlight"]))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 5 : Score de conformité ------------------------------------
    story.append(Paragraph("5. Score de conformité", styles["section"]))
    score = result.get("conformite_score", 0)
    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0
    story.append(_score_badge(score, styles))
    story.append(Spacer(1, 0.4 * cm))

    # -- Section 6 : Priorité d'action --------------------------------------
    story.append(Paragraph("6. Priorité d'action", styles["section"]))
    priorite = _safe(result.get("priorite_action", "Non défini"))
    delai = _safe(result.get("delai_recommandation", "Non défini"))
    story.append(Paragraph(
        f"→ Priorité : <b>{priorite}</b> — Délai recommandé : <b>{delai}</b>",
        styles["body"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 7 : Actions correctives ------------------------------------
    story.append(Paragraph("7. Actions correctives proposées", styles["section"]))
    actions = result.get("actions_correctives", [])
    if actions:
        for i, action in enumerate(actions, 1):
            story.append(Paragraph(f"{i}. {_safe(action)}", styles["item"]))
    else:
        story.append(Paragraph("Aucune action corrective proposée.", styles["body"]))
    story.append(Spacer(1, 0.3 * cm))

    # -- Section 8 : Recommandations supplémentaires ------------------------
    story.append(Paragraph("8. Recommandations supplémentaires", styles["section"]))
    reco = _safe(result.get("recommandations", "Aucune recommandation supplémentaire."))
    story.append(Paragraph(reco, styles["body"]))

    # -- Pied de page (numéro de page via onPage) ---------------------------
    def _add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {page_num}")
        canvas.restoreState()

    # -- Génération ---------------------------------------------------------
    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)

    return str(filename.resolve())


# ---------------------------------------------------------------------------
# Test rapide (python report_generator.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_result = {
        "diagnostic": (
            "Le processus de contrôle qualité présente des lacunes importantes. "
            "Les enregistrements de mesure ne sont pas systématiquement archivés, "
            "ce qui compromet la traçabilité exigée par la norme."
        ),
        "clauses_concernees": [
            "7.1.5 – Ressources pour la surveillance et la mesure",
            "8.5.2 – Identification et traçabilité",
            "9.1.1 – Surveillance, mesure, analyse et évaluation",
        ],
        "niveau_risque": "Élevé 🔴",
        "conformite_score": 42,
        "priorite_action": "Urgente",
        "delai_recommandation": "Sous 30 jours",
        "actions_correctives": [
            "Mettre en place un registre numérique d'archivage des mesures.",
            "Former les opérateurs aux exigences de traçabilité ISO 9001.",
            "Réaliser un audit interne ciblé sur la clause 7.1.5 sous 15 jours.",
        ],
        "recommandations": (
            "Il est conseillé de réviser la procédure de contrôle qualité dans son ensemble "
            "et de planifier une revue de direction pour valider les corrections apportées."
        ),
    }

    constat = (
        "Lors de la visite du site de production, il a été constaté que les instruments "
        "de mesure (pieds à coulisse, micromètres) ne font pas l'objet d'un étalonnage "
        "documenté. Les opérateurs ne disposent pas de procédure écrite pour enregistrer "
        "les résultats de contrôle en cours de fabrication."
    )

    path = generate_audit_report(sample_result, constat, output_dir=".")
    print(f"✅ Rapport généré : {path}")