import codecs
import json
import os

from chesterbot.wipes import main_dir
from chesterbot.wipes.Claim import Claim


class Wipe:
    def __init__(
            self,
            claims: dict[Claim],
            server_name: str = "",
            started_at: str = "",
            stoped_at: str = "",
            path: str = "",
    ):
        self.server_name = server_name
        self.started_at = started_at
        self.stoped_at = stoped_at
        self.path = path if path != "" else f"{self.server_name}_{self.started_at}"
        self.claims = claims

    def save(self):
        cur_dir = os.path.join(main_dir, self.path)
        if not os.path.exists(cur_dir):
            os.mkdir(cur_dir)
        if not os.path.exists(os.path.join(main_dir, self.path, "claims")):
            os.mkdir(os.path.join(main_dir, self.path, "claims"))
        with codecs.open(
            f"{main_dir}/{self.path}/wipe.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {key: val for key, val in self.__dict__.items() if key not in {"claims"}},
                file,
                ensure_ascii=False
            )

    @staticmethod
    def from_dict(raw_dict):
        return Wipe(
            claims={},
            server_name=raw_dict["server_name"],
            started_at=raw_dict["started_at"],
            stoped_at=raw_dict['stoped_at'],
            path=raw_dict['path']
        )

    @staticmethod
    def load(file_name, claims_dir):
        """Загружает данные из файла с указанным именем"""
        with codecs.open(
                file_name,
                "r",
                encoding="utf-8"
        ) as file:
            raw_data = json.load(file)
            wipe = Wipe(
                server_name=raw_data['server_name'],
                started_at=raw_data['started_at'],
                stoped_at=raw_data['stoped_at'],
                path=raw_data['path'],
                claims=
                {
                    claim_name[:-5]: Claim.from_dict(
                        json.load(
                            codecs.open(full_path, "r", encoding="utf-8"),
                        )
                    )
                    for claim_name in os.listdir(claims_dir)
                    if os.path.isfile(full_path := os.path.join(claims_dir, claim_name))
                       and claim_name not in {}
                }
            )
        return wipe
