from html import escape
from IPython.display import HTML, display


def _to_dict(value):
    """
    Convert a Pydantic model, dictionary, or similar object
    into a plain Python dictionary.
    """
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):  # Pydantic v2
        return value.model_dump()

    if hasattr(value, "dict"):  # Pydantic v1
        return value.dict()

    return vars(value)


def _safe_text(value, default="—"):
    """
    Convert a value into HTML-safe text.
    """
    if value is None or value == "":
        return escape(default)

    return escape(str(value))


def _safe_css_class(value, default="unknown"):
    """
    Convert a status into a safe CSS class component.
    """
    value = str(value or default).lower()

    allowed = {"present", "denied", "uncertain", "unknown"}

    return value if value in allowed else default


def _render_status(status):
    """
    Render a coloured status badge.
    """
    status_value = str(status or "unknown")
    status_class = _safe_css_class(status_value)

    return f"""
    <span class="sem-status sem-status-{status_class}">
        {escape(status_value)}
    </span>
    """


def _render_evidence_inline(evidence):
    """
    Render transcript evidence directly inside the evidence column.
    """
    evidence = evidence or []

    if not evidence:
        return """
        <span class="sem-no-evidence">
            No evidence
        </span>
        """

    rendered_items = []

    for evidence_item in evidence:
        evidence_item = _to_dict(evidence_item)

        timestamp = _safe_text(
            evidence_item.get("timestamp"),
            default="No timestamp",
        )

        speaker = _safe_text(
            evidence_item.get("speaker"),
            default="Unknown speaker",
        )

        excerpt = _safe_text(
            evidence_item.get("excerpt"),
            default="No excerpt",
        )

        rendered_items.append(
            f"""
            <div class="sem-evidence-item">
                <div class="sem-evidence-meta">
                    <span class="sem-evidence-time">
                        {timestamp}
                    </span>

                    <span class="sem-evidence-speaker">
                        {speaker}
                    </span>
                </div>

                <div class="sem-evidence-excerpt">
                    “{excerpt}”
                </div>
            </div>
            """
        )

    return "".join(rendered_items)


def _make_plain_row(label, value, status=False):
    """
    Create a row for a plain, non-evidence-backed value.
    """
    if status:
        rendered_value = _render_status(value)
    else:
        rendered_value = _safe_text(value)

    return {
        "label": label,
        "value": rendered_value,
        "evidence": '<span class="sem-not-applicable">—</span>',
        "group_start": True,
    }


def _make_evidence_backed_rows(label, items):
    """
    Create one table row per EvidenceBackedText item.

    The field label is shown only on the first row of the group.
    """
    items = items or []
    rows = []

    for item_index, item in enumerate(items):
        item = _to_dict(item)

        rows.append(
            {
                "label": label if item_index == 0 else "",
                "value": _safe_text(item.get("text")),
                "evidence": _render_evidence_inline(
                    item.get("evidence")
                ),
                "group_start": item_index == 0,
            }
        )

    return rows


def _make_associated_symptom_rows(symptoms):
    """
    Create one row per associated symptom.
    """
    symptoms = symptoms or []
    rows = []

    for symptom_index, symptom in enumerate(symptoms):
        symptom = _to_dict(symptom)

        symptom_name = _safe_text(
            symptom.get("symptom")
        )

        symptom_status = _render_status(
            symptom.get("status")
        )

        value_html = f"""
        <div class="sem-associated-value">
            <span class="sem-associated-name">
                {symptom_name}
            </span>

            {symptom_status}
        </div>
        """

        rows.append(
            {
                "label": (
                    "Associated symptoms"
                    if symptom_index == 0
                    else ""
                ),
                "value": value_html,
                "evidence": _render_evidence_inline(
                    symptom.get("evidence")
                ),
                "group_start": symptom_index == 0,
            }
        )

    return rows


def _make_core_evidence_rows(core_evidence):
    """
    Render core problem evidence at the bottom of the table.
    """
    core_evidence = core_evidence or []

    if not core_evidence:
        return []

    return [
        {
            "label": "Core evidence",
            "value": """
                <span class="sem-core-description">
                    Evidence supporting the identification
                    of this problem
                </span>
            """,
            "evidence": _render_evidence_inline(core_evidence),
            "group_start": True,
        }
    ]


