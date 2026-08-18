import json
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from io import BytesIO

from app import db
from app.models import Assay, Control, PCRExperiment, PCRTemplate, Reagent, Sample
from app.services.experiment_service import add_cycle_group, add_program_step, delete_program_step, master_mix_reactions, master_mix_totals, move_program_step, total_reactions, update_program_step
from app.services.pcr_file_service import experiment_from_dict, experiment_json

pcr_bp = Blueprint("pcr", __name__)


def _protocol_time_seconds(value):
    value = (value or "").strip()
    if not value or value == "∞":
        return 0
    if ":" in value:
        minutes, seconds = value.split(":", 1)
        return round(float(minutes or 0) * 60 + float(seconds or 0))
    return round(float(value))


def _delete_experiment(record):
    for sample in list(record.samples):
        db.session.delete(sample)
    for control in list(record.controls):
        db.session.delete(control)
    db.session.delete(record)


@pcr_bp.get("/")
def index():
    return render_template(
        "pcr/index.html",
        experiment_count=PCRExperiment.query.count(),
        template_count=PCRTemplate.query.count(),
    )


@pcr_bp.route("/experiments", methods=["GET", "POST"])
def experiments():
    experiments = PCRExperiment.query.order_by(PCRExperiment.updated_at.desc()).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            experiment = PCRExperiment(name=name, notes=request.form.get("notes", "").strip() or None)
            db.session.add(experiment)
            db.session.commit()
            flash("Experiment created. Review the calculation before saving it.", "success")
            return redirect(url_for("pcr.experiment", experiment_id=experiment.id))
        flash("Experiment name is required.", "danger")
    return render_template("pcr/experiment_list.html", experiments=experiments)


