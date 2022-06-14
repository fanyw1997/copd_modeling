class TimeConvert:
    def __init__(self, start_real_year: int, start_real_month: int):
        assert 1 <= start_real_month <= 12
        self._start_real_year = start_real_year
        self._start_real_month = start_real_month

    def get_real_year_month(self, month: int) -> tuple:
        assert month >= 0
        year = month // 12
        month = month % 12
        year = self._start_real_year + year
        month = self._start_real_month + month
        if month > 12:
            month -= 12
            year += 1

        return year, month

    def get_cycle_month(self, real_year: int, real_month: int) -> int:
        assert 1 <= real_month <= 12
        assert real_year > self._start_real_year or \
               real_year == self._start_real_year and real_month >= self._start_real_month

        month = (real_year - self._start_real_year) * 12 + (real_month - self._start_real_month)

        return month