def show_symptom_evidence_matrix(
    extraction,
    show_empty_fields=False,
    show_associated_symptoms=True,
    show_core_evidence=True,
    max_width="1400px",
):
    """
    Display a SymptomExtraction result as an evidence matrix.

    Parameters
    ----------
    extraction:
        SymptomExtraction Pydantic model or dictionary.

    show_empty_fields:
        When True, fields with no extracted values are also shown.

    show_associated_symptoms:
        When True, associated symptoms are included.

    show_core_evidence:
        When True, core evidence is shown at the bottom of each
        problem table.

    max_width:
        Maximum width of the output, for example "1400px" or "100%".
    """
    extraction_data = _to_dict(extraction)
    problems = extraction_data.get("problems") or []

    field_mapping = [
        ("Quality", "quality"),
        ("Course", "course"),
        ("Severity", "severity"),
        ("Onset", "onset"),
        ("Duration", "duration"),
        ("Frequency", "frequency"),
        ("Provoked by", "provoking_factors"),
        ("Relieved by", "relieving_factors"),
        (
            "Negative characteristics",
            "negative_characteristics",
        ),
    ]

    rendered_problems = []

    for problem_index, problem in enumerate(problems, start=1):
        problem = _to_dict(problem)
        rows = []

        # Basic problem information
        rows.append(
            _make_plain_row(
                "Anatomical site",
                problem.get("anatomical_site"),
            )
        )

        rows.append(
            _make_plain_row(
                "Laterality",
                problem.get("laterality"),
            )
        )

        rows.append(
            _make_plain_row(
                "Status",
                problem.get("status"),
                status=True,
            )
        )

        # Evidence-backed descriptive fields
        for field_label, field_name in field_mapping:
            field_items = problem.get(field_name) or []

            if field_items:
                rows.extend(
                    _make_evidence_backed_rows(
                        field_label,
                        field_items,
                    )
                )

            elif show_empty_fields:
                rows.append(
                    {
                        "label": field_label,
                        "value": (
                            '<span class="sem-empty">—</span>'
                        ),
                        "evidence": (
                            '<span class="sem-not-applicable">'
                            "—"
                            "</span>"
                        ),
                        "group_start": True,
                    }
                )

        # Associated symptoms
        if show_associated_symptoms:
            associated_symptoms = (
                problem.get("associated_symptoms") or []
            )

            if associated_symptoms:
                rows.extend(
                    _make_associated_symptom_rows(
                        associated_symptoms
                    )
                )

            elif show_empty_fields:
                rows.append(
                    {
                        "label": "Associated symptoms",
                        "value": (
                            '<span class="sem-empty">—</span>'
                        ),
                        "evidence": (
                            '<span class="sem-not-applicable">'
                            "—"
                            "</span>"
                        ),
                        "group_start": True,
                    }
                )

        # Core evidence
        if show_core_evidence:
            rows.extend(
                _make_core_evidence_rows(
                    problem.get("core_evidence")
                )
            )

        table_rows = []

        for row in rows:
            group_class = (
                "sem-group-start"
                if row.get("group_start")
                else "sem-group-continuation"
            )

            table_rows.append(
                f"""
                <tr class="{group_class}">
                    <th class="sem-field-cell">
                        {escape(row["label"])}
                    </th>

                    <td class="sem-value-cell">
                        {row["value"]}
                    </td>

                    <td class="sem-evidence-cell">
                        {row["evidence"]}
                    </td>
                </tr>
                """
            )

        problem_name = _safe_text(
            problem.get("problem"),
            default=f"Problem {problem_index}",
        )

        problem_status = _render_status(
            problem.get("status")
        )

        rendered_problems.append(
            f"""
            <section class="sem-problem">
                <div class="sem-problem-header">
                    <div>
                        <div class="sem-problem-number">
                            Problem {problem_index}
                        </div>

                        <h2 class="sem-problem-title">
                            {problem_name}
                        </h2>
                    </div>

                    <div class="sem-problem-status">
                        {problem_status}
                    </div>
                </div>

                <div class="sem-table-wrapper">
                    <table class="sem-table">
                        <colgroup>
                            <col class="sem-field-column">
                            <col class="sem-value-column">
                            <col class="sem-evidence-column">
                        </colgroup>

                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Extracted value</th>
                                <th>Supporting evidence</th>
                            </tr>
                        </thead>

                        <tbody>
                            {''.join(table_rows)}
                        </tbody>
                    </table>
                </div>
            </section>
            """
        )

    if not problems:
        rendered_problems.append(
            """
            <div class="sem-no-problems">
                No symptom problems were extracted.
            </div>
            """
        )

    css = f"""
    <style>
        .sem-container {{
            width: 100%;
            max-width: {escape(str(max_width))};
            margin: 16px 0;
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            color: #202124;
        }}

        .sem-problem {{
            margin-bottom: 36px;
        }}

        .sem-problem-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 14px;
        }}

        .sem-problem-number {{
            margin-bottom: 5px;
            color: #6b7280;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .sem-problem-title {{
            margin: 0;
            font-size: 20px;
            line-height: 1.4;
        }}

        .sem-problem-status {{
            flex-shrink: 0;
        }}

        .sem-table-wrapper {{
            width: 100%;
            overflow-x: auto;
            border: 1px solid #dfe3e8;
            border-radius: 10px;
        }}

        .sem-table {{
            width: 100%;
            min-width: 850px;
            border-collapse: collapse;
            table-layout: fixed;
            background: white;
        }}

        .sem-table th,
        .sem-table td {{
            padding: 12px 14px;
            border-right: 1px solid #e5e7eb;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
            text-align: left;
        }}

        .sem-table th:last-child,
        .sem-table td:last-child {{
            border-right: none;
        }}

        .sem-table tbody tr:last-child th,
        .sem-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        .sem-table thead th {{
            background: #f1f5f9;
            color: #475569;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .sem-field-column {{
            width: 17%;
        }}

        .sem-value-column {{
            width: 31%;
        }}

        .sem-evidence-column {{
            width: 52%;
        }}

        .sem-field-cell {{
            background: #f8fafc;
            color: #475569;
            font-size: 13px;
            font-weight: 700;
        }}

        .sem-value-cell {{
            font-size: 14px;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }}

        .sem-evidence-cell {{
            background: #fcfcfd;
        }}

        .sem-group-start:not(:first-child) th,
        .sem-group-start:not(:first-child) td {{
            border-top: 2px solid #dbe1e8;
        }}

        .sem-group-continuation .sem-field-cell {{
            background: #f8fafc;
        }}

        .sem-evidence-item {{
            margin-bottom: 8px;
            padding: 9px 11px;
            border-left: 3px solid #94a3b8;
            border-radius: 5px;
            background: #f8fafc;
        }}

        .sem-evidence-item:last-child {{
            margin-bottom: 0;
        }}

        .sem-evidence-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
        }}

        .sem-evidence-time {{
            color: #334155;
            font-family:
                ui-monospace,
                SFMono-Regular,
                Menlo,
                monospace;
            font-size: 11px;
            font-weight: 700;
        }}

        .sem-evidence-speaker {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 999px;
            background: #e2e8f0;
            color: #475569;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .sem-evidence-excerpt {{
            color: #334155;
            font-size: 12px;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }}

        .sem-associated-value {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
        }}

        .sem-associated-name {{
            min-width: 0;
            overflow-wrap: anywhere;
        }}

        .sem-status {{
            display: inline-block;
            flex-shrink: 0;
            padding: 3px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            white-space: nowrap;
        }}

        .sem-status-present {{
            background: #dcfce7;
            color: #166534;
        }}

        .sem-status-denied {{
            background: #f1f5f9;
            color: #475569;
        }}

        .sem-status-uncertain {{
            background: #fef3c7;
            color: #92400e;
        }}

        .sem-status-unknown {{
            background: #e5e7eb;
            color: #4b5563;
        }}

        .sem-no-evidence {{
            color: #b91c1c;
            font-size: 12px;
            font-weight: 600;
        }}

        .sem-not-applicable,
        .sem-empty {{
            color: #9ca3af;
        }}

        .sem-core-description {{
            color: #64748b;
            font-size: 13px;
            font-style: italic;
        }}

        .sem-no-problems {{
            padding: 18px;
            border: 1px solid #dfe3e8;
            border-radius: 10px;
            color: #64748b;
            background: #f8fafc;
        }}

        @media (max-width: 900px) {{
            .sem-field-column {{
                width: 20%;
            }}

            .sem-value-column {{
                width: 34%;
            }}

            .sem-evidence-column {{
                width: 46%;
            }}
        }}
    </style>
    """

    output_html = f"""
    {css}

    <div class="sem-container">
        {''.join(rendered_problems)}
    </div>
    """

    display(HTML(output_html))