DATA_FOLDER = "db_data"


def import_csv(filename: str):
    with open(f"./{DATA_FOLDER}/{filename}", "r+") as f1:
        x = []
        for line in f1:
            if not line.strip().startswith("#"):
                stringified = ", ".join(
                    list(map(lambda x: f"'{x}'", line.split(",")))
                )
                x.append(f"({stringified})")
        print("Import CSV successful.")
        return ",".join(x)
