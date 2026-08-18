from app import db
from app.models import PCRExperiment, PCRTemplate


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Your workbench" in response.data
    assert b"PCR Results" in response.data


def test_create_experiment(client, app):
    response = client.post("/pcr/experiments", data={"name": "Pilot run", "notes": "Initial setup"})
    assert response.status_code == 302
    with app.app_context():
        experiment = db.session.scalar(db.select(PCRExperiment))
        assert experiment.name == "Pilot run"
        assert experiment.status == "Draft"


def test_assay_requires_name_and_target(client):
    response = client.post("/pcr/assays", data={"name": "", "target": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Assay name and target are required" in response.data


def test_complete_experiment_can_be_built_saved_and_duplicated(client, app):
    response = client.post(
        "/pcr/experiments/new",
        data={
            "name": "Rickettsia r17 qPCR",
            "pcr_type": "qPCR",
            "target": "r17",
            "reaction_volume_ul": "20",
            "instrument": "CFX96",
            "experiment_date": "2026-08-15",
            "replicate_type": "Technical",
            "technical_replicates": "3",
        },
    )
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "0093"})
    client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC", "control_type": "No-template control"})
    client.post(f"/pcr/experiments/{experiment_id}/reagents", data={"name": "Master Mix", "volume_per_reaction_ul": "10"})
    client.post(f"/pcr/experiments/{experiment_id}/program/steps", data={"name": "Initial denaturation", "temperature_c": "95", "duration_seconds": "180", "cycles": "1"})

    detail = client.get(f"/pcr/experiments/{experiment_id}")
    assert detail.status_code == 200
    assert b"Rickettsia r17 qPCR" in detail.data
    assert b"Initial denaturation" in detail.data
    assert b"6" in detail.data

    saved = client.get(f"/pcr/experiments/{experiment_id}/save")
    assert saved.status_code == 200
    assert saved.headers["Content-Disposition"].endswith("Rickettsia_r17_qPCR.pcr")

    duplicate = client.post(f"/pcr/experiments/{experiment_id}/duplicate")
    assert duplicate.status_code == 302
    with app.app_context():
        assert db.session.query(PCRExperiment).count() == 2


