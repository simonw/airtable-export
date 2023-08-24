import click

class ClickLogger:
    def __init__(self):
        self.click = click

    def log(self, records, filenames):
        filenames_seperated_by_comma = ", ".join(filenames)
        number_of_records = len(records)
        human_friendly_records = "record" if number_of_records == 1 else "records"
        log_message = f"Wrote {number_of_records} {human_friendly_records} to {filenames_seperated_by_comma}"
        self.click.echo(log_message, err=True)


