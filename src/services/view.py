from abc import ABC, abstractmethod
import html


class TableView(ABC):
    COLUMNS = (
        ('Дата', None),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('USD купівля', 'USD_BUY'),
        ('EUR купівля', 'EUR_BUY'),
    )

    @classmethod
    def headers(cls):
        return tuple(title for title, _key in cls.COLUMNS)

    @staticmethod
    def _cell(value):
        if value is None:
            return '—'
        if isinstance(value, float):
            return f'{value:.4f}'
        return str(value)

    def rows(self, data):
        table = []
        for row in data:
            for date, rates in row.items():
                cells = []
                for _title, key in self.COLUMNS:
                    value = date if key is None else rates[key]
                    cells.append(self._cell(value))
                table.append(tuple(cells))
        return table

    @abstractmethod
    def render(self, data) -> str:
        pass


class ConsoleTableView(TableView):
    def render(self, data) -> str:
        headers = self.headers()
        table = self.rows(data)
        widths = [len(header) for header in headers]
        for row in table:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(cell))

        def line(cells):
            return ' | '.join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

        rule = '-+-'.join('-' * width for width in widths)
        body = '\n'.join(line(row) for row in table) or '(немає курсів)'
        return f'{line(headers)}\n{rule}\n{body}'


class HtmlTableView(TableView):
    def render(self, data) -> str:
        headers = self.headers()
        head = ''.join(f'<th>{html.escape(header)}</th>' for header in headers)
        body_rows = [
            '<tr>' + ''.join(f'<td>{html.escape(cell)}</td>' for cell in row) + '</tr>'
            for row in self.rows(data)
        ]
        body = ''.join(body_rows) or f'<tr><td colspan="{len(headers)}">немає курсів</td></tr>'
        return f'<table class="rates"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
