import re
from html import escape

from IPython.display import HTML, display

from .schema import EVIDENCE_BACKED_FIELDS


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


def _collect_excerpts(extraction):
    """Every evidence excerpt cited anywhere in an extraction (accepts model or dict)."""
    data = _to_dict(extraction)
    excerpts = []

    def _add(evidence_list):
        for evidence in evidence_list or []:
            excerpt = _to_dict(evidence).get("excerpt")
            if excerpt:
                excerpts.append(excerpt)

    for problem in data.get("problems") or []:
        problem = _to_dict(problem)
        _add(problem.get("core_evidence"))
        for field_name in EVIDENCE_BACKED_FIELDS:
            for item in problem.get(field_name) or []:
                _add(_to_dict(item).get("evidence"))
        for associated in problem.get("associated_symptoms") or []:
            _add(_to_dict(associated).get("evidence"))
    return excerpts


def _coverage_html(transcript, extraction, max_width="1000px"):
    """Build the coverage HTML (separated from display() so it is unit-testable)."""
    transcript = transcript or ""
    # Put each timestamped turn on its own line for readability.
    display_text = re.sub(r"(\[\d{1,2}:\d{2}\])", r"\n\1", transcript).lstrip("\n")

    excerpts = _collect_excerpts(extraction)
    haystack = display_text.lower()
    spans, missing = [], []
    for excerpt in excerpts:
        index = haystack.find(excerpt.lower())
        if index == -1:
            missing.append(excerpt)
        else:
            spans.append((index, index + len(excerpt)))

    # Merge overlapping/adjacent highlight spans.
    spans.sort()
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    parts, cursor = [], 0
    for start, end in merged:
        parts.append(escape(display_text[cursor:start]))
        parts.append('<mark class="tc-hit">' + escape(display_text[start:end]) + "</mark>")
        cursor = end
    parts.append(escape(display_text[cursor:]))
    body = "".join(parts).replace("\n", "<br>")

    total = len(excerpts)
    located = total - len(missing)

    missing_html = ""
    if missing:
        items = "".join("<li>“" + escape(m) + "”</li>" for m in missing)
        missing_html = (
            '<div class="tc-missing"><strong>' + str(len(missing))
            + " excerpt(s) not found verbatim in the transcript:</strong><ul>"
            + items + "</ul></div>"
        )

    style = """
    <style>
      .tc-wrap { max-width: MAXW; margin:12px 0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#202124; }
      .tc-head { font-size:13px; color:#475569; margin-bottom:8px; }
      .tc-body { padding:14px; border:1px solid #dfe3e8; border-radius:10px; background:#fff; line-height:1.7; font-size:14px; }
      .tc-hit { background:#fde68a; padding:1px 2px; border-radius:3px; }
      .tc-missing { margin-top:10px; padding:10px 12px; border-left:3px solid #f59e0b; background:#fffbeb; font-size:13px; color:#92400e; border-radius:6px; }
      .tc-missing ul { margin:6px 0 0; padding-left:18px; }
    </style>
    """.replace("MAXW", escape(str(max_width)))

    head = (
        '<div class="tc-head"><strong>Coverage:</strong> ' + str(located) + "/" + str(total)
        + " cited excerpts located and highlighted. Un-highlighted text was not cited — "
        "scan it for missed symptoms.</div>"
    )

    return (
        style + '<div class="tc-wrap">' + head
        + '<div class="tc-body">' + body + "</div>" + missing_html + "</div>"
    )


def show_transcript_coverage(transcript, extraction, max_width="1000px"):
    """Render the transcript with every cited evidence excerpt highlighted.

    See which parts of the conversation the extractor picked up; the *un*-highlighted
    spans are what it did not cite, so read those to spot missed symptoms. Excerpts are
    matched case-insensitively as substrings; any that can't be located are listed below
    (usually a sign the citation isn't verbatim).
    """
    display(HTML(_coverage_html(transcript, extraction, max_width=max_width)))


def _proposed_missing_excerpts(critique):
    """Verbatim excerpts the reviewer proposes as MISSING (accepts model or dict)."""
    data = _to_dict(critique)
    out = []
    for change in data.get("changes") or []:
        change = _to_dict(change)
        if change.get("kind") == "missing" and change.get("excerpt"):
            out.append(change["excerpt"])
    return out


