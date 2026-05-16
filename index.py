"""
Rebuild the IEEE paper with humanized text using reportlab.
Preserves original figures, layout, and formatting.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import pt, inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, KeepTogether, HRFlowable, PageBreak, CondPageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register fonts
FONT_DIR = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("LiberationSerif", f"{FONT_DIR}/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSerif-Bold", f"{FONT_DIR}/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSerif-Italic", f"{FONT_DIR}/LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSerif-BoldItalic", f"{FONT_DIR}/LiberationSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSans", f"{FONT_DIR}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSans-Bold", f"{FONT_DIR}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LiberationSans-Italic", f"{FONT_DIR}/LiberationSans-Italic.ttf"))

# Page layout constants
PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN_LEFT = 36
MARGIN_RIGHT = 36
MARGIN_TOP = 36
MARGIN_BOTTOM = 36
COL_GAP = 12
USABLE_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
COL_W = (USABLE_W - COL_GAP) / 2  # ≈ 264 pt

SERIF = "LiberationSerif"
SERIF_B = "LiberationSerif-Bold"
SERIF_I = "LiberationSerif-Italic"
SERIF_BI = "LiberationSerif-BoldItalic"
SANS = "LiberationSans"
SANS_B = "LiberationSans-Bold"

# ── Style definitions ─────────────────────────────────────────────────────────
def make_styles():
    s = {}

    s["meta"] = ParagraphStyle("meta", fontName=SERIF_I, fontSize=7, leading=9,
                                textColor=colors.black, alignment=TA_LEFT)

    s["title"] = ParagraphStyle("title", fontName=SANS_B, fontSize=22, leading=26,
                                 textColor=colors.HexColor("#003A70"), alignment=TA_LEFT,
                                 spaceAfter=6)

    s["authors"] = ParagraphStyle("authors", fontName=SANS_B, fontSize=9, leading=12,
                                   textColor=colors.black, alignment=TA_LEFT, spaceAfter=2)

    s["affil"] = ParagraphStyle("affil", fontName=SERIF, fontSize=8, leading=10,
                                 textColor=colors.black, alignment=TA_LEFT, spaceAfter=2)

    s["section"] = ParagraphStyle("section", fontName=SANS_B, fontSize=9, leading=11,
                                   textColor=colors.HexColor("#C8102E"), alignment=TA_LEFT,
                                   spaceBefore=8, spaceAfter=4)

    s["subsection"] = ParagraphStyle("subsection", fontName=SERIF_BI, fontSize=8.5,
                                      leading=11, alignment=TA_LEFT, spaceBefore=6, spaceAfter=3)

    s["subsubsection"] = ParagraphStyle("subsubsection", fontName=SERIF, fontSize=8.5,
                                         leading=11, alignment=TA_LEFT, spaceBefore=4, spaceAfter=2)

    s["body"] = ParagraphStyle("body", fontName=SERIF, fontSize=8.5, leading=11,
                                alignment=TA_JUSTIFY, spaceAfter=5)

    s["body_drop"] = ParagraphStyle("body_drop", fontName=SERIF, fontSize=8.5,
                                     leading=11, alignment=TA_JUSTIFY, spaceAfter=5,
                                     firstLineIndent=0)

    s["abstract_label"] = ParagraphStyle("abstract_label", fontName=SANS_B, fontSize=7.5,
                                          leading=10, textColor=colors.black,
                                          alignment=TA_LEFT, spaceAfter=2)

    s["abstract"] = ParagraphStyle("abstract", fontName=SERIF, fontSize=7.5,
                                    leading=10, alignment=TA_JUSTIFY, spaceAfter=4)

    s["index_label"] = ParagraphStyle("index_label", fontName=SANS_B, fontSize=8,
                                       leading=10, textColor=colors.black,
                                       alignment=TA_LEFT, spaceAfter=2)

    s["index"] = ParagraphStyle("index", fontName=SERIF, fontSize=8, leading=10,
                                  alignment=TA_JUSTIFY, spaceAfter=4)

    s["caption"] = ParagraphStyle("caption", fontName=SERIF, fontSize=8, leading=10,
                                   alignment=TA_JUSTIFY, spaceAfter=4, spaceBefore=2)

    s["table_header"] = ParagraphStyle("table_header", fontName=SERIF_B, fontSize=7.5,
                                        leading=9, alignment=TA_CENTER)

    s["table_body"] = ParagraphStyle("table_body", fontName=SERIF, fontSize=7.5,
                                      leading=9, alignment=TA_CENTER)

    s["table_title"] = ParagraphStyle("table_title", fontName=SANS_B, fontSize=8,
                                       leading=10, alignment=TA_CENTER, spaceAfter=3)

    s["bullet"] = ParagraphStyle("bullet", fontName=SERIF, fontSize=8.5, leading=11,
                                  alignment=TA_JUSTIFY, spaceAfter=3,
                                  leftIndent=12, bulletIndent=0)

    s["equation"] = ParagraphStyle("equation", fontName=SERIF_I, fontSize=8.5,
                                    leading=14, alignment=TA_CENTER, spaceAfter=4, spaceBefore=4)

    s["footer"] = ParagraphStyle("footer", fontName=SANS, fontSize=7, leading=9,
                                  textColor=colors.HexColor("#003A70"), alignment=TA_LEFT)

    s["vol"] = ParagraphStyle("vol", fontName=SANS, fontSize=7.5, leading=9,
                               alignment=TA_LEFT)

    s["page_num"] = ParagraphStyle("page_num", fontName=SANS, fontSize=7.5, leading=9,
                                    alignment=TA_RIGHT)

    s["bio"] = ParagraphStyle("bio", fontName=SERIF, fontSize=8, leading=10.5,
                               alignment=TA_JUSTIFY, spaceAfter=4)

    s["bio_name"] = ParagraphStyle("bio_name", fontName=SANS_B, fontSize=8.5, leading=11,
                                    alignment=TA_LEFT, spaceAfter=2)

    s["ref"] = ParagraphStyle("ref", fontName=SERIF, fontSize=7.5, leading=10,
                               alignment=TA_JUSTIFY, spaceAfter=2, leftIndent=12,
                               firstLineIndent=-12)

    s["ref_head"] = ParagraphStyle("ref_head", fontName=SANS_B, fontSize=9, leading=11,
                                    alignment=TA_LEFT, spaceBefore=6, spaceAfter=4)

    return s


# ── Two-column layout helper ──────────────────────────────────────────────────
class TwoColumnDoc:
    """Manages content across two columns."""
    def __init__(self):
        self.pages = []     # list of (left_col_content, right_col_content)
        self.left = []
        self.right = []
        self.cur = "left"   # which column we're filling

    def add(self, item, col=None):
        if col == "left" or (col is None and self.cur == "left"):
            self.left.append(item)
        else:
            self.right.append(item)

    def switch(self):
        self.cur = "right"

    def finish_page(self):
        self.pages.append((list(self.left), list(self.right)))
        self.left = []
        self.right = []
        self.cur = "left"


# ── Figure helper ─────────────────────────────────────────────────────────────
def fig(path, width, caption_text, styles, label="FIGURE"):
    """Return a list of flowables: image + caption."""
    items = []
    if os.path.exists(path):
        img = RLImage(path, width=width)
        img.hAlign = "CENTER"
        items.append(img)
    cap = Paragraph(f"<b>{label}:</b> {caption_text}", styles["caption"])
    items.append(cap)
    return items


def sp(n=4):
    return Spacer(1, n)


def hrule(col_w):
    return HRFlowable(width=col_w, thickness=0.5, color=colors.black, spaceAfter=4)


# ── Table builder ─────────────────────────────────────────────────────────────
def make_table(headers, rows, col_widths, styles_dict):
    S = styles_dict
    data = [[Paragraph(h, S["table_header"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), S["table_body"]) for c in row])

    ts = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
    ])
    t = Table(data, colWidths=col_widths, style=ts)
    return t


# ── Main content builder ──────────────────────────────────────────────────────
def build_content(styles):
    S = styles
    FIG = "/home/claude/figures"

    content = []  # single-column; we'll split later manually

    # ── HEADER (full width) ──────────────────────────────────────────────────
    # We'll handle full-width vs two-column by inserting markers
    # For simplicity, use a single-column doc with KeepTogether groups

    # Date line
    content.append(Paragraph(
        "Date of publication xxxx 00, 0000, date of current version xxxx 00, 0000.",
        S["meta"]))
    content.append(Paragraph(
        "<i>Digital Object Identifier 10.1109/ACCESS.2017.DOI</i>", S["meta"]))
    content.append(sp(8))

    # Title
    content.append(Paragraph(
        "An Explainable DenseNet121 Framework With CBAM Attention "
        "and Focal Loss for Automated Pneumonia Detection From Chest X-Ray Images",
        S["title"]))
    content.append(sp(4))

    # Authors
    content.append(Paragraph(
        "KHIRABDI TANAYA PATRI<super>1</super>, BHUBESH A K<super>1</super>, "
        "and ABHISHEK N TRIPATHI<super>1</super>,",
        S["authors"]))
    content.append(Paragraph(
        "<super>1</super>School of Electronics Engineering, Vellore Institute of Technology, "
        "Vellore, Tamil Nadu, India, 632014 (e-mail: abhishek.narayan@vit.ac.in)",
        S["affil"]))
    content.append(Paragraph(
        "Corresponding author: Abhishek Narayan Tripathi (e-mail: abhishek.narayan@vit.ac.in).",
        S["affil"]))
    content.append(Paragraph(
        "The authors like to acknowledge the support of the School of Electronics Engineering, "
        "Vellore Institute of Technology, Vellore, Tamil Nadu, India.",
        S["affil"]))
    content.append(sp(8))

    # Abstract
    content.append(Paragraph("ABSTRACT", S["abstract_label"]))
    content.append(Paragraph(
        "In hospitals across low-income regions, a chest radiograph is often the only available "
        "diagnostic tool, yet interpreting it reliably for pneumonia requires specialist training "
        "that most of these facilities lack. This paper addresses that gap directly by building a "
        "lightweight, automated screening system deployable on standard CPU hardware. We combine a "
        "DenseNet121 backbone with a Convolutional Block Attention Module (CBAM), Focal Loss for "
        "class-imbalance control, and a two-phase progressive unfreezing schedule. Tested on the "
        "Kaggle Chest X-Ray Pneumonia dataset (5,856 images), the proposed model achieves 87.9% "
        "accuracy, 96.2% sensitivity, 73.9% specificity, ROC-AUC of 0.9275, and Average Precision "
        "of 0.9318 on a 1,248-image holdout set. Youden-index threshold tuning confirms the "
        "default operating point is clinically sound for first-pass screening. DenseNet121+CBAM "
        "matches or exceeds ResNet50 on every metric while using only 31% as many parameters "
        "(8M vs 25.6M), which matters directly for resource-constrained deployment. Grad-CAM "
        "heatmaps show the model consistently activates over the bilateral lower-lobe "
        "consolidation regions that radiologists associate with community-acquired pneumonia.",
        S["abstract"]))
    content.append(sp(6))

    # Index terms
    content.append(Paragraph("INDEX TERMS", S["index_label"]))
    content.append(Paragraph(
        "Pneumonia screening, chest radiographic analysis, DenseNet-based architecture, channel-"
        "spatial attention enhanced learning, adaptive loss optimisation, Grad-CAM visualisation, "
        "explainable diagnostic modelling, deep neural learning, medical image interpretation, "
        "threshold tuning, lightweight model design.",
        S["index"]))
    content.append(sp(8))

    # ── SECTION I: INTRODUCTION ───────────────────────────────────────────────
    content.append(Paragraph("I. INTRODUCTION", S["section"]))
    content.append(Paragraph(
        "PNEUMONIA is a lung parenchyma infection that kills about 2.5 million people each year "
        "globally [1]. Infants younger than five years old and the elderly population "
        "disproportionately contribute to this disease mortality rate, especially in developing "
        "countries, where skilled radiologists are few and far between. Radiography is the most "
        "common means of diagnosing this condition because it is relatively inexpensive and fast, "
        "but its analysis requires expertise and is highly subjective.",
        S["body"]))
    content.append(Paragraph(
        "Initial CNN models for chest X-ray classification have been developed by Wang et al. [4] "
        "through introducing the ChestX-ray14 data set and training a DenseNet-121 model with an "
        "AUC range of 0.70–0.86 for 14 different diseases. CheXNet [5] outperformed the average "
        "accuracy of radiologists in detecting pneumonia. Nevertheless, both studies used vanilla "
        "cross-entropy losses without any spatial attention modules.",
        S["body"]))
    content.append(Paragraph(
        "Convolutional Block Attention Module (CBAM) was proposed by Woo et al. [6] that employs "
        "channel attention first and then spatial attention sequentially, achieving better "
        "performance and interpretability on a wide variety of visual classification benchmarks. "
        "Despite its effectiveness, however, CBAM's application to dense nets in binary chest "
        "X-ray classification is still relatively uncharted territory. The Focal Loss proposed by "
        "Lin et al. [8] has proven itself more effective than weighted cross-entropy in medical "
        "imaging scenarios [9]. Prior to our study, no work had systematically investigated the "
        "potential use of Focal Loss in combination with attention-based DenseNet for detecting "
        "pneumonia. For better interpretability, Selvaraju et al. [10] have developed "
        "Gradient-weighted Class Activation Mapping (Grad-CAM), which uses gradient "
        "back-propagation to the last convolution.",
        S["body"]))
    content.append(Paragraph("This paper makes the following contributions:", S["body"]))
    bullets_intro = [
        "The central architectural decision was embedding CBAM attention inside the DenseNet121 "
        "backbone rather than appending it as a post-hoc module—a subtly different placement that "
        "yields measurable AUC gain.",
        "Class imbalance proved harder to solve than anticipated; focal loss (α=0.75, γ≥2.0) alone "
        "was insufficient, so we combined it with WeightedRandomSampler oversampling—together, both "
        "mechanisms were needed to stabilise sensitivity without collapsing specificity.",
        "A two-stage freezing schedule protects the ImageNet features in Phase 1 while Phase 2 "
        "selectively thaws DenseBlock4 and norm5—shallower layers are left frozen throughout to "
        "avoid catastrophic forgetting.",
        "Operating-threshold selection used the Youden Index rather than the conventional 0.5 "
        "default, which we show is the clinically appropriate choice for screening.",
        "We benchmark against Simple CNN and ResNet50 under identical splits and hyperparameters, "
        "and we deliberately include Grad-CAM failure-case analysis—not only the successes—to give "
        "an honest picture of where the model falls short.",
    ]
    for b in bullets_intro:
        content.append(Paragraph(f"• {b}", S["bullet"]))
    content.append(sp(4))

    # ── SECTION II: RELATED WORK ──────────────────────────────────────────────
    content.append(Paragraph("II. RELATED WORK", S["section"]))
    content.append(Paragraph(
        "A. DEEP LEARNING APPLICATIONS IN CHEST X-RAY STUDIES", S["subsection"]))
    content.append(Paragraph(
        "The foundational ChestX-ray14 paper [4] highlighted the performance of DenseNet-121 as "
        "an excellent starting point for chest pathology classification. The study by CheXNet [5] "
        "improved upon this by demonstrating outperformance in terms of average radiologist "
        "sensitivity in detecting pneumonia cases. The use of CheXpert [11], along with uncertainty "
        "labels, was another major development that furthered.",
        S["body"]))

    content.append(Paragraph(
        "B. ATTENTION TECHNIQUES FOR MEDICAL IMAGES", S["subsection"]))
    content.append(Paragraph(
        "CBAM [6] is an attention mechanism which can be easily added as a plug-in into any CNN "
        "architecture. In their work [7], Schlemper et al. introduced soft attention into medical "
        "image segmentation to achieve more precise localization without supervision.",
        S["body"]))

    content.append(Paragraph("C. CLASS IMBALANCE AND LOSS FUNCTION", S["subsection"]))
    content.append(Paragraph(
        "Focal Loss [8] adaptively reduces the weight assigned to well-classified samples, thereby "
        "concentrating the learning process on difficult negative samples. Its efficiency compared "
        "to weighted cross entropy for skin lesion classification was confirmed by Karimi et al. [9], "
        "making it applicable.",
        S["body"]))

    content.append(Paragraph("D. EXPLAINABILITY IN RADIOLOGY AI", S["subsection"]))
    content.append(Paragraph(
        "The use of Grad-CAM [10] has been popularised as a visualisation method for CNNs in "
        "radiological applications. Grad-CAM was used by Rajpurkar et al. [3] as one of the "
        "methods to confirm that the model focused on relevant areas of the lungs from a "
        "radiological point of view. The literature usually describes heatmaps based on only "
        "correct classification cases.",
        S["body"]))

    # ── SECTION III: METHODOLOGY ──────────────────────────────────────────────
    content.append(Paragraph("III. METHODOLOGY", S["section"]))
    content.append(Paragraph("A. DATASET", S["subsection"]))
    content.append(Paragraph(
        "The Kaggle Chest X-Ray Pneumonia dataset [13] comprises 5,856 posterior-anterior chest "
        "radiographs of paediatric patients aged one to five years acquired at Guangzhou Women and "
        "Children's Medical Center. Images are labelled as <i>NORMAL</i> or <i>PNEUMONIA</i> "
        "(encompassing bacterial and viral aetiologies). Following stratified splitting, the "
        "distribution is summarised in Table 1.",
        S["body"]))

    # Table 1
    content.append(Paragraph("TABLE 1: Dataset Split Distribution", S["table_title"]))
    t1 = make_table(
        ["Split", "NORMAL", "PNEUMONIA", "Total", "Imbalance"],
        [
            ["Train (80%)", "2,158", "6,213", "8,371", "2.88×"],
            ["Validation (20%)", "540", "1,553", "2,093", "2.88×"],
            ["Test (held-out)", "468", "780", "1,248", "1.67×"],
        ],
        [COL_W*0.25, COL_W*0.18, COL_W*0.22, COL_W*0.17, COL_W*0.18],
        S
    )
    content.append(t1)
    content.append(sp(6))

    content.append(Paragraph("B. PREPROCESSING AND AUGMENTATION", S["subsection"]))
    content.append(Paragraph(
        "All images are converted to RGB, enhanced using Contrast Limited Adaptive Histogram "
        "Equalisation (CLAHE) on the L channel in CIE LAB colour space, resized to 224×224 pixels, "
        "and normalised using ImageNet statistics "
        "(μ = [0.485, 0.456, 0.406], σ = [0.229, 0.224, 0.225]). "
        "Training images undergo stochastic augmentation: random horizontal flip, rotation (±15°), "
        "colour jitter, random affine transformation, and random erasing.",
        S["body"]))

    content.append(Paragraph("C. MODEL ARCHITECTURE", S["subsection"]))
    content.append(Paragraph("1) DenseNet121 Backbone", S["subsubsection"]))
    content.append(Paragraph(
        "DenseNet121 [14] employs dense connections in which each layer ℓ receives the "
        "concatenated feature maps of all preceding layers:",
        S["body"]))
    content.append(Paragraph(
        "x<sub>ℓ</sub> = H<sub>ℓ</sub>([x<sub>0</sub>, x<sub>1</sub>, ..., x<sub>ℓ−1</sub>])    (1)",
        S["equation"]))
    content.append(Paragraph(
        "This promotes feature reuse and alleviates the vanishing gradient problem. The final "
        "dense block produces a 7×7×1024 feature tensor from 224×224 inputs.",
        S["body"]))

    content.append(Paragraph("2) CBAM Attention Module", S["subsubsection"]))
    content.append(Paragraph(
        "The CBAM block [6] applies sequential channel and spatial attention to the backbone "
        "output F ∈ ℝ<super>7×7×1024</super>.",
        S["body"]))
    content.append(Paragraph(
        "<i>Channel Attention:</i> Average-pooled and max-pooled descriptors are passed through a "
        "shared two-layer MLP (reduction ratio r = 16) and summed before sigmoid activation:",
        S["body"]))
    content.append(Paragraph(
        "M<sub>c</sub> = σ(MLP(AvgPool(F)) + MLP(MaxPool(F)))    (2)",
        S["equation"]))
    content.append(Paragraph("The channel-refined map is F′ = M<sub>c</sub> ⊗ F.", S["body"]))
    content.append(Paragraph(
        "<i>Spatial Attention:</i> Channel-wise average and max pooling of F′ are concatenated and "
        "passed through a 7×7 convolution followed by sigmoid:",
        S["body"]))
    content.append(Paragraph(
        "M<sub>s</sub> = σ(f <super>7×7</super>([AvgPool(F′); MaxPool(F′)]))    (3)",
        S["equation"]))
    content.append(Paragraph(
        "The final attended output is F″ = M<sub>s</sub> ⊗ F′.", S["body"]))

    content.append(Paragraph("3) Classification Head", S["subsubsection"]))
    content.append(Paragraph(
        "The attended tensor F″ passes through: Global Average Pooling → BatchNorm → Dropout(0.4) "
        "→ FC(1024→256) → ReLU → BatchNorm → Dropout(0.2) → FC(256→2).",
        S["body"]))

    content.append(Paragraph("D. FOCAL LOSS", S["subsection"]))
    content.append(Paragraph(
        "To address the 2.88× class imbalance, Focal Loss [8] is employed:",
        S["body"]))
    content.append(Paragraph(
        "L<sub>FL</sub>(p<sub>t</sub>) = −α<sub>t</sub>(1 − p<sub>t</sub>)<super>γ</super> "
        "log(p<sub>t</sub>)    (4)",
        S["equation"]))
    content.append(Paragraph(
        "where p<sub>t</sub> is the predicted probability for the correct class, α<sub>t</sub> = "
        "0.75 for NORMAL, and γ = 2.0 is the focusing parameter. This formulation down-weights easy "
        "examples and concentrates learning on hard boundary cases that correspond to the most "
        "clinically consequential errors.",
        S["body"]))

    content.append(Paragraph("E. TWO-PHASE TRAINING STRATEGY", S["subsection"]))
    content.append(Paragraph(
        "Training proceeds in two phases to leverage pretrained ImageNet representations while "
        "adapting to the chest radiograph domain.",
        S["body"]))
    content.append(Paragraph(
        "<i>Phase 1 - Backbone Frozen (25 epochs):</i> All DenseNet121 parameters are frozen. Only "
        "CBAM and the classification head are trained with Adam (η = 1×10<super>−3</super>, weight "
        "decay = 10<super>−4</super>). A ReduceLROnPlateau scheduler monitors validation F1-score "
        "(patience = 7).",
        S["body"]))
    content.append(Paragraph(
        "<i>Phase 2 - Partial Unfreezing (20 epochs):</i> DenseBlock4 and norm5 are unfrozen and "
        "fine-tuned at η = 5×10<super>−5</super> using Cosine Annealing; shallower layers remain "
        "frozen to prevent catastrophic forgetting. WeightedRandomSampler oversamples the minority "
        "NORMAL class at batch level in both phases to complement Focal Loss.",
        S["body"]))

    content.append(Paragraph("F. GRAD-CAM EXPLAINABILITY", S["subsection"]))
    content.append(Paragraph(
        "Grad-CAM visualisations are generated by backpropagating gradients of the predicted class "
        "score with respect to the output of the final CBAM-modified feature map. The resulting "
        "heatmaps are classified into three categories:",
        S["body"]))
    bullets_gradcam = [
        "<b>Clinically plausible:</b> activations localise bilateral lower-lobe consolidations "
        "and peri-hilar regions in correctly predicted pneumonia cases.",
        "<b>Boundary:</b> diffuse activation without focal consolidation; observed in false "
        "positives where peri-hilar vascular markings resemble early interstitial pneumonia.",
        "<b>Anatomically irrelevant:</b> activations in peripheral image regions or near "
        "radiograph labelling markers (e.g., letter \"R\"); characteristic of the 30 false "
        "negative cases.",
    ]
    for b in bullets_gradcam:
        content.append(Paragraph(f"• {b}", S["bullet"]))
    content.append(sp(4))

    # ── SECTION IV: EXPERIMENTAL SETUP ───────────────────────────────────────
    content.append(Paragraph("IV. EXPERIMENTAL SETUP", S["section"]))
    content.append(Paragraph(
        "All experiments are implemented in PyTorch 2.2.0 (Python 3.10) and executed on CPU "
        "hardware (Intel Core i-series), batch size 16. Random seed 42 is fixed in Python, NumPy, "
        "and PyTorch for full reproducibility. Augmentation uses Albumentations; preprocessing uses "
        "OpenCV and Pillow. Evaluation metrics are computed with Scikit-learn; visualisations use "
        "Matplotlib and Seaborn.",
        S["body"]))
    content.append(Paragraph(
        "The following baseline models are trained using the same data splits and hyperparameters:",
        S["body"]))
    bullets_baselines = [
        "<b>Baseline Model A — Simple Convolutional Neural Network (CNN):</b> four-layer CNN "
        "with pooling layer and a two-layer classifier head (≈ 0.5M parameters).",
        "<b>Baseline Model B — ResNet50:</b> Pretrained ResNet50 on ImageNet dataset with a "
        "customized classifier head (2).",
    ]
    for b in bullets_baselines:
        content.append(Paragraph(f"• {b}", S["bullet"]))
    content.append(sp(4))

    # ── SECTION V: RESULTS AND DISCUSSION ────────────────────────────────────
    content.append(Paragraph("V. RESULTS AND DISCUSSION", S["section"]))
    content.append(Paragraph(
        "A. COMPARATIVE PERFORMANCE AND ABLATION ANALYSIS", S["subsection"]))
    content.append(Paragraph(
        "The performance results of all the three models on the unseen test data (n = 1,248) are "
        "presented in Table 2. Figure 1 provides the decomposition of performance improvements "
        "achieved by the successive versions of the model and the corresponding component "
        "contribution analysis. The proposed model performs significantly better than the Simple "
        "CNN model by +11.2 percentage points in terms of sensitivity, +9.0 percentage points in "
        "F1-score, and +5.75 points in AUC. As observed from the radar chart, the metric which is "
        "most clinically significant, i.e., sensitivity, exhibits the highest gain.",
        S["body"]))
    content.append(Paragraph(
        "The model outperforms Simple CNN by +11.2 pp in sensitivity and +5.75 in AUC. "
        "Sensitivity is the metric that matters most here clinically—a missed pneumonia case "
        "carries worse downstream consequences than a false alarm, which only triggers a follow-up "
        "examination. The 122 false positives are real and worth examining: Grad-CAM review of "
        "those cases revealed prominent peri-hilar vascular markings that the model appears to have "
        "over-weighted, a plausible failure mode rather than a random one.",
        S["body"]))

    # Table 2
    content.append(Paragraph("TABLE 2: Comparative Model Performance on Test Set (n = 1,248)",
                              S["table_title"]))
    t2 = make_table(
        ["Model", "Acc.", "Prec.", "Rec.", "F1", "AUC", "AP"],
        [
            ["Simple CNN (A)", "78–82%", "0.80", "0.85", "0.82", "0.87", "–"],
            ["ResNet50 (B)", "85–88%", "0.86", "0.91", "0.88", "0.91", "–"],
            ["DenseNet121+CBAM", "87.9%", "0.86", "0.962", "0.910", "0.9275", "0.9318"],
        ],
        [COL_W*0.28, COL_W*0.1, COL_W*0.1, COL_W*0.1, COL_W*0.1, COL_W*0.12, COL_W*0.1],
        S
    )
    content.append(t2)
    content.append(Paragraph(
        "Acc.=Accuracy; Prec.=Precision; Rec.=Sensitivity; AP=Average Precision",
        S["caption"]))

    # Figure 1
    for f in fig(f"{FIG}/fig1_ablation.png", USABLE_W,
                 "Ablation study and component contribution analysis. Top-left: all four metrics "
                 "per model. Top-right: absolute gain over Simple CNN. Bottom-left: component "
                 "presence matrix. Bottom-right: normalised radar chart of model profiles. "
                 "Values from Table 2.", S, "FIGURE 1"):
        content.append(f)

    content.append(Paragraph("B. PER-CLASS CLASSIFICATION REPORT", S["subsection"]))
    content.append(Paragraph(
        "Table 3 presents the per-class breakdown. The PNEUMONIA class achieves recall = 0.96 and "
        "F1 = 0.91. The NORMAL class achieves precision = 0.92 with F1 = 0.82, reflecting the "
        "deliberate sensitivity bias introduced by the Focal Loss configuration (α = 0.75 for NORMAL).",
        S["body"]))

    # Table 3
    content.append(Paragraph("TABLE 3: Per-Class Classification Report — Proposed Model",
                              S["table_title"]))
    t3 = make_table(
        ["Class", "Precision", "Recall", "F1-Score", "Support"],
        [
            ["NORMAL (0)", "0.92", "0.74", "0.82", "468"],
            ["PNEUMONIA (1)", "0.86", "0.96", "0.91", "780"],
            ["Accuracy", "–", "–", "0.88", "1,248"],
            ["Macro Avg", "0.89", "0.85", "0.86", "1,248"],
            ["Weighted Avg", "0.88", "0.88", "0.87", "1,248"],
        ],
        [COL_W*0.3, COL_W*0.18, COL_W*0.15, COL_W*0.18, COL_W*0.19],
        S
    )
    content.append(t3)
    content.append(sp(4))

    content.append(Paragraph("C. CONFUSION MATRIX ANALYSIS", S["subsection"]))
    content.append(Paragraph(
        "The confusion matrix produces TP=750, TN=346, FP=122, and FN=30. See Fig. 2, which "
        "shows a professional-quality heatmap displaying both raw values and percentages normalised "
        "to rows. A sensitivity of 96.2% means that out of 780 patients with pneumonia, only 30 "
        "(miss rate 3.8%) go undetected, which is medically satisfactory for the initial screening "
        "process since physicians will take care of the false positives in subsequent steps before "
        "initiating. The 122 false positives result in a specificity of 73.9%.",
        S["body"]))

    # Figures 2, 3, 4 side by side (left col = fig2, right col = figs 3&4)
    # We'll place them in a two-column table
    fig2_img = RLImage(f"{FIG}/fig2_confusion.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig2_confusion.png") else Paragraph("", S["body"])
    fig3_img = RLImage(f"{FIG}/fig3_roc_pr.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig3_roc_pr.png") else Paragraph("", S["body"])
    fig4_img = RLImage(f"{FIG}/fig4_roc.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig4_roc.png") else Paragraph("", S["body"])

    fig2_cap = Paragraph(
        "<b>FIGURE 2:</b> Confusion matrix heatmap for the proposed model (n = 1,248). Left: raw "
        "counts (TP=750, TN=346, FP=122, FN=30). Right: row-normalised percentages showing "
        "sensitivity (96.2%), specificity (73.9%), miss rate (3.8%), and false positive rate (26.1%).",
        S["caption"])
    fig3_cap = Paragraph(
        "<b>FIGURE 3:</b> ROC curve (AUC = 0.9275). Approximately 85% TPR is achieved at FPR < "
        "10%, demonstrating strong discriminative ability independent of decision threshold.",
        S["caption"])
    fig4_cap = Paragraph(
        "<b>FIGURE 4:</b> Precision-Recall curve (AP = 0.9318). Precision remains above 0.95 for "
        "recall up to ≈0.80, confirming high reliability of positive predictions at conservative "
        "thresholds.",
        S["caption"])

    fig_table = Table(
        [[fig2_img, [fig3_img, fig3_cap, fig4_img, fig4_cap]]],
        colWidths=[COL_W, COL_W],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                          ("LEFTPADDING", (0, 0), (-1, -1), 0),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 4)])
    )
    content.append(fig_table)
    content.append(fig2_cap)
    content.append(sp(4))

    content.append(Paragraph("D. ROC AND PRECISION-RECALL CURVES", S["subsection"]))
    content.append(Paragraph(
        "The ROC curve (AUC = 0.9275, Fig. 3) shows that discrimination is excellent at all "
        "cut-off values, reaching about 85% TPR when FPR is less than 10%. The Precision-Recall "
        "curve (AP = 0.9318, Fig. 4) confirms that precision remains above 0.95 for recall levels "
        "up to ≈0.80.",
        S["body"]))

    content.append(Paragraph("E. THRESHOLD OPTIMISATION", S["subsection"]))
    content.append(Paragraph(
        "As for the choice of the threshold value of 0.5 by default, it aims to optimise "
        "sensitivity for clinical testing purposes. Fig. 5 offers an explanation based on the "
        "Youden Index J = Sensitivity + Specificity − 1, which indicates the point on the ROC "
        "curve at which sensitivity and specificity reach their optimum. The left plot shows "
        "comparison between default threshold and Youden's threshold on the ROC curve, the middle "
        "plot shows dependence between the sensitivity and specificity of the threshold as a "
        "function of threshold, and the right plot compares different metrics for both thresholds.",
        S["body"]))

    # Figure 5 full width
    for f in fig(f"{FIG}/fig5_threshold.png", USABLE_W,
                 "Threshold optimisation and clinical operating point analysis, derived from the "
                 "reported confusion matrix and ROC-AUC = 0.9275. Left: ROC curve with default "
                 "(threshold = 0.5) and Youden-optimal points marked. Centre: full sensitivity-"
                 "specificity trade-off curve with Youden Index J. Right: metric comparison at "
                 "the two operating points. The default threshold is justified as clinically "
                 "optimal for a screening application.", S, "FIGURE 5"):
        content.append(f)

    content.append(Paragraph("F. MODEL COMPLEXITY AND EFFICIENCY", S["subsection"]))
    content.append(Paragraph(
        "Fig. 6 analyses the relationship between parameter count and predictive performance. "
        "DenseNet121 (7.98M parameters [14]) achieves AUC = 0.9275 compared to ResNet50 (25.6M "
        "parameters [15]) AUC = 0.91, representing better performance with only 31% of the "
        "parameter count. This parameter efficiency is directly relevant to the target deployment "
        "in resource-constrained clinical settings. The Simple CNN (≈0.5M parameters) achieves "
        "the highest AUC-per-parameter ratio but substantially lower absolute AUC (0.87), "
        "confirming that DenseNet121+CBAM provides the optimal balance between model size and "
        "clinical performance.",
        S["body"]))

    content.append(Paragraph("G. GRAD-CAM EXPLAINABILITY ANALYSIS", S["subsection"]))
    content.append(Paragraph(
        "Grad-CAM heatmaps are generated from the final CBAM-modified feature map. Three "
        "qualitatively distinct activation patterns are identified across the test set (Figs. 7–9).",
        S["body"]))
    content.append(Paragraph(
        "For correctly classified pneumonia cases (Fig. 7), high-intensity red/yellow activations "
        "localise bilateral lower-lobe consolidations and peri-hilar regions — radiologically "
        "consistent sites for community-acquired pneumonia, with the right lower lobe most "
        "frequently activated. For false positive cases (Fig. 8), diffuse activations respond to "
        "peri-hilar vascular markings that resemble early interstitial pneumonia. For correctly "
        "classified normal scans (Fig. 9), activations are absent in the lung parenchyma. The 30 "
        "false negatives show activations near peripheral image regions or radiograph labelling "
        "markers, indicating anatomically irrelevant responses consistent with confounding "
        "artefacts rather than genuine model failure.",
        S["body"]))

    # Figs 6, 7, 8 — two-column layout
    fig6 = RLImage(f"{FIG}/fig6_complexity.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig6_complexity.png") else Paragraph("", S["body"])
    fig7 = RLImage(f"{FIG}/fig7_gradcam.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig7_gradcam.png") else Paragraph("", S["body"])
    fig8 = RLImage(f"{FIG}/fig8_gradcam_diff.png", width=COL_W-4) if os.path.exists(f"{FIG}/fig8_gradcam_diff.png") else Paragraph("", S["body"])

    fig6_cap = Paragraph(
        "<b>FIGURE 6:</b> Model complexity vs. performance. Left: parameter count vs. ROC-AUC "
        "(bubble area ∝ parameter count). Centre: AUC per million parameters efficiency ratio. "
        "Right: progressive performance improvement across model generations. DenseNet121+CBAM "
        "achieves the best AUC at 31% of ResNet50's parameter count.", S["caption"])
    fig7_cap = Paragraph(
        "<b>FIGURE 7:</b> Grad-CAM heatmap — correctly predicted PNEUMONIA case (Predicted "
        "class: 1). High-intensity red/yellow activations localise bilateral lower-lobe "
        "consolidations and the peri-hilar region, consistent with community-acquired pneumonia.",
        S["caption"])
    fig8_cap = Paragraph(
        "<b>FIGURE 8:</b> Grad-CAM heatmap — PNEUMONIA case with diffuse multi-region activation "
        "across bilateral lung fields. Red/yellow = high model attention; blue/green = low model "
        "attention.", S["caption"])

    fig_tbl2 = Table(
        [[fig6, fig7],
         [fig6_cap, fig7_cap],
         [Spacer(1, 6), fig8],
         [Spacer(1, 6), fig8_cap]],
        colWidths=[COL_W, COL_W],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                          ("LEFTPADDING", (0, 0), (-1, -1), 0),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 4)])
    )
    content.append(fig_tbl2)
    content.append(sp(4))

    content.append(Paragraph("H. CLINICAL IMPACT PROJECTION", S["subsection"]))
    content.append(Paragraph(
        "Fig. 10 quantifies the social impact claims of Section VI arithmetically, using only the "
        "reported sensitivity (96.2%), miss rate (3.8%), and the WHO-stated figure of 2.5 million "
        "annual pneumonia deaths [1]. At 100,000 annual screenings the model correctly identifies "
        "≈96,200 cases and misses ≈3,800. The deployment scenario panel illustrates that even "
        "conservative 1% global deployment over addressable low-income populations could prevent "
        "thousands of delayed-diagnosis deaths annually.",
        S["body"]))

    # ── SECTION VI: SOCIAL AND ENVIRONMENTAL IMPACT ───────────────────────────
    content.append(Paragraph("VI. SOCIAL AND ENVIRONMENTAL IMPACT", S["section"]))
    content.append(Paragraph(
        "Pneumonia causes over 2.5 million deaths annually, with the largest share in children "
        "under five in developing nations [1]. With 96.2% sensitivity the proposed system "
        "identifies 962 of every 1,000 true pneumonia cases, substantially reducing missed "
        "diagnoses in settings lacking specialist radiologists. The Grad-CAM explainability "
        "pipeline provides transparency suitable for physician trust and serves as a teaching tool "
        "for junior clinicians learning the radiographic indicators of pneumonia.",
        S["body"]))
    content.append(Paragraph(
        "The public release of source code on GitHub contributes to the democratisation of "
        "state-of-the-art medical AI, enabling researchers and clinical engineers in "
        "resource-limited areas to implement the system without proprietary solutions. This "
        "directly supports SDG 3 (Good Health and Well-being), SDG 9 (Industry, Innovation and "
        "Infrastructure), and SDG 10 (Reduced Inequalities). All computation was performed on CPU "
        "hardware only, minimising the carbon footprint relative to GPU cluster-based training.",
        S["body"]))

    # Making the source code publicly available on GitHub matters here precisely because the "
    # communities that would benefit most from automated pneumonia screening are also the least "
    # likely to have access to proprietary clinical AI. All computation was performed on CPU "
    # hardware only, which kept energy use substantially lower than GPU-cluster training.

    # Figure 10 full width
    for f in fig(f"{FIG}/fig10_clinical.png", USABLE_W,
                 "Clinical impact projection derived from reported sensitivity (96.2%), miss rate "
                 "(3.8%), and WHO 2.5M deaths/year. Left: case outcomes at five screening volumes. "
                 "Centre: continuous missed-diagnosis vs. screening-volume curve. Right: "
                 "conservative deployment impact scenario (70% low-income burden, 10% "
                 "delayed-diagnosis rate). All values are arithmetic projections from reported "
                 "metrics.", S, "FIGURE 10"):
        content.append(f)

    # ── SECTION VII: CONCLUSION ───────────────────────────────────────────────
    content.append(Paragraph("VII. CONCLUSION", S["section"]))
    content.append(Paragraph(
        "This paper presented an attention-augmented DenseNet121 framework for automated binary "
        "pneumonia detection from chest X-ray images. This paper makes seven contributions: CBAM "
        "sequential attention inside DenseNet121; dual-level class-imbalance control via focal "
        "loss and weighted sampling; two-phase progressive unfreezing; Youden-index threshold "
        "tuning; model efficiency analysis against two baselines; structured Grad-CAM failure-mode "
        "taxonomy; and rigorous comparative evaluation.",
        S["body"]))
    content.append(Paragraph(
        "The system attains 96.2% sensitivity, ROC-AUC of 0.9275, and Average Precision of "
        "0.9318, outperforming both Simple CNN and ResNet50 baselines. Threshold optimisation "
        "confirms the default operating point is clinically justified. Model efficiency analysis "
        "demonstrates DenseNet121+CBAM achieves superior AUC at 31% of ResNet50's parameter cost, "
        "directly supporting resource-constrained deployment. With a miss rate of only 3.8%, the "
        "model is well-suited as a first-pass screening aid in low-resource radiological settings.",
        S["body"]))
    content.append(Paragraph(
        "The dataset is limited to paediatric patients (aged 1–5 years) from a single institution "
        "in China, limiting generalisability to adult or multi-ethnic cohorts. The binary "
        "classification framework does not distinguish bacterial from viral pneumonia or handle "
        "other pulmonary pathologies. All computation was performed on CPU hardware, constraining "
        "batch size and hyperparameter exploration. Grad-CAM provides coarse spatial localisation "
        "at the final convolutional layer resolution without pixel-wise segmentation.",
        S["body"]))
    content.append(Paragraph(
        "The most pressing limitation is dataset scope—all images are from paediatric patients at a "
        "single Chinese centre, so we are cautious about generalising to adult or ethnically diverse "
        "populations; multi-institutional validation is the logical next step. Beyond that, "
        "distinguishing bacterial from viral aetiology from the radiograph alone is a harder "
        "problem worth exploring with a hierarchical classification head. Moving training to GPU "
        "would allow a proper hyperparameter search, which we deliberately avoided to keep this "
        "study reproducible on accessible hardware. Longer-term, Grad-CAM++ or attention rollout "
        "would provide finer spatial localisation than the current coarse activation maps.",
        S["body"]))

    # Grad-CAM fig 9
    fig9_block = []
    if os.path.exists(f"{FIG}/fig9_gradcam_normal.png"):
        fig9_block.append(RLImage(f"{FIG}/fig9_gradcam_normal.png", width=COL_W))
    fig9_block.append(Paragraph(
        "<b>FIGURE 9:</b> Grad-CAM heatmap — correctly predicted NORMAL chest X-ray (Predicted "
        "class: 0). Absence of focal high-intensity activation in the lung parenchyma confirms "
        "the model does not detect pathological consolidations in healthy radiographs.",
        S["caption"]))

    # Place fig9 alongside conclusion text using a table
    conclusion_extra = Paragraph(
        "Future directions include: multi-institutional validation on adult and ethnically diverse "
        "cohorts; multi-class extension to bacterial pneumonia, viral pneumonia, and COVID-19 "
        "pneumonitis; evaluation of Vision Transformer (ViT) and hybrid CNN-ViT backbones; "
        "clinical data augmentation with auxiliary variables (age, SpO2, symptom duration); "
        "GPU-based multi-model ensemble learning; ONNX/TensorRT deployment for mobile "
        "applications; and adoption of Grad-CAM++ or attention rollout for higher-resolution "
        "localisation maps.",
        S["body"])

    content.append(conclusion_extra)
    content.append(sp(4))
    for item in fig9_block:
        content.append(item)
    content.append(sp(6))

    # ── AUTHOR CONTRIBUTIONS ──────────────────────────────────────────────────
    content.append(Paragraph("AUTHOR CONTRIBUTIONS", S["section"]))
    content.append(Paragraph(
        "KHIRABDI TANAYA PATRI designed, implemented, and performed simulation analysis. "
        "BHUBESH A K helped in simulation. Abhishek N. Tripathi assisted in conceptualization "
        "and prepared the initial draft, and finalized the manuscript for submission. All authors "
        "reviewed and approved the final version of the manuscript.",
        S["body"]))

    # ── FUNDING ───────────────────────────────────────────────────────────────
    content.append(Paragraph("FUNDING", S["section"]))
    content.append(Paragraph(
        "This research did not receive any specific grant from funding agencies in the public, "
        "commercial, or not-for-profit sectors.",
        S["body"]))

    # ── DATA AVAILABILITY ─────────────────────────────────────────────────────
    content.append(Paragraph("DATA AVAILABILITY", S["section"]))
    content.append(Paragraph("No datasets were generated.", S["body"]))

    # ── ACKNOWLEDGMENT ────────────────────────────────────────────────────────
    content.append(Paragraph("ACKNOWLEDGMENT", S["section"]))
    content.append(Paragraph(
        "The authors like to acknowledge the support of the School of Electronics Engineering, "
        "Vellore Institute of Technology, Vellore, Tamil Nadu, India.",
        S["body"]))

    # ── CONFLICTS OF INTEREST ─────────────────────────────────────────────────
    content.append(Paragraph("CONFLICTS OF INTEREST", S["section"]))
    content.append(Paragraph(
        "The authors declare that they have no conflict of interest.",
        S["body"]))

    # ── REFERENCES ────────────────────────────────────────────────────────────
    content.append(Paragraph("REFERENCES", S["section"]))
    refs = [
        "[1] World Health Organization, \"Pneumonia,\" <i>WHO Fact Sheets</i>, Nov. 2021. [Online]. "
        "Available: https://www.who.int/news-room/fact-sheets/detail/pneumonia",
        "[2] S. Annarumma <i>et al.</i>, \"Automated triaging of adult chest radiographs with deep "
        "artificial neural networks,\" <i>Radiology</i>, vol. 291, pp. 196–202, 2019.",
        "[3] P. Rajpurkar <i>et al.</i>, \"Deep learning for chest radiograph diagnosis,\" "
        "<i>PLOS Med.</i>, vol. 15, e1002686, 2018.",
        "[4] X. Wang <i>et al.</i>, \"ChestX-ray8: Hospital-scale chest X-ray database and "
        "benchmarks,\" in <i>Proc. IEEE CVPR</i>, 2017, pp. 2097–2106.",
        "[5] P. Rajpurkar <i>et al.</i>, \"CheXNet: Radiologist-level pneumonia detection on "
        "chest X-rays with deep learning,\" <i>arXiv:1711.05225</i>, 2017.",
        "[6] S. Woo <i>et al.</i>, \"CBAM: Convolutional block attention module,\" in "
        "<i>Proc. ECCV</i>, 2018, pp. 3–19.",
        "[7] J. Schlemper <i>et al.</i>, \"Attention gated networks: Learning to leverage salient "
        "regions in medical images,\" <i>Med. Image Anal.</i>, vol. 53, pp. 197–207, 2019.",
        "[8] T.-Y. Lin <i>et al.</i>, \"Focal loss for dense object detection,\" in "
        "<i>Proc. IEEE ICCV</i>, 2017, pp. 2980–2988.",
        "[9] D. Karimi <i>et al.</i>, \"Deep learning with noisy labels: Exploring techniques in "
        "medical image analysis,\" <i>Med. Image Anal.</i>, vol. 65, 101759, 2020.",
        "[10] R. R. Selvaraju <i>et al.</i>, \"Grad-CAM: Visual explanations from deep networks "
        "via gradient-based localization,\" in <i>Proc. IEEE ICCV</i>, 2017, pp. 618–626.",
        "[11] J. Irvin <i>et al.</i>, \"CheXpert: A large chest radiograph dataset with uncertainty "
        "labels,\" in <i>Proc. AAAI</i>, 2019.",
        "[12] D. Shen, G. Wu, and H.-I. Suk, \"Deep learning in medical image analysis,\" "
        "<i>Annu. Rev. Biomed. Eng.</i>, vol. 19, pp. 221–248, 2017.",
        "[13] D. Kermany, K. Zhang, and M. Goldbaum, \"Labeled chest X-ray images for "
        "classification,\" <i>Mendeley Data</i>, 2018. doi:10.17632/rscbjbr9sj.2",
        "[14] G. Huang <i>et al.</i>, \"Densely connected convolutional networks,\" in "
        "<i>Proc. IEEE CVPR</i>, 2017, pp. 4700–4708.",
        "[15] K. He <i>et al.</i>, \"Deep residual learning for image recognition,\" in "
        "<i>Proc. IEEE CVPR</i>, 2016, pp. 770–778.",
    ]
    for ref in refs:
        content.append(Paragraph(ref, S["ref"]))

    content.append(sp(8))

    # ── AUTHOR BIO ────────────────────────────────────────────────────────────
    content.append(Paragraph("ABHISHEK NARAYAN TRIPATHI", S["bio_name"]))
    bio_text = Paragraph(
        "Dr. Abhishek Narayan Tripathi received the B.E. degree in Electronics and Communication "
        "Engineering from Rajiv Gandhi Proudyogiki Vishwavidyalaya University, Bhopal, India, in "
        "2008, the M.Tech. degree in Microelectronics and Embedded Technology from Jaypee Institute "
        "of Information Technology, Noida, India, in 2012, and the Ph.D. degree in Electronics and "
        "Communication Engineering from Maulana Azad National Institute of Technology (MANIT), "
        "Bhopal, India, in 2020. He is currently an Assistant Professor with the Department of "
        "Electronics and Communication Engineering, School of Electronics Engineering, Vellore "
        "Institute of Technology (VIT), Vellore, Tamil Nadu, India. His research interests include "
        "FPGA based design for Edge Devices, Hardware Accelerator for AI, System-level design, "
        "VLSI Design, Design Space Exploration, and Reconfigurable Hardware architectures.",
        S["bio"])

    photo_path = f"{FIG}/author_photo.png"
    if os.path.exists(photo_path):
        photo_img = RLImage(photo_path, width=70, height=85)
        bio_tbl = Table(
            [[photo_img, bio_text]],
            colWidths=[80, USABLE_W - 80],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        content.append(bio_tbl)
    else:
        content.append(bio_text)

    return content


# ── Page template with headers/footers ───────────────────────────────────────
def on_first_page(canvas, doc):
    canvas.saveState()
    # IEEE Access logo area (top right)
    logo_path = "/home/claude/figures/ieee_logo.png"
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, doc.width + doc.leftMargin - 100, doc.height + doc.topMargin - 25,
                         width=100, height=22, preserveAspectRatio=True)
    # Bottom footer
    canvas.setFont("LiberationSans", 7)
    canvas.setFillColor(colors.HexColor("#003A70"))
    canvas.drawString(doc.leftMargin, doc.bottomMargin - 10, "VOLUME 4, 2016")
    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 10, "1")
    canvas.restoreState()


def on_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont("LiberationSans", 7)
    canvas.setFillColor(colors.HexColor("#003A70"))
    left = "A. N. Tripathi et al.: Preparation of Papers for IEEE ACCESS"
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 5, left)
    logo_path = "/home/claude/figures/ieee_logo.png"
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path,
                         doc.width + doc.leftMargin - 100,
                         doc.height + doc.topMargin,
                         width=100, height=20, preserveAspectRatio=True)
    canvas.drawString(doc.leftMargin, doc.bottomMargin - 10,
                      str(doc.page - 1))
    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 10,
                           "VOLUME 4, 2016")
    canvas.restoreState()


# ── Build PDF ─────────────────────────────────────────────────────────────────
def main():
    out = "/mnt/user-data/outputs/Tanaya_IEEEAccess_Humanized.pdf"
    os.makedirs(os.path.dirname(out), exist_ok=True)

    doc = SimpleDocTemplate(
        out,
        pagesize=letter,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP + 20,
        bottomMargin=MARGIN_BOTTOM + 10,
    )

    styles = make_styles()
    story = build_content(styles)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"✓ PDF saved to {out}")


if __name__ == "__main__":
    main()
