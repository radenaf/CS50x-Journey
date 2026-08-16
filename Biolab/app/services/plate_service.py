from app import db
from app.models import Control, Plate, PlateWell, Sample


def ensure_plate(experiment):
    if experiment.plates:
        return experiment.plates[0]
    plate = Plate(name=f"{experiment.name} plate", experiment=experiment)
    for row in range(8):
        for column in range(1, 13):
            plate.wells.append(PlateWell(position=f"{chr(65 + row)}{column}"))
    db.session.add(plate)
    return plate


def assign_well(plate, position, sample_id=None, control_id=None, target=None, replicate_number=None):
    well = next((item for item in plate.wells if item.position == position), None)
    if well is None:
        raise ValueError("Unknown plate position")
    well.sample_id = int(sample_id) if sample_id else None
    well.control_id = int(control_id) if control_id else None
    well.target = target or None
    well.replicate_number = int(replicate_number) if replicate_number else None
    sample = Sample.query.get(well.sample_id) if well.sample_id else None
    control = Control.query.get(well.control_id) if well.control_id else None
    well.contents = sample.name if sample else control.name if control else None
    return well
