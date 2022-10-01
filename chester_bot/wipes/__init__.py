import os
from chester_bot.wipes.config import main_dir
from chester_bot.wipes.Wipe import Wipe

if not os.path.exists(main_dir):
    os.mkdir(main_dir)


wipe_list = [
    tmp_dir
    for tmp_dir in os.listdir(main_dir)
    if os.path.isdir(os.path.join(main_dir, tmp_dir))
       and tmp_dir not in {"__pycache__", "__pycache___"}
]

last_wipe = \
    Wipe(claims={}) if len(wipe_list) == 0 \
        else Wipe.load(
        os.path.join(main_dir, wipe_list[0], "wipe.json"),
        os.path.join(main_dir, wipe_list[0], "claims")
    ) if len(wipe_list) == 1 \
        else Wipe.load(
        os.path.join(
            claims_dir := max(
                [os.path.join(main_dir, dir_path) for dir_path in wipe_list],
                key=os.path.getmtime),
            "wipe.json"),
        os.path.join(claims_dir, "claims")
    )

