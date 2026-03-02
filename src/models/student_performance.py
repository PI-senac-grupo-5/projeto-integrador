def parse_bool(value):
    if value == 1:
        return True
    return False  # nesse caso se o campo vier com número diferente de 1, vai retornar false


class StudentPerformance:
    def __init__(
            self,
            student_id: int,
            age: int,
            gender: str,
            academic_level: str,
            study_hours: float,
            self_study_hours: float,
            online_classes_hours: float,
            social_media_hours: float,
            gaming_hours: float,
            sleep_hours: float,
            screen_time_hours: float,
            exercise_minutes: int,
            caffeine_intake_mg: float,
            part_time_job: int,
            upcoming_deadline: int,
            internet_quality: str,
            mental_health_score: float,
            focus_index: float,
            burnout_level: float,
            productivity_score: float,
            exam_score: float
    ):
        self.student_id = student_id
        self.age = age
        self.gender = gender
        self.academic_level = academic_level
        self.study_hours = study_hours
        self.self_study_hours = self_study_hours
        self.online_classes_hours = online_classes_hours
        self.social_media_hours = social_media_hours
        self.gaming_hours = gaming_hours
        self.sleep_hours = sleep_hours
        self.screen_time_hours = screen_time_hours
        self.exercise_minutes = exercise_minutes
        self.caffeine_intake_mg = caffeine_intake_mg
        self.part_time_job = parse_bool(part_time_job)
        self.upcoming_deadline = parse_bool(upcoming_deadline)
        self.internet_quality = internet_quality
        self.mental_health_score = mental_health_score
        self.focus_index = focus_index
        self.burnout_level = burnout_level
        self.productivity_score = productivity_score
        self.exam_score = exam_score

    # podemos criar qualquer validação referente aos dados acima

    def validate(self):
        for field, value in vars(self).items():
            if isinstance(value, (int, float)):
                if value < 0:
                    # qualquer campo que seja negativo, vai retornar um erro
                    # podemos retornar um 'ValueError' genérico ou criar um exception personalizado
                    raise ValueError(f"O campo '{field}' não pode ser menor que 0")
