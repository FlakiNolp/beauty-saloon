from src.keyboards.gen_beauty_saloon import GenBeautySaloon
from src.keyboards.gen_service import GenService
from src.keyboards.gen_specialist import GenSpecialist
from src.keyboards.gen_datetime import GenDatetime
from src.abstract_classes.abstract_fabric_method import AbstractFabricMethod


class Creator:
    @staticmethod
    def factory(type: str) -> AbstractFabricMethod:
        if type == 'service':
            return GenService()
        elif type == 'beauty_saloon':
            return GenBeautySaloon()
        elif type == 'specialist':
            return GenSpecialist()
        elif type == 'datetime':
            return GenDatetime()
