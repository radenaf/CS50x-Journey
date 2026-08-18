from app.models.assay import Assay
from app.models.control import Control
from app.models.experiment import PCRExperiment
from app.models.pcr_program import PCRCycleGroup, PCRProgram, PCRStep
from app.models.reagent import Reagent
from app.models.sample import Sample
from app.models.template import PCRTemplate


def register_models():
    return (
        Assay,
        PCRTemplate,
        PCRExperiment,
        Sample,
        Control,
        Reagent,
        PCRProgram,
        PCRStep,
        PCRCycleGroup,
    )
