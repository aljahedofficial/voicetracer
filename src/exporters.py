"""
VoiceTracer Export Module

Generates exportable reports in multiple formats (PDF, DOCX, XLSX, PPTX, CSV, JSON, PNG, ZIP).
"""

import json
import csv
import io
from pathlib import Path
from typing import Dict, List, Any, BinaryIO
from datetime import datetime
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors


class ExportMetadata:
    """Generate metadata for exports."""
    
    @staticmethod
    def create_metadata(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict
    ) -> Dict[str, Any]:
        """Create metadata for export."""
        return {
            'title': 'VoiceTracer Analysis Report',
            'created_at': datetime.now().isoformat(),
            'analysis_id': analysis_result.doc_pair_id,
            'original_text_stats': original_metadata,
            'edited_text_stats': edited_metadata,
            'metrics': {
                'original': {
                    'burstiness': analysis_result.original_metrics.burstiness,
                    'lexical_diversity': analysis_result.original_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.original_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.original_metrics.ai_ism_likelihood,
                },
                'edited': {
                    'burstiness': analysis_result.edited_metrics.burstiness,
                    'lexical_diversity': analysis_result.edited_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.edited_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.edited_metrics.ai_ism_likelihood,
                },
                'deltas': {
                    'burstiness_delta': analysis_result.metric_deltas.burstiness_delta,
                    'burstiness_pct_change': analysis_result.metric_deltas.burstiness_pct_change,
                    'lexical_diversity_delta': analysis_result.metric_deltas.lexical_diversity_delta,
                    'lexical_diversity_pct_change': analysis_result.metric_deltas.lexical_diversity_pct_change,
                    'syntactic_complexity_delta': analysis_result.metric_deltas.syntactic_complexity_delta,
                    'syntactic_complexity_pct_change': analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    'ai_ism_delta': analysis_result.metric_deltas.ai_ism_delta,
                    'ai_ism_pct_change': analysis_result.metric_deltas.ai_ism_pct_change,
                },
            },
            'thesis_alignment': {
                'research_questions_addressed': [
                    'How does AI editing affect L2 learner writing characteristics?',
                    'Can we quantify stylistic differences between human and AI-edited text?',
                    'What linguistic markers indicate AI involvement?',
                    'How can L2 learners preserve voice while improving grammar?',
                ],
                'methodology': 'VoiceTracer v0.1.0',
                'source': 'https://github.com/VoiceTracer',
            },
        }


class CSVExporter:
    """Export data to CSV format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        include_original_text: bool = False,
        include_edited_text: bool = False,
        **options
    ) -> str:
        """
        Generate CSV export with analysis data.
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header section
        writer.writerow(['VoiceTracer Analysis Report'])
        writer.writerow(['Generated:', datetime.now().isoformat()])
        writer.writerow([])

        # Text statistics
        writer.writerow(['Text Statistics'])
        writer.writerow(['Metric', 'Original', 'Edited', 'Delta', '% Change'])
        writer.writerow(['Word Count',
                        original_metadata.get('word_count', 0),
                        edited_metadata.get('word_count', 0),
                        edited_metadata.get('word_count', 0) - original_metadata.get('word_count', 0),
                        ''])
        writer.writerow(['Character Count',
                        original_metadata.get('char_count', 0),
                        edited_metadata.get('char_count', 0),
                        edited_metadata.get('char_count', 0) - original_metadata.get('char_count', 0),
                        ''])
        writer.writerow(['Sentence Count',
                        original_metadata.get('sentence_count', 0),
                        edited_metadata.get('sentence_count', 0),
                        edited_metadata.get('sentence_count', 0) - original_metadata.get('sentence_count', 0),
                        ''])
        writer.writerow([])

        # Metrics
        writer.writerow(['Metric Comparison'])
        writer.writerow(['Metric', 'Original', 'Edited', 'Delta', '% Change'])

        metrics_to_export = [
            ('Burstiness', 'burstiness'),
            ('Lexical Diversity', 'lexical_diversity'),
            ('Syntactic Complexity', 'syntactic_complexity'),
            ('AI-ism Likelihood', 'ai_ism_likelihood'),
        ]
        metrics_delta_map = {
            'burstiness': (analysis_result.metric_deltas.burstiness_delta,
                           analysis_result.metric_deltas.burstiness_pct_change),
            'lexical_diversity': (analysis_result.metric_deltas.lexical_diversity_delta,
                                  analysis_result.metric_deltas.lexical_diversity_pct_change),
            'syntactic_complexity': (analysis_result.metric_deltas.syntactic_complexity_delta,
                                     analysis_result.metric_deltas.syntactic_complexity_pct_change),
            'ai_ism_likelihood': (analysis_result.metric_deltas.ai_ism_delta,
                                  analysis_result.metric_deltas.ai_ism_pct_change),
        }

        for label, key in metrics_to_export:
            orig = getattr(analysis_result.original_metrics, key)
            edit = getattr(analysis_result.edited_metrics, key)
            delta, pct = metrics_delta_map.get(key, (edit - orig, 0))

            writer.writerow([label, round(orig, 3), round(edit, 3), round(delta, 3), f'{pct:+.1f}%'])

        writer.writerow([])

        # AI-isms detected
        if analysis_result.ai_isms:
            writer.writerow(['AI-isms Detected'])
            writer.writerow(['Phrase', 'Category', 'Context'])
            for ai_ism in analysis_result.ai_isms:
                writer.writerow([
                    ai_ism.get('phrase', ''),
                    ai_ism.get('category', ''),
                    ai_ism.get('context', '')[:100],  # Truncate context
                ])

        return output.getvalue()