def _review_diff_html(transcript, extraction, critique, max_width="1000px"):
    """Transcript with A's cited excerpts (green) and B's proposed-missing excerpts (orange)."""
    display_text = re.sub(r"(\[\d{1,2}:\d{2}\])", r"\n\1", transcript or "").lstrip("\n")
    n = len(display_text)
    marks = [None] * n
    low = display_text.lower()

    def apply(excerpts, cls, override):
        unlocated = []
        for excerpt in excerpts:
            if not excerpt:
                continue
            index = low.find(excerpt.lower())
            if index == -1:
                unlocated.append(excerpt)
                continue
            for i in range(index, index + len(excerpt)):
                if override or marks[i] is None:
                    marks[i] = cls
        return unlocated

    apply(_collect_excerpts(extraction), "a", True)          # green wins
    b_unlocated = apply(_proposed_missing_excerpts(critique), "b", False)  # orange on unmarked

    parts, i = [], 0
    while i < n:
        cls = marks[i]
        j = i
        while j < n and marks[j] == cls:
            j += 1
        segment = escape(display_text[i:j])
        parts.append('<mark class="rv-' + cls + '">' + segment + "</mark>" if cls else segment)
        i = j
    body = "".join(parts).replace("\n", "<br>")

    changes = [_to_dict(c) for c in (_to_dict(critique).get("changes") or [])]
    if changes:
        rows = []
        for change in changes:
            kind = str(change.get("kind", "?"))
            excerpt = change.get("excerpt")
            field = change.get("field")
            rows.append(
                '<li class="rv-change rv-' + escape(kind) + '">'
                + '<span class="rv-kind">' + escape(kind) + "</span> "
                + "<strong>" + escape(str(change.get("problem", "—"))) + "</strong>"
                + (" · " + escape(str(field)) if field else "")
                + "<div>" + escape(str(change.get("text", ""))) + "</div>"
                + '<div class="rv-reason">' + escape(str(change.get("reason", ""))) + "</div>"
                + ('<div class="rv-ex">“' + escape(excerpt) + "”</div>" if excerpt else "")
                + "</li>"
            )
        proposals = '<ul class="rv-list">' + "".join(rows) + "</ul>"
    else:
        proposals = '<div class="rv-none">Reviewer proposed no changes.</div>'

    unlocated_note = ""
    if b_unlocated:
        items = "".join("<li>“" + escape(u) + "”</li>" for u in b_unlocated)
        unlocated_note = (
            '<div class="rv-warn"><strong>' + str(len(b_unlocated))
            + " reviewer excerpt(s) not found verbatim (can't highlight):</strong><ul>"
            + items + "</ul></div>"
        )

    style = """
    <style>
      .rv-wrap { max-width: MAXW; margin:12px 0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#202124; }
      .rv-legend { font-size:13px; color:#475569; margin-bottom:8px; }
      .rv-body { padding:14px; border:1px solid #dfe3e8; border-radius:10px; background:#fff; line-height:1.7; font-size:14px; }
      .rv-a { background:#bbf7d0; border-radius:3px; padding:1px 2px; }
      .rv-b { background:#fed7aa; border-radius:3px; padding:1px 2px; }
      .rv-props-title { margin:14px 0 6px; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; color:#475569; }
      .rv-list { list-style:none; margin:0; padding:0; }
      .rv-change { padding:10px 12px; margin-bottom:8px; border:1px solid #e5e7eb; border-left:3px solid #94a3b8; border-radius:6px; font-size:13px; }
      .rv-missing { border-left-color:#f59e0b; }
      .rv-wrong { border-left-color:#ef4444; }
      .rv-misattributed { border-left-color:#8b5cf6; }
      .rv-kind { display:inline-block; font-size:10px; font-weight:700; text-transform:uppercase; padding:2px 6px; border-radius:999px; background:#e2e8f0; color:#475569; }
      .rv-reason { color:#64748b; font-style:italic; margin-top:2px; }
      .rv-ex { color:#334155; background:#f8fafc; border-left:2px solid #cbd5e1; padding:4px 8px; margin-top:4px; border-radius:4px; font-size:12px; }
      .rv-none { color:#16a34a; font-size:13px; }
      .rv-warn { margin-top:10px; padding:8px 10px; border-left:3px solid #f59e0b; background:#fffbeb; color:#92400e; font-size:12px; border-radius:6px; }
      .rv-warn ul { margin:4px 0 0; padding-left:18px; }
    </style>
    """.replace("MAXW", escape(str(max_width)))

    legend = (
        '<div class="rv-legend"><strong>Extractor vs reviewer.</strong> '
        '<mark class="rv-a">green</mark> = captured by extractor (A) · '
        '<mark class="rv-b">orange</mark> = reviewer (B) says this was missed. '
        "Read the orange spans and the proposals below.</div>"
    )

    return (
        style + '<div class="rv-wrap">' + legend
        + '<div class="rv-body">' + body + "</div>" + unlocated_note
        + '<div class="rv-props-title">Reviewer proposals (' + str(len(changes)) + ")</div>"
        + proposals + "</div>"
    )


def show_review_diff(transcript, extraction, critique, max_width="1000px"):
    """Render the extractor-vs-reviewer diff.

    The transcript is highlighted green where the extractor (A) cited evidence and orange
    where the reviewer (B) says a symptom was missed, followed by B's list of proposed
    changes. Un-highlighted text is what neither model flagged.
    """
    display(HTML(_review_diff_html(transcript, extraction, critique, max_width=max_width)))