import json
from datetime import datetime
from pprint import pp
from typing import List

import requests

import dnevnik
from dnevnik.student_homework import StudentHomework


class Client:
    """
    Клиент. Нужен для выполнения различных запросов
    """
    auth_token = None
    profile_id = None

    def __init__(self, auth_token: str, profile_id: int):
        """
        Конструктор клиента:
        param auth_token: Токен авторизации:
        param profile_id: ID профиля
        """
        self.auth_token = auth_token
        self.profile_id = profile_id

    def make_request(self, method: str, raw=False, **query_options):
        """ Позволяет сделать запрос с передачей всех необходимых параметровю. Дополнительные аргументы передаются как
            kwargs, параметр raw указывает на требования возврата без обработки модулем json, method позволяет указать
            метод API """
        parameters = {
            "Auth-Token": self.auth_token,
            "Content-Type": "application/json",
            "Profile-Id": str(self.profile_id),
            "Profile-Type": "student",
            "Referer": "https://dnevnik.mos.ru/diary/diary/lessons",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.87 Safari/537.36 RuxitSynthetic/1.0 v8662719366318635631 "
                          "t6281935149377429786 ",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept": "*/*"
        }
        data = query_options
        request = requests.get("https://dnevnik.mos.ru" + method, headers=parameters, params=query_options)
        if request.status_code != 200:
            print(request.content.decode("utf-8"))
            raise Exception(f"Incorrect status_code ({request.status_code})!")
        if not raw:
            return json.loads(request.content)
        return request.content.decode("utf-8")

    @property
    def profile(self) -> dnevnik.student_profile.StudentProfile:
        """ Свойство, позволяет получить профиль пользователя """
        return dnevnik.student_profile.StudentProfile(self)

    def get_homeworks(self, begin_prepared_date: datetime = None, end_prepared_date: datetime = None) -> List[
        StudentHomework]:
        """ Свойство для получения домашних работ """
        homeworks = []
        begin_prepared_date = datetime.today() if not begin_prepared_date else begin_prepared_date
        end_prepared_date = datetime.today() if not end_prepared_date else end_prepared_date
        homeworks_raw = self.make_request("/core/api/student_homeworks",
                                          begin_prepared_date=begin_prepared_date.strftime("%d.%m.%Y"),
                                          end_prepared_date=end_prepared_date.strftime("%d.%m.%Y"))
        for homework in homeworks_raw:
            del homework["deleted_at"]
            del homework["homework_entry_id"]
            del homework["student_name"]
            homeworks.append(StudentHomework(self, **homework))
        return homeworks