class JSONExporter:
    """Export data to JSON format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        include_original_text: bool = False,
        include_edited_text: bool = False,
        **options
    ) -> str:
        """
        Generate JSON export with full analysis data.
        
        Returns:
            JSON string
        """
        export_data = {
            'metadata': ExportMetadata.create_metadata(
                analysis_result,
                doc_pair,
                original_metadata,
                edited_metadata
            ),
            'text_statistics': {
                'original': original_metadata,
                'edited': edited_metadata,
            },
            'metrics': {
                'original': {
                    'burstiness': analysis_result.original_metrics.burstiness,
                    'lexical_diversity': analysis_result.original_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.original_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.original_metrics.ai_ism_likelihood,
                },
                'edited': {
                    'burstiness': analysis_result.edited_metrics.burstiness,
                    'lexical_diversity': analysis_result.edited_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.edited_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.edited_metrics.ai_ism_likelihood,
                },
                'deltas': {
                    'burstiness': {
                        'delta': analysis_result.metric_deltas.burstiness_delta,
                        'pct_change': analysis_result.metric_deltas.burstiness_pct_change,
                    },
                    'lexical_diversity': {
                        'delta': analysis_result.metric_deltas.lexical_diversity_delta,
                        'pct_change': analysis_result.metric_deltas.lexical_diversity_pct_change,
                    },
                    'syntactic_complexity': {
                        'delta': analysis_result.metric_deltas.syntactic_complexity_delta,
                        'pct_change': analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    },
                    'ai_ism_likelihood': {
                        'delta': analysis_result.metric_deltas.ai_ism_delta,
                        'pct_change': analysis_result.metric_deltas.ai_ism_pct_change,
                    },
                },
            },
            'ai_isms_detected': [
                {
                    'phrase': ai.get('phrase'),
                    'category': ai.get('category'),
                    'context': ai.get('context'),
                }
                for ai in analysis_result.ai_isms
            ],
        }
        
        if include_original_text:
            export_data['texts'] = {'original': doc_pair.original_text}
        if include_edited_text:
            export_data['texts'] = export_data.get('texts', {})
            export_data['texts']['edited'] = doc_pair.edited_text
        
        return json.dumps(export_data, indent=2)


class PDFExporter:
    """Export to PDF format (using reportlab)."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> bytes:
        """
        Generate PDF report using reportlab.
        
        Returns:
            BytesIO object with PDF data
        """
        pdf_content = io.BytesIO()
        doc = SimpleDocTemplate(pdf_content, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=WD_PARAGRAPH_ALIGNMENT.CENTER
        )
        story.append(Paragraph("VoiceTracer Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Text Statistics
        story.append(Paragraph("Text Statistics", styles['Heading2']))
        stats_data = [
            ['Metric', 'Original', 'Edited', 'Change'],
            ['Word Count', str(original_metadata.get('word_count', 0)), str(edited_metadata.get('word_count', 0)), 
             str(edited_metadata.get('word_count', 0) - original_metadata.get('word_count', 0))],
            ['Character Count', str(original_metadata.get('character_count', 0)), str(edited_metadata.get('character_count', 0)),
             str(edited_metadata.get('character_count', 0) - original_metadata.get('character_count', 0))],
            ['Sentence Count', str(original_metadata.get('sentence_count', 0)), str(edited_metadata.get('sentence_count', 0)),
             str(edited_metadata.get('sentence_count', 0) - original_metadata.get('sentence_count', 0))],
        ]
        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Metrics Comparison
        story.append(Paragraph("Metric Comparison", styles['Heading2']))
        metrics_data = [
            ['Metric', 'Original', 'Edited', 'Change (%)'],
            ['Burstiness', f"{analysis_result.original_metrics.burstiness:.3f}", 
             f"{analysis_result.edited_metrics.burstiness:.3f}",
             f"{analysis_result.metric_deltas.burstiness_pct_change:+.1f}%"],
            ['Lexical Diversity', f"{analysis_result.original_metrics.lexical_diversity:.3f}",
             f"{analysis_result.edited_metrics.lexical_diversity:.3f}",
             f"{analysis_result.metric_deltas.lexical_diversity_pct_change:+.1f}%"],
            ['Syntactic Complexity', f"{analysis_result.original_metrics.syntactic_complexity:.3f}",
             f"{analysis_result.edited_metrics.syntactic_complexity:.3f}",
             f"{analysis_result.metric_deltas.syntactic_complexity_pct_change:+.1f}%"],
            ['AI-ism Likelihood', f"{analysis_result.original_metrics.ai_ism_likelihood:.1f}",
             f"{analysis_result.edited_metrics.ai_ism_likelihood:.1f}",
             f"{analysis_result.metric_deltas.ai_ism_pct_change:+.1f}%"],
        ]
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # AI-isms detected
        if analysis_result.ai_isms:
            story.append(PageBreak())
            story.append(Paragraph("AI-isms Detected", styles['Heading2']))
            for ai_ism in analysis_result.ai_isms[:5]:
                story.append(Paragraph(f"<b>{ai_ism.get('phrase', 'N/A')}</b> ({ai_ism.get('category', 'N/A')})", styles['Normal']))
                story.append(Paragraph(f"<i>{ai_ism.get('context', 'N/A')[:100]}</i>", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        pdf_content.seek(0)
        return pdf_content.getvalue()


class ExcelExporter:
    """Export to Excel (XLSX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate Excel workbook with multiple sheets.
        
        Sheets:
        1. Summary - Key metrics and stats
        2. Detailed Metrics - Full metric values
        3. Text Statistics - Word count, etc.
        4. AI-isms - Detected phrases and context
        5. Recommendations - Actionable suggestions
        
        Returns:
            BytesIO object with XLSX data
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_data = {
                'Metric': ['Burstiness', 'Lexical Diversity', 'Syntactic Complexity', 'AI-ism Likelihood'],
                'Original': [
                    analysis_result.original_metrics.burstiness,
                    analysis_result.original_metrics.lexical_diversity,
                    analysis_result.original_metrics.syntactic_complexity,
                    analysis_result.original_metrics.ai_ism_likelihood,
                ],
                'Edited': [
                    analysis_result.edited_metrics.burstiness,
                    analysis_result.edited_metrics.lexical_diversity,
                    analysis_result.edited_metrics.syntactic_complexity,
                    analysis_result.edited_metrics.ai_ism_likelihood,
                ],
                'Change (%)': [
                    analysis_result.metric_deltas.burstiness_pct_change,
                    analysis_result.metric_deltas.lexical_diversity_pct_change,
                    analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    analysis_result.metric_deltas.ai_ism_pct_change,
                ],
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Text Statistics
            stats_data = {
                'Statistic': ['Word Count', 'Character Count', 'Sentence Count', 'Avg Sentence Length'],
                'Original': [
                    original_metadata.get('word_count', 0),
                    original_metadata.get('char_count', 0),
                    original_metadata.get('sentence_count', 0),
                    original_metadata.get('avg_sentence_length', 0),
                ],
                'Edited': [
                    edited_metadata.get('word_count', 0),
                    edited_metadata.get('char_count', 0),
                    edited_metadata.get('sentence_count', 0),
                    edited_metadata.get('avg_sentence_length', 0),
                ],
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
        
        output.seek(0)
        return output


class DocxExporter:
    """Export to Word (DOCX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> bytes:
        """
        Generate Word document with analysis using python-docx.
        
        Returns:
            BytesIO object with DOCX data
        """
        doc = Document()
        
        # Title
        title = doc.add_heading('VoiceTracer Analysis Report', 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Metadata
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph()
        
        # Text Statistics
        doc.add_heading('Text Statistics', 1)
        stats_table = doc.add_table(rows=4, cols=4)
        stats_table.style = 'Light Grid Accent 1'
        
        # Header row
        header_cells = stats_table.rows[0].cells
        header_cells[0].text = 'Metric'
        header_cells[1].text = 'Original'
        header_cells[2].text = 'Edited'
        header_cells[3].text = 'Change'
        
        # Data rows
        rows_data = [
            ['Word Count', str(original_metadata.get('word_count', 0)), str(edited_metadata.get('word_count', 0)),
             str(edited_metadata.get('word_count', 0) - original_metadata.get('word_count', 0))],
            ['Character Count', str(original_metadata.get('character_count', 0)), str(edited_metadata.get('character_count', 0)),
             str(edited_metadata.get('character_count', 0) - original_metadata.get('character_count', 0))],
            ['Sentence Count', str(original_metadata.get('sentence_count', 0)), str(edited_metadata.get('sentence_count', 0)),
             str(edited_metadata.get('sentence_count', 0) - original_metadata.get('sentence_count', 0))],
        ]
        
        for i, row_data in enumerate(rows_data, start=1):
            cells = stats_table.rows[i].cells
            for j, text in enumerate(row_data):
                cells[j].text = text
        
        doc.add_paragraph()
        
        # Metrics Comparison
        doc.add_heading('Metric Comparison', 1)
        metrics_table = doc.add_table(rows=5, cols=4)
        metrics_table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = metrics_table.rows[0].cells
        header_cells[0].text = 'Metric'
        header_cells[1].text = 'Original'
        header_cells[2].text = 'Edited'
        header_cells[3].text = 'Change (%)'
        
        # Metrics data
        metrics_rows = [
            ['Burstiness', f"{analysis_result.original_metrics.burstiness:.3f}", 
             f"{analysis_result.edited_metrics.burstiness:.3f}",
             f"{analysis_result.metric_deltas.burstiness_pct_change:+.1f}%"],
            ['Lexical Diversity', f"{analysis_result.original_metrics.lexical_diversity:.3f}",
             f"{analysis_result.edited_metrics.lexical_diversity:.3f}",
             f"{analysis_result.metric_deltas.lexical_diversity_pct_change:+.1f}%"],
            ['Syntactic Complexity', f"{analysis_result.original_metrics.syntactic_complexity:.3f}",
             f"{analysis_result.edited_metrics.syntactic_complexity:.3f}",
             f"{analysis_result.metric_deltas.syntactic_complexity_pct_change:+.1f}%"],
            ['AI-ism Likelihood', f"{analysis_result.original_metrics.ai_ism_likelihood:.1f}",
             f"{analysis_result.edited_metrics.ai_ism_likelihood:.1f}",
             f"{analysis_result.metric_deltas.ai_ism_pct_change:+.1f}%"],
        ]
        
        for i, row_data in enumerate(metrics_rows, start=1):
            cells = metrics_table.rows[i].cells
            for j, text in enumerate(row_data):
                cells[j].text = text
        
        doc.add_paragraph()
        
        # AI-isms Detected
        if analysis_result.ai_isms:
            doc.add_heading('AI-isms Detected', 1)
            for ai_ism in analysis_result.ai_isms[:5]:
                phrase = ai_ism.get('phrase', 'N/A')
                category = ai_ism.get('category', 'N/A')
                context = ai_ism.get('context', 'N/A')[:150]
                
                p = doc.add_paragraph()
                p.add_run(f"{phrase} ").bold = True
                p.add_run(f"({category})")
                
                doc.add_paragraph(context, style='List Bullet')
            
            doc.add_paragraph()
        
        # Original Text (if included)
        if options.get('include_original_text', False):
            doc.add_page_break()
            doc.add_heading('Original Text', 1)
            doc.add_paragraph(doc_pair.original_text)
        
        # Edited Text (if included)
        if options.get('include_edited_text', False):
            doc.add_page_break()
            doc.add_heading('Edited Text', 1)
            doc.add_paragraph(doc_pair.edited_text)
        
        # Save to BytesIO
        docx_content = io.BytesIO()
        doc.save(docx_content)
        docx_content.seek(0)
        return docx_content.getvalue()


class PowerPointExporter:
    """Export to PowerPoint (PPTX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate PowerPoint presentation with slides.
        
        Note: Uses python-pptx to create presentations with:
        - 9 slides covering analysis
        - Embedded charts
        - Speaker notes
        - Editable by instructors
        
        Returns:
            BytesIO object with PPTX data
        """
        # Placeholder - full implementation would use python-pptx
        pptx_content = io.BytesIO()
        pptx_content.write(b'PPTX Export - Not yet implemented')
        pptx_content.seek(0)
        return pptx_content


class ExportFactory:
    """Factory for creating exporters based on format."""
    
    EXPORTERS = {
        'csv': CSVExporter,
        'json': JSONExporter,
        'xlsx': ExcelExporter,
        'docx': DocxExporter,
        'pptx': PowerPointExporter,
        'pdf': PDFExporter,
    }
    
    @staticmethod
    def export(
        format_type: str,
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> Any:
        """
        Generate export in specified format.
        
        Args:
            format_type: 'csv', 'json', 'xlsx', 'docx', 'pptx', 'pdf'
            analysis_result: AnalysisResult object
            doc_pair: DocumentPair object
            original_metadata: Original text metadata dict
            edited_metadata: Edited text metadata dict
            **options: Additional format-specific options
        
        Returns:
            Export data (string for CSV/JSON, BytesIO for binary formats)
        """
        if format_type not in ExportFactory.EXPORTERS:
            raise ValueError(f"Unsupported format: {format_type}")
        
        exporter_class = ExportFactory.EXPORTERS[format_type]
        return exporter_class.export(
            analysis_result,
            doc_pair,
            original_metadata,
            edited_metadata,
            **options
        )