@pcr_bp.post("/experiments/<int:experiment_id>/delete")
def delete_experiment(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    _delete_experiment(record)
    db.session.commit()
    flash("Experiment deleted.", "success")
    return redirect(url_for("pcr.experiments"))


@pcr_bp.post("/experiments/clear")
def clear_experiments():
    records = PCRExperiment.query.all()
    for record in records:
        _delete_experiment(record)
    db.session.commit()
    flash(f"Cleared {len(records)} experiment(s).", "success")
    return redirect(url_for("pcr.experiments"))


@pcr_bp.route("/experiments/new", methods=["GET", "POST"])
def new_experiment():
    templates = PCRTemplate.query.order_by(PCRTemplate.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Experiment name is required.", "danger")
        else:
            template = db.session.get(PCRTemplate, request.form.get("template_id")) if request.form.get("template_id") else None
            experiment = PCRExperiment(
                name=name,
                pcr_type=template.pcr_type if template else request.form.get("pcr_type", "Custom PCR"),
                target=request.form.get("target", "").strip() or None,
                sample_count=max(int(request.form.get("sample_count") or 0), 0),
                reaction_volume_ul=template.reaction_volume_ul if template and not request.form.get("reaction_volume_ul") else float(request.form.get("reaction_volume_ul") or 25),
                instrument=request.form.get("instrument", "").strip() or None,
                experiment_date=date.fromisoformat(request.form.get("experiment_date")) if request.form.get("experiment_date") else date.today(),
                notes=request.form.get("notes", "").strip() or None,
                replicate_type=request.form.get("replicate_type", "None"),
                technical_replicates=max(int(request.form.get("technical_replicates") or 1), 1),
                biological_replicates=max(int(request.form.get("biological_replicates") or 1), 1),
                template=template,
                positive_controls=max(int(request.form.get("positive_controls") or 0), 0),
                negative_controls=max(int(request.form.get("negative_controls") or 0), 0),
                ntcs=max(int(request.form.get("ntcs") or 0), 0),
                master_mix_excess_percent=0,
                extra_reactions=max(int(request.form.get("extra_reactions") or 0), 0),
            )
            if template and template.protocol_json:
                protocol_copy = experiment_from_dict(json.loads(template.protocol_json))
                experiment.reagents = protocol_copy.reagents
                experiment.programs = protocol_copy.programs
            db.session.add(experiment)
            db.session.commit()
            flash("Experiment created. Continue building the run below.", "success")
            return redirect(url_for("pcr.experiment", experiment_id=experiment.id))
    return render_template("pcr/experiment_new.html", templates=templates, today=date.today().isoformat())


@pcr_bp.get("/experiments/<int:experiment_id>")
def experiment(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    master_mix_rows = master_mix_totals(record)
    individual_reagents = [reagent for reagent in record.reagents if not reagent.include_in_master_mix]
    return render_template(
        "pcr/review.html",
        experiment=record,
        total_reactions=total_reactions(record),
        master_mix_reactions=master_mix_reactions(record),
        master_mix_rows=master_mix_rows,
        master_mix_total=sum(total for _, total in master_mix_rows),
        individual_reagents=individual_reagents,
        individual_total=sum(reagent.volume_per_reaction_ul for reagent in individual_reagents),
    )


@pcr_bp.get("/experiments/<int:experiment_id>/pdf")
def experiment_pdf(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    master_mix_rows = master_mix_totals(record)
    individual_reagents = [reagent for reagent in record.reagents if not reagent.include_in_master_mix]
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.6 * inch, leftMargin=0.6 * inch, topMargin=0.65 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    teal = colors.HexColor("#167d72")
    pale = colors.HexColor("#eef5f3")
    ink = colors.HexColor("#17252b")
    muted = colors.HexColor("#5f7075")
    body = ParagraphStyle("PdfBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12, textColor=ink)
    label = ParagraphStyle("PdfLabel", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=muted)
    header = ParagraphStyle("PdfHeader", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white)
    title = styles["Title"]
    title.fontName, title.fontSize, title.leading, title.textColor, title.alignment = "Helvetica-Bold", 24, 28, ink, 0
    subtitle = styles["Heading2"]
    subtitle.fontName, subtitle.fontSize, subtitle.leading, subtitle.textColor = "Helvetica", 12, 15, teal
    section = styles["Heading2"]
    section.fontName, section.fontSize, section.leading, section.textColor, section.spaceBefore, section.spaceAfter = "Helvetica-Bold", 13, 16, ink, 14, 6

    def cell(value, style=body):
        return Paragraph(str(value).replace("&", "&amp;"), style)

    def section_title(text):
        return [Spacer(1, 7), Paragraph(text, section)]

    def table_style(header=True, highlight_last=False):
        commands = [("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5dfdd")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
        if header:
            commands += [("BACKGROUND", (0, 0), (-1, 0), teal), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
        if highlight_last:
            commands += [("BACKGROUND", (0, -1), (-1, -1), pale), ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")]
        return TableStyle(commands)

    story = [Paragraph("Experiment Review", title), Paragraph(record.name, subtitle), Spacer(1, 12)]
    info = [[cell("PCR Type", label), cell(record.template.name if record.template else record.pcr_type)], [cell("Reaction volume", label), cell(f"{record.reaction_volume_ul:.2f} uL")], [cell("Date", label), cell(record.experiment_date.strftime("%d %b %Y"))], [cell("Notes", label), cell(record.notes or "No notes added.")]]
    story.append(Table(info, colWidths=[1.45 * inch, 5.95 * inch], style=TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5dfdd")), ("BACKGROUND", (0, 0), (0, -1), pale), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])))
    story += section_title("Reactions")
    reaction_rows = [[cell("Measure", header), cell("Count", header)], [cell("Samples"), cell(record.sample_count or len(record.samples))], [cell("Positive controls"), cell(record.positive_controls)], [cell("Negative controls"), cell(record.negative_controls)], [cell("NTCs"), cell(record.ntcs)], [cell("Total reactions"), cell(total_reactions(record))], [cell("Extra master-mix reactions"), cell(record.extra_reactions)], [cell("Master mix reactions"), cell(master_mix_reactions(record))]]
    story.append(Table(reaction_rows, colWidths=[5.5 * inch, 1.9 * inch], style=table_style(highlight_last=True)))
    story += section_title("Sample and control IDs")
    ids = [[cell("#", header), cell("Type", header), cell("ID name", header), cell("Control type / specimen", header), cell("Result", header)]]
    row_number = 1
    for control in record.controls:
        ids.append([cell(row_number), cell("Control"), cell(control.name), cell(control.control_type), cell(control.result or "")])
        row_number += 1
    for sample in record.samples:
        ids.append([cell(row_number), cell("Sample"), cell(sample.name), cell(sample.specimen_id or ""), cell(sample.result or "")])
        row_number += 1
    story.append(Table(ids, repeatRows=1, colWidths=[0.35 * inch, 0.7 * inch, 1.7 * inch, 2.0 * inch, 2.65 * inch], style=table_style()))
    story += section_title("Master mix")
    mix = [[cell("Component", header), cell("Volume / reaction", header), cell("Total required", header)]] + [[cell(reagent.name), cell(f"{reagent.volume_per_reaction_ul:.2f} uL"), cell(f"{total:.2f} uL")] for reagent, total in master_mix_rows]
    mix.append([cell("Total master mix"), cell(""), cell(f"{sum(total for _, total in master_mix_rows):.2f} uL")])
    story.append(Table(mix, repeatRows=1, colWidths=[3.8 * inch, 1.7 * inch, 2.2 * inch], style=table_style(highlight_last=True)))
    if individual_reagents:
        story += section_title("Added individually")
        individual = [[cell("Component", header), cell("Volume / reaction", header), cell("Total required", header)]] + [[cell(reagent.name), cell(f"{reagent.volume_per_reaction_ul:.2f} uL"), cell(f"{reagent.volume_per_reaction_ul * total_reactions(record):.2f} uL")] for reagent in individual_reagents]
        story.append(Table(individual, repeatRows=1, colWidths=[3.8 * inch, 1.7 * inch, 2.2 * inch], style=table_style()))
    story += section_title("PCR program")
    program = [[cell("#", header), cell("Instruction", header), cell("Details", header)]]
    for index, step in enumerate(record.programs[0].steps if record.programs else [], 1):
        if step.step_type == "goto":
            details = f"Repeat from step {step.goto_step or '?'}"
            instruction = f"GOTO {step.goto_step or '?'}, {step.repeat_count} more times"
        elif step.name == "Hold":
            instruction, details = "Hold", f"{step.temperature_c:g} C for infinity"
        else:
            instruction = step.name
            details = f"{step.temperature_c:g} C for {step.duration_seconds // 60}:{step.duration_seconds % 60:02d}"
        program.append([cell(index), cell(instruction), cell(details)])
    story.append(Table(program, repeatRows=1, colWidths=[0.35 * inch, 3.0 * inch, 4.35 * inch], style=table_style()))
    document.build(story)
    buffer.seek(0)
    safe_name = "".join(character if character.isalnum() or character in "-_" else "_" for character in record.name)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"{safe_name}_review.pdf")


@pcr_bp.get("/experiments/<int:experiment_id>/edit")
def edit_experiment(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    return render_template("pcr/experiment.html", experiment=record, total_reactions=total_reactions(record), master_mix_reactions=master_mix_reactions(record))


@pcr_bp.post("/experiments/<int:experiment_id>/save")
def save_experiment(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    record.status = "Saved"
    db.session.commit()
    flash("Experiment saved.", "success")
    return redirect(url_for("pcr.experiment", experiment_id=record.id))


@pcr_bp.route("/types/new", methods=["GET", "POST"])
def new_type():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("PCR Type name is required.", "danger")
        else:
            reagents = []
            reagent_categories = request.form.getlist("reagent_category")
            for index, reagent_name in enumerate(request.form.getlist("reagent_name")):
                if reagent_name.strip():
                    category = reagent_categories[index]
                    reagents.append({"name": reagent_name.strip(), "category": category, "include_in_master_mix": category != "Template", "volume_per_reaction_ul": float(request.form.getlist("reagent_volume")[index] or 0)})
            steps = []
            step_kinds = request.form.getlist("step_kind")
            step_hours = request.form.getlist("step_hours")
            step_minutes = request.form.getlist("step_minutes")
            step_times = request.form.getlist("step_time")
            legacy_durations = request.form.getlist("step_duration")
            step_temperatures = request.form.getlist("step_temperature")
            step_gotos = request.form.getlist("step_goto")
            step_repeats = request.form.getlist("step_repeats")
            for index, step_name in enumerate(request.form.getlist("step_name")):
                if step_name.strip():
                    kind = step_kinds[index] if index < len(step_kinds) else "step"
                    if index < len(step_times):
                        duration_seconds = _protocol_time_seconds(step_times[index])
                    else:
                        hours = float(step_hours[index] or 0) if index < len(step_hours) else 0
                        minutes = float(step_minutes[index] or 0) if index < len(step_minutes) else (float(legacy_durations[index] or 0) if index < len(legacy_durations) else 0)
                        duration_seconds = round(hours * 3600 + minutes * 60)
                    temperature = float(step_temperatures[index] or 0) if index < len(step_temperatures) else 0
                    goto_step = int(step_gotos[index] or 0) if index < len(step_gotos) else 0
                    repeats = int(step_repeats[index] or 0) if index < len(step_repeats) else 0
                    steps.append({"name": "GOTO" if kind == "goto" else step_name.strip(), "step_type": kind, "order": index + 1, "temperature_c": temperature, "duration_seconds": duration_seconds, "cycles": 1, "goto_step": goto_step or None, "repeat_count": max(repeats, 0)})
            protocol = {"experiment": {"name": name, "pcr_type": request.form.get("category", "Conventional PCR"), "reaction_volume_ul": float(request.form.get("reaction_volume_ul") or 25)}, "reagents": reagents, "program": {"name": f"{name} program", "steps": steps, "cycle_groups": []}}
            db.session.add(PCRTemplate(name=name, pcr_type=request.form.get("category", "Conventional PCR"), reaction_volume_ul=protocol["experiment"]["reaction_volume_ul"], protocol_json=json.dumps(protocol)))
            db.session.commit()
            flash("PCR Type saved.", "success")
            return redirect(url_for("pcr.templates"))
    return render_template("pcr/type_new.html")


@pcr_bp.get("/types")
def types():
    return redirect(url_for("pcr.templates"))


@pcr_bp.post("/experiments/<int:experiment_id>/general")
def update_general(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    record.name = request.form.get("name", record.name).strip() or record.name
    record.pcr_type = request.form.get("pcr_type", record.pcr_type)
    record.target = request.form.get("target", "").strip() or None
    record.assay_id = request.form.get("assay_id") or None
    record.reaction_volume_ul = float(request.form.get("reaction_volume_ul") or record.reaction_volume_ul)
    record.instrument = request.form.get("instrument", "").strip() or None
    record.experiment_date = date.fromisoformat(request.form.get("experiment_date")) if request.form.get("experiment_date") else record.experiment_date
    record.notes = request.form.get("notes", "").strip() or None
    record.replicate_type = request.form.get("replicate_type", "None")
    record.technical_replicates = max(int(request.form.get("technical_replicates") or 1), 1)
    record.biological_replicates = max(int(request.form.get("biological_replicates") or 1), 1)
    record.sample_count = max(int(request.form.get("sample_count") or record.sample_count), 0)
    record.positive_controls = max(int(request.form.get("positive_controls") or 0), 0)
    record.negative_controls = max(int(request.form.get("negative_controls") or 0), 0)
    record.ntcs = max(int(request.form.get("ntcs") or 0), 0)
    record.extra_reactions = max(int(request.form.get("extra_reactions") or 0), 0)
    db.session.commit()
    flash("Experiment information saved.", "success")
    return redirect(url_for("pcr.experiment", experiment_id=record.id))


@pcr_bp.post("/experiments/<int:experiment_id>/samples")
def add_sample(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    name = request.form.get("name", "").strip()
    if name:
        record.samples.append(Sample(name=name, replicate_count=max(int(request.form.get("replicate_count") or 1), 1), specimen_id=request.form.get("specimen_id", "").strip() or None, sample_type=request.form.get("sample_type", "").strip() or None, result=request.form.get("result", "").strip() or None, notes=request.form.get("notes", "").strip() or None))
        db.session.commit()
    return redirect(url_for("pcr.edit_experiment", experiment_id=record.id) + "#sample-id-name")


@pcr_bp.post("/experiments/<int:experiment_id>/controls")
def add_control(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    name = request.form.get("name", "").strip()
    if name:
        record.controls.append(Control(name=name, control_type=request.form.get("control_type", "Other"), replicate_count=max(int(request.form.get("replicate_count") or 1), 1), result=request.form.get("result", "").strip() or None, notes=request.form.get("notes", "").strip() or None))
        db.session.commit()
    return redirect(url_for("pcr.edit_experiment", experiment_id=record.id) + "#control-id-name")


@pcr_bp.post("/experiments/<int:experiment_id>/samples/<int:sample_id>/delete")
def delete_sample(experiment_id, sample_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    sample = next((item for item in record.samples if item.id == sample_id), None)
    if sample:
        db.session.delete(sample)
        db.session.commit()
    return redirect(url_for("pcr.edit_experiment", experiment_id=record.id) + "#sample-id-name")


@pcr_bp.post("/experiments/<int:experiment_id>/controls/<int:control_id>/delete")
def delete_control(experiment_id, control_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    control = next((item for item in record.controls if item.id == control_id), None)
    if control:
        db.session.delete(control)
        db.session.commit()
    return redirect(url_for("pcr.edit_experiment", experiment_id=record.id) + "#control-id-name")


@pcr_bp.post("/experiments/<int:experiment_id>/results/<string:record_type>/<int:record_id>")
def update_result(experiment_id, record_type, record_id):
    experiment = db.get_or_404(PCRExperiment, experiment_id)
    records = experiment.samples if record_type == "sample" else experiment.controls if record_type == "control" else None
    record = next((item for item in records if item.id == record_id), None) if records is not None else None
    if record is None:
        return redirect(url_for("pcr.experiment", experiment_id=experiment.id))
    result = request.form.get("result", "").strip()
    record.result = request.form.get("custom_result", "").strip() if result == "Other" else result
    record.result = record.result or None
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=experiment.id))


@pcr_bp.post("/experiments/<int:experiment_id>/results")
def update_results(experiment_id):
    experiment = db.get_or_404(PCRExperiment, experiment_id)
    standard_results = {"Amplification detected", "No amplification detected", "Band detected", "No band detected", "Control valid", "Control failed", "Invalid", "Inconclusive"}
    for control in experiment.controls:
        result = request.form.get(f"control_result_{control.id}", "").strip()
        control.result = request.form.get(f"control_custom_result_{control.id}", "").strip() if result == "Other" else result
        control.result = control.result or None
    for sample in experiment.samples:
        result = request.form.get(f"sample_result_{sample.id}", "").strip()
        sample.result = request.form.get(f"sample_custom_result_{sample.id}", "").strip() if result == "Other" else result
        sample.result = sample.result or None
    db.session.commit()
    flash("Sample and control results saved.", "success")
    return redirect(url_for("pcr.experiment", experiment_id=experiment.id))
@pcr_bp.post("/experiments/<int:experiment_id>/reagents")
def add_reagent(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    name = request.form.get("name", "").strip()
    if name:
        record.reagents.append(Reagent(name=name, category=request.form.get("category", "Other"), include_in_master_mix=request.form.get("include_in_master_mix", "yes") == "yes", stock_concentration=request.form.get("stock_concentration", "").strip() or None, volume_per_reaction_ul=float(request.form.get("volume_per_reaction_ul") or 0), notes=request.form.get("notes", "").strip() or None))
        db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id))


@pcr_bp.post("/experiments/<int:experiment_id>/program/steps")
def add_step(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    add_program_step(record, request.form)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.post("/experiments/<int:experiment_id>/program/steps/<int:step_id>/delete")
def delete_step(experiment_id, step_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    delete_program_step(record, step_id)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.post("/experiments/<int:experiment_id>/program/steps/<int:step_id>/move/<int:direction>")
def move_step(experiment_id, step_id, direction):
    record = db.get_or_404(PCRExperiment, experiment_id)
    move_program_step(record, step_id, -1 if direction < 0 else 1)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.post("/experiments/<int:experiment_id>/program/steps/<int:step_id>/duplicate")
def duplicate_step(experiment_id, step_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    program = record.programs[0] if record.programs else None
    source = next((item for item in program.steps if item.id == step_id), None) if program else None
    if source:
        add_program_step(record, {"name": f"{source.name} copy", "step_type": source.step_type, "temperature_c": source.temperature_c, "duration_seconds": source.duration_seconds, "cycles": source.cycles, "goto_step": source.goto_step, "repeat_count": source.repeat_count})
        db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.post("/experiments/<int:experiment_id>/program/steps/<int:step_id>")
def update_step(experiment_id, step_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    update_program_step(record, step_id, request.form)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.post("/experiments/<int:experiment_id>/program/groups")
def add_group(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    add_cycle_group(record, request.form)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=record.id) + "#program")


@pcr_bp.get("/experiments/<int:experiment_id>/save")
def save_file(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    safe_name = record.name.replace(" ", "_")
    return send_file(BytesIO(experiment_json(record).encode("utf-8")), mimetype="application/json", as_attachment=True, download_name=f"{safe_name}.pcr")


@pcr_bp.post("/experiments/<int:experiment_id>/duplicate")
def duplicate_experiment(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    copy = experiment_from_dict(json.loads(experiment_json(record)))
    copy.name = f"{record.name} copy"
    db.session.add(copy)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=copy.id))


@pcr_bp.post("/experiments/<int:experiment_id>/template")
def create_template(experiment_id):
    record = db.get_or_404(PCRExperiment, experiment_id)
    template = PCRTemplate(
        name=request.form.get("name", "").strip() or record.name,
        description=request.form.get("description", "").strip() or record.notes,
        pcr_type=record.pcr_type,
        target=record.target,
        instrument=record.instrument,
        reaction_volume_ul=record.reaction_volume_ul,
        protocol_json=experiment_json(record),
        assay_id=record.assay_id,
    )
    db.session.add(template)
    db.session.commit()
    flash("Template saved. The experiment remains unchanged.", "success")
    return redirect(url_for("pcr.templates"))


@pcr_bp.post("/templates/<int:template_id>/experiment")
def experiment_from_template(template_id):
    template = db.get_or_404(PCRTemplate, template_id)
    if template.protocol_json:
        copy = experiment_from_dict(json.loads(template.protocol_json))
    else:
        copy = PCRExperiment(name=template.name, pcr_type=template.pcr_type, target=template.target, instrument=template.instrument, reaction_volume_ul=template.reaction_volume_ul, assay_id=template.assay_id)
    copy.name = request.form.get("name", "").strip() or f"{template.name} experiment"
    copy.template = template
    db.session.add(copy)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=copy.id))


@pcr_bp.post("/open")
def open_file():
    upload = request.files.get("file")
    if not upload or not upload.filename:
        flash("Choose a .pcr file to open.", "danger")
        return redirect(url_for("pcr.experiments"))
    imported = experiment_from_dict(json.load(upload.stream))
    db.session.add(imported)
    db.session.commit()
    return redirect(url_for("pcr.experiment", experiment_id=imported.id))


@pcr_bp.get("/templates")
def templates():
    records = PCRTemplate.query.order_by(PCRTemplate.name).all()
    return render_template("pcr/template_list.html", templates=records)


@pcr_bp.post("/templates/<int:template_id>/delete")
def delete_template(template_id):
    record = db.get_or_404(PCRTemplate, template_id)
    for experiment in record.experiments:
        experiment.template = None
    db.session.delete(record)
    db.session.commit()
    flash("PCR Type deleted. Existing experiments were kept.", "success")
    return redirect(url_for("pcr.templates"))


@pcr_bp.route("/assays", methods=["GET", "POST"])
def assays():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        target = request.form.get("target", "").strip()
        if not name or not target:
            flash("Assay name and target are required.", "danger")
        else:
            db.session.add(Assay(name=name, target=target, description=request.form.get("description", "").strip() or None))
            db.session.commit()
            flash("Assay created.", "success")
            return redirect(url_for("pcr.assays"))

    records = Assay.query.order_by(Assay.name).all()
    return render_template("pcr/assay_list.html", assays=records)