def test_program_edit_cycle_group_and_file_import_preserve_protocol(client, app):
    response = client.post("/pcr/experiments/new", data={"name": "Round 1", "pcr_type": "Nested PCR"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/program/steps", data={"name": "Denature", "temperature_c": "95", "duration_seconds": "20", "cycles": "1"})
    with app.app_context():
        experiment = db.get_or_404(PCRExperiment, experiment_id)
        step_id = experiment.programs[0].steps[0].id
    client.post(f"/pcr/experiments/{experiment_id}/program/steps/{step_id}", data={"name": "Initial denaturation", "temperature_c": "94", "duration_seconds": "30", "cycles": "1"})
    client.post(f"/pcr/experiments/{experiment_id}/program/groups", data={"name": "Amplification", "cycles": "40"})
    saved = client.get(f"/pcr/experiments/{experiment_id}/save")
    imported = client.post("/pcr/open", data={"file": (saved, "round_1.pcr")}, content_type="multipart/form-data")
    assert imported.status_code == 302
    with app.app_context():
        records = db.session.query(PCRExperiment).order_by(PCRExperiment.id).all()
        loaded = records[-1]
        assert loaded.programs[0].steps[0].name == "Initial denaturation"
        assert loaded.programs[0].cycle_groups[0].cycles == 40


def test_delete_experiment_removes_related_setup(client, app):
    response = client.post("/pcr/experiments", data={"name": "Delete me"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "Sample 1"})
    client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC", "control_type": "No-template control"})
    client.get(f"/pcr/experiments/{experiment_id}/edit")

    response = client.post(f"/pcr/experiments/{experiment_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(PCRExperiment, experiment_id) is None


def test_pcr_type_supports_goto_protocol_instruction(client, app):
    response = client.post(
        "/pcr/types/new",
        data={
            "name": "qPCR with plate read",
            "category": "qPCR",
            "reaction_volume_ul": "25",
            "reagent_name": ["Mastermix"],
            "reagent_category": ["Mastermix"],
            "reagent_volume": ["6.25"],
            "step_kind": ["step", "step", "goto"],
            "step_name": ["Denaturation", "Annealing", "GOTO"],
            "step_temperature": ["95", "60", "0"],
            "step_duration": ["0.08", "0.50", "0"],
            "step_cycles": ["1", "1", "1"],
            "step_goto": ["", "", "2"],
            "step_repeats": ["", "", "39"],
        },
    )

    assert response.status_code == 302
    with app.app_context():
        protocol = db.session.query(PCRTemplate).one().protocol_json
        assert '"step_type": "goto"' in protocol
        assert '"goto_step": 2' in protocol
        assert '"repeat_count": 39' in protocol


def test_experiment_uses_explicit_extra_reactions(client, app):
    response = client.post("/pcr/experiments", data={"name": "Extra reaction run"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/general", data={"name": "Extra reaction run", "sample_count": "10", "extra_reactions": "3"})

    review = client.get(f"/pcr/experiments/{experiment_id}")

    assert review.status_code == 200
    assert b"Extra master-mix reactions" in review.data
    assert b">13<" in review.data


def test_add_sample_and_control_ids(client, app):
    response = client.post("/pcr/experiments", data={"name": "ID entry run"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])

    sample_response = client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "Sample-001"})
    control_response = client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC-001", "control_type": "No-template control"})

    assert sample_response.status_code == 302
    assert control_response.status_code == 302
    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        assert experiment.samples[0].name == "Sample-001"
        assert experiment.samples[0].replicate_count == 1
        assert experiment.controls[0].name == "NTC-001"
        assert experiment.controls[0].replicate_count == 1
        assert experiment.samples[0].experiment_id == experiment_id
        assert experiment.controls[0].experiment_id == experiment_id


def test_delete_sample_and_control_ids(client, app):
    response = client.post("/pcr/experiments", data={"name": "Remove IDs"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "Sample-001"})
    client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC-001", "control_type": "No-template control"})

    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        sample_id = experiment.samples[0].id
        control_id = experiment.controls[0].id

    sample_response = client.post(f"/pcr/experiments/{experiment_id}/samples/{sample_id}/delete")
    control_response = client.post(f"/pcr/experiments/{experiment_id}/controls/{control_id}/delete")

    assert sample_response.status_code == 302
    assert sample_response.headers["Location"].endswith("#sample-id-name")
    assert control_response.status_code == 302
    assert control_response.headers["Location"].endswith("#control-id-name")
    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        assert not experiment.samples
        assert not experiment.controls


def test_sample_and_control_results_can_be_updated(client, app):
    response = client.post("/pcr/experiments", data={"name": "Result run"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "Sample-001"})
    client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC-001", "control_type": "No-template control"})
    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        sample_id = experiment.samples[0].id
        control_id = experiment.controls[0].id

    client.post(f"/pcr/experiments/{experiment_id}/results/sample/{sample_id}", data={"result": "Amplification detected"})
    client.post(f"/pcr/experiments/{experiment_id}/results/control/{control_id}", data={"result": "Control valid"})

    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        assert experiment.samples[0].result == "Amplification detected"
        assert experiment.controls[0].result == "Control valid"


def test_all_sample_and_control_results_save_together(client, app):
    response = client.post("/pcr/experiments", data={"name": "Bulk result run"})
    experiment_id = int(response.headers["Location"].rsplit("/", 1)[-1])
    client.post(f"/pcr/experiments/{experiment_id}/samples", data={"name": "Sample-001"})
    client.post(f"/pcr/experiments/{experiment_id}/controls", data={"name": "NTC-001", "control_type": "No-template control"})
    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        sample_id = experiment.samples[0].id
        control_id = experiment.controls[0].id

    response = client.post(f"/pcr/experiments/{experiment_id}/results", data={f"sample_result_{sample_id}": "Amplification detected", f"control_result_{control_id}": "Other", f"control_custom_result_{control_id}": "Control response acceptable"})

    assert response.status_code == 302
    with app.app_context():
        experiment = db.session.get(PCRExperiment, experiment_id)
        assert experiment.samples[0].result == "Amplification detected"
        assert experiment.controls[0].result == "Control response acceptable"
